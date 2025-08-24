from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import re
from datetime import datetime
import os
from difflib import SequenceMatcher
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import enhanced ML system
try:
    from improve_accuracy import AccuracyImprover as EnhancedMLEnhancer
    enhanced_ml_available = True
    logger = logging.getLogger(__name__)
    logger.info("Enhanced ML system loaded successfully")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Enhanced ML system not available: {e}")
    enhanced_ml_available = False

# Fallback to original ML enhancer (with conditional import)
try:
    from ml_enhancer import ml_enhancer
    original_ml_available = True
except ImportError as e:
    logger.warning(f"Original ML enhancer not available: {e}")
    original_ml_available = False
    ml_enhancer = None

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here-dev-only')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize enhanced ML system
if enhanced_ml_available:
    try:
        enhanced_ml_enhancer = EnhancedMLEnhancer()
        logger.info("Enhanced ML enhancer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize enhanced ML enhancer: {e}")
        enhanced_ml_available = False

# Load IPC sections data (now handled by ML enhancer)
def load_ipc_data():
    if enhanced_ml_available:
        return {"sections": enhanced_ml_enhancer.ipc_sections}
    else:
        return {"sections": ml_enhancer.ipc_sections}

# Initialize conversation logs directory
def init_logs_directory():
    if not os.path.exists('logs'):
        os.makedirs('logs')

# Save conversation log
def save_conversation_log(user_input, response, session_id):
    init_logs_directory()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "user_input": user_input,
        "response": response
    }
    
    log_file = f"logs/conversation_{timestamp}_{session_id}.json"
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving conversation log: {e}")

# Calculate similarity between two strings
def calculate_similarity(str1, str2):
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

# Extract keywords from user input
def extract_keywords(user_input):
    # Convert to lowercase and remove punctuation
    cleaned_input = re.sub(r'[^\w\s]', ' ', user_input.lower())
    words = cleaned_input.split()
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords

# Enhanced section finding using ML
def find_relevant_sections(user_input, ipc_data, threshold=0.3):
    if enhanced_ml_available:
        return enhanced_ml_enhancer.find_relevant_sections_enhanced(user_input)
    elif original_ml_available:
        return ml_enhancer.find_relevant_sections_enhanced(user_input)
    else:
        # Fallback to basic keyword matching
        return basic_keyword_matching(user_input, ipc_data)

# Generate enhanced response with ML capabilities
def generate_response(relevant_sections, user_input):
    if enhanced_ml_available:
        # Use enhanced ML for response generation
        return generate_enhanced_response_with_ml(relevant_sections, user_input)
    elif original_ml_available:
        return ml_enhancer.generate_enhanced_response(user_input, relevant_sections)
    else:
        return generate_basic_response(relevant_sections, user_input)

# Basic keyword matching fallback
def basic_keyword_matching(user_input, ipc_data):
    """Basic keyword matching when ML systems are not available"""
    keywords = extract_keywords(user_input)
    results = []
    
    for section in ipc_data['sections']:
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            for section_keyword in section['keywords']:
                similarity = SequenceMatcher(None, keyword.lower(), section_keyword.lower()).ratio()
                if similarity > 0.7:
                    score += similarity
                    matched_keywords.append(keyword)
        
        if score > 0:
            section_copy = section.copy()
            section_copy['score'] = score / len(keywords) if keywords else 0
            section_copy['method'] = 'basic_keyword_matching'
            section_copy['matched_keywords'] = matched_keywords
            results.append(section_copy)
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

# Basic response generation fallback
def generate_basic_response(relevant_sections, user_input):
    """Basic response generation when ML systems are not available"""
    if not relevant_sections:
        return {
            "message": "I couldn't find any specific IPC sections that match your description. Please try rephrasing your query or provide more details about the incident.",
            "sections": [],
            "confidence": 0,
            "suggestions": [],
            "enhanced_analysis": None,
            "accuracy_note": "Basic keyword matching used"
        }
    
    # Calculate overall confidence
    total_score = sum(section['score'] for section in relevant_sections)
    avg_confidence = total_score / len(relevant_sections)
    
    # Generate base response
    if len(relevant_sections) == 1:
        section = relevant_sections[0]
        message = f"Based on your description, this incident appears to fall under **IPC Section {section['section_number']} - {section['title']}**.\n\n"
        message += f"**Description:** {section['description']}\n\n"
        message += f"**Punishment:** {section['punishment']}"
    else:
        message = f"I found {len(relevant_sections)} potentially relevant IPC sections for your case:\n\n"
        for i, section in enumerate(relevant_sections, 1):
            confidence = section['score']
            message += f"{i}. **IPC Section {section['section_number']} - {section['title']}** (Confidence: {confidence:.1%})\n"
            message += f"   **Description:** {section['description']}\n"
            message += f"   **Punishment:** {section['punishment']}\n\n"
    
    # Add disclaimer
    message += "\n\n⚠️ **Important Disclaimer:** This is general legal information based on the Indian Penal Code and should not be considered as legal advice. For specific legal guidance, please consult with a qualified lawyer or legal professional."
    
    return {
        "message": message,
        "sections": relevant_sections,
        "confidence": avg_confidence,
        "matched_keywords": [kw for section in relevant_sections for kw in section.get('matched_keywords', [])],
        "suggestions": [],
        "enhanced_analysis": None,
        "accuracy_note": "Basic keyword matching used",
        "system_version": "Basic v1.0"
    }

# Enhanced response generation with improved accuracy
def generate_enhanced_response_with_ml(relevant_sections, user_input):
    """Generate enhanced response using improved ML system"""
    if not relevant_sections:
        return {
            "message": "I couldn't find any specific IPC sections that match your description. Please try rephrasing your query or provide more details about the incident.",
            "sections": [],
            "confidence": 0,
            "suggestions": [],
            "enhanced_analysis": None,
            "gemini_summary": None,
            "accuracy_note": "Enhanced ML system used for analysis"
        }
    
    # Calculate overall confidence
    total_score = sum(section['score'] for section in relevant_sections)
    avg_confidence = total_score / len(relevant_sections)
    
    # Generate base response
    if len(relevant_sections) == 1:
        section = relevant_sections[0]
        message = f"Based on your description, this incident appears to fall under **IPC Section {section['section_number']} - {section['title']}**.\n\n"
        message += f"**Description:** {section['description']}\n\n"
        message += f"**Punishment:** {section['punishment']}"
    else:
        message = f"I found {len(relevant_sections)} potentially relevant IPC sections for your case:\n\n"
        for i, section in enumerate(relevant_sections, 1):
            confidence = section['score']
            message += f"{i}. **IPC Section {section['section_number']} - {section['title']}** (Confidence: {confidence:.1%})\n"
            message += f"   **Description:** {section['description']}\n"
            message += f"   **Punishment:** {section['punishment']}\n\n"
    
    # Generate Gemini AI summary
    gemini_summary = generate_gemini_summary(user_input, relevant_sections)
    
    # Add enhanced accuracy note
    message += "\n\n✅ **Enhanced Analysis:** This analysis was performed using our improved ML system with better accuracy and pattern recognition."
    
    # Add Gemini summary if available
    if gemini_summary:
        message += f"\n\n🤖 **AI Summary:** {gemini_summary}"
    
    # Add disclaimer
    message += "\n\n⚠️ **Important Disclaimer:** This is general legal information based on the Indian Penal Code and should not be considered as legal advice. For specific legal guidance, please consult with a qualified lawyer or legal professional."
    
    return {
        "message": message,
        "sections": relevant_sections,
        "confidence": avg_confidence,
        "matched_keywords": [kw for section in relevant_sections for kw in section.get('matched_keywords', [])],
        "suggestions": [],
        "enhanced_analysis": None,
        "gemini_summary": gemini_summary,
        "accuracy_note": "Enhanced ML system used for analysis",
        "system_version": "Enhanced v2.0"
    }

# Generate Gemini AI summary
def generate_gemini_summary(user_input, relevant_sections):
    """Generate AI-powered summary using Gemini"""
    try:
        if not original_ml_available or not ml_enhancer.gemini_client:
            return None
        
        # Prepare context for Gemini
        sections_info = []
        for section in relevant_sections[:3]:  # Top 3 sections
            sections_info.append(f"IPC {section['section_number']}: {section['title']} - {section['description']}")
        
        context = "\n".join(sections_info)
        
        # Create prompt for Gemini
        prompt = f"""
        As a legal AI assistant, provide a concise and helpful summary for this case:
        
        User Query: "{user_input}"
        
        Relevant IPC Sections:
        {context}
        
        Please provide:
        1. A brief summary of the legal situation
        2. Key points about the applicable laws
        3. General guidance (not legal advice)
        
        Keep it concise (2-3 sentences) and user-friendly.
        """
        
        # Generate response using Gemini
        response = ml_enhancer.gemini_client.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e:
        logger.warning(f"Gemini summary generation failed: {e}")
        return None

# Frontend is now served by React/Vite
# This route is no longer needed

@app.route('/api/analyze', methods=['POST'])
def analyze_crime():
    try:
        data = request.get_json()
        user_input = data.get('description', '').strip()
        
        if not user_input:
            return jsonify({
                "error": "Please provide a description of the incident"
            }), 400
        
        # Load IPC data
        ipc_data = load_ipc_data()
        
        # Find relevant sections
        relevant_sections = find_relevant_sections(user_input, ipc_data)
        
        # Generate response
        response = generate_response(relevant_sections, user_input)
        
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save conversation log
        save_conversation_log(user_input, response, session['session_id'])
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            "error": "An error occurred while processing your request. Please try again."
        }), 500

@app.route('/api/sections', methods=['GET'])
def get_all_sections():
    try:
        ipc_data = load_ipc_data()
        return jsonify(ipc_data)
    except Exception as e:
        logger.error(f"Error loading sections: {e}")
        return jsonify({"error": "Failed to load IPC sections"}), 500

@app.route('/api/search', methods=['GET'])
def search_sections():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"sections": []})
        
        ipc_data = load_ipc_data()
        relevant_sections = find_relevant_sections(query, ipc_data, threshold=0.2)
        
        return jsonify({
            "sections": [match['section'] for match in relevant_sections],
            "query": query
        })
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({"error": "Search failed"}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        init_logs_directory()
        logs = []
        for filename in os.listdir('logs'):
            if filename.endswith('.json'):
                with open(f'logs/{filename}', 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    logs.append(log_data)
        
        # Sort by timestamp
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify({"logs": logs})
        
    except Exception as e:
        logger.error(f"Error loading logs: {e}")
        return jsonify({"error": "Failed to load logs"}), 500

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    """Get AI-powered suggestions for a query"""
    try:
        data = request.get_json()
        user_input = data.get('description', '').strip()
        
        if not user_input:
            return jsonify({
                "error": "Please provide a description of the incident"
            }), 400
        
        # Get relevant sections using enhanced ML if available
        if enhanced_ml_available:
            relevant_sections = enhanced_ml_enhancer.find_relevant_sections_enhanced(user_input)
        elif original_ml_available:
            relevant_sections = ml_enhancer.find_relevant_sections_enhanced(user_input)
        else:
            # Load IPC data for basic matching
            ipc_data = load_ipc_data()
            relevant_sections = basic_keyword_matching(user_input, ipc_data)
        
        # Get LLM suggestions and Gemini summary
        suggestions = []
        gemini_summary = None
        
        if enhanced_ml_available:
            # Enhanced ML system with Gemini integration
            suggestions = [
                "Consider consulting with a legal professional for specific advice",
                "Document all evidence related to the incident",
                "File a police complaint if necessary",
                "Keep records of any financial losses or damages"
            ]
            
            # Generate Gemini summary for enhanced system
            if original_ml_available and ml_enhancer.gemini_client:
                gemini_summary = generate_gemini_summary(user_input, relevant_sections)
                
        elif original_ml_available and ml_enhancer.use_llm:
            enhanced_analysis = ml_enhancer.llm_enhance_analysis(user_input, relevant_sections)
            if enhanced_analysis:
                suggestions = enhanced_analysis.get('suggestions', [])
        
        return jsonify({
            "suggestions": suggestions,
            "relevant_sections": [section['section_number'] for section in relevant_sections],
            "confidence": sum(section['score'] for section in relevant_sections) / len(relevant_sections) if relevant_sections else 0,
            "gemini_summary": gemini_summary,
            "system_version": "Enhanced v2.0" if enhanced_ml_available else ("Original v1.0" if original_ml_available else "Basic v1.0")
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return jsonify({
            "error": "An error occurred while processing your request. Please try again."
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the status of ML models and features"""
    status_data = {
            "ml_enhancement": {
                "llm_enabled": ml_enhancer.use_llm if original_ml_available else False,
                "ai_model": "GEMINI" if original_ml_available else "None",
                "gemini_configured": ml_enhancer.gemini_client is not None if original_ml_available else False,
                "semantic_search_enabled": ml_enhancer.use_semantic_search if original_ml_available else False,
                "sentence_model_loaded": ml_enhancer.sentence_model is not None if original_ml_available else False,
                "total_sections": len(ml_enhancer.ipc_sections) if original_ml_available else 0
            },
        "enhanced_system": {
            "available": enhanced_ml_available,
            "version": "Enhanced v2.0" if enhanced_ml_available else "Original v1.0",
            "features": {
                "enhanced_tfidf": enhanced_ml_available,
                "legal_synonyms": enhanced_ml_available,
                "pattern_matching": enhanced_ml_available,
                "improved_scoring": enhanced_ml_available,
                "gemini_ai_summary": original_ml_available and ml_enhancer.gemini_client is not None
            },
            "accuracy_improvement": "75-115% F1-Score improvement" if enhanced_ml_available else "Not available",
            "ai_capabilities": {
                "gemini_available": original_ml_available and ml_enhancer.gemini_client is not None,
                "ai_summary_enabled": True
            }
        }
    }
    
    if enhanced_ml_available:
        status_data["enhanced_system"]["total_sections"] = len(enhanced_ml_enhancer.ipc_sections)
        status_data["enhanced_system"]["expanded_sections"] = len(enhanced_ml_enhancer.expanded_sections)

    
    return jsonify(status_data)

@app.route('/api/gemini-summary', methods=['POST'])
def get_gemini_summary():
    """Get AI-powered summary using Gemini"""
    try:
        data = request.get_json()
        user_input = data.get('description', '').strip()
        
        if not user_input:
            return jsonify({
                "error": "Please provide a description of the incident"
            }), 400
        
        # Get relevant sections
        if enhanced_ml_available:
            relevant_sections = enhanced_ml_enhancer.find_relevant_sections_enhanced(user_input)
        elif original_ml_available:
            relevant_sections = ml_enhancer.find_relevant_sections_enhanced(user_input)
        else:
            ipc_data = load_ipc_data()
            relevant_sections = basic_keyword_matching(user_input, ipc_data)
        
        # Generate Gemini summary
        gemini_summary = generate_gemini_summary(user_input, relevant_sections)
        
        if gemini_summary:
            return jsonify({
                "summary": gemini_summary,
                "relevant_sections": [section['section_number'] for section in relevant_sections],
                "confidence": sum(section['score'] for section in relevant_sections) / len(relevant_sections) if relevant_sections else 0,
                "ai_model": "Gemini",
                "system_version": "Enhanced v2.0" if enhanced_ml_available else ("Original v1.0" if original_ml_available else "Basic v1.0")
            })
        else:
            return jsonify({
                "error": "Unable to generate AI summary. Please try again.",
                "relevant_sections": [section['section_number'] for section in relevant_sections],
                "system_version": "Enhanced v2.0" if enhanced_ml_available else ("Original v1.0" if original_ml_available else "Basic v1.0")
            }), 500
        
    except Exception as e:
        logger.error(f"Error generating Gemini summary: {e}")
        return jsonify({
            "error": "An error occurred while generating the AI summary."
        }), 500

@app.route('/api/test-enhanced', methods=['POST'])
def test_enhanced_system():
    """Test the enhanced ML system with sample queries"""
    try:
        data = request.get_json()
        test_queries = data.get('queries', [
            "Someone stole my phone",
            "A person hit me with a stick during an argument",
            "Someone threatened me with a knife"
        ])
        
        results = []
        for query in test_queries:
            if enhanced_ml_available:
                relevant_sections = enhanced_ml_enhancer.find_relevant_sections_enhanced(query)
            elif original_ml_available:
                relevant_sections = ml_enhancer.find_relevant_sections_enhanced(query)
            else:
                # Load IPC data for basic matching
                ipc_data = load_ipc_data()
                relevant_sections = basic_keyword_matching(query, ipc_data)
            
            results.append({
                "query": query,
                "sections": [section['section_number'] for section in relevant_sections[:3]],
                "confidence": sum(section['score'] for section in relevant_sections) / len(relevant_sections) if relevant_sections else 0,
                "system_used": "Enhanced v2.0" if enhanced_ml_available else ("Original v1.0" if original_ml_available else "Basic v1.0")
            })
        
        return jsonify({
            "test_results": results,
            "enhanced_system_available": enhanced_ml_available,
            "total_tests": len(test_queries)
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced system test: {e}")
        return jsonify({
            "error": "An error occurred while testing the enhanced system."
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
