import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
# from sentence_transformers import SentenceTransformer  # Temporarily disabled due to NumPy compatibility
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import re
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLEnhancer:
    def __init__(self):
        """Initialize ML models and configurations"""
        self.use_llm = os.getenv('USE_LLM_ENHANCEMENT', 'true').lower() == 'true'
        self.use_semantic_search = os.getenv('USE_SEMANTIC_SEARCH', 'true').lower() == 'true'
        self.similarity_threshold = float(os.getenv('SIMILARITY_THRESHOLD', '0.3'))
        
        # Initialize Gemini client
        self.gemini_client = None
        
        if self.use_llm and os.getenv('GEMINI_API_KEY'):
            try:
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                self.gemini_client = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'))
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self.use_llm = False
        else:
            logger.warning("No Gemini API key configured")
            self.use_llm = False
        
        # Initialize sentence transformer model (temporarily disabled)
        self.sentence_model = None
        # if self.use_semantic_search:
        #     try:
        #         self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        #         logger.info("Sentence transformer model loaded successfully")
        #     except Exception as e:
        #         logger.warning(f"Failed to load sentence transformer: {e}")
        #         self.use_semantic_search = False
        
        # Initialize TF-IDF vectorizer as fallback
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Load IPC sections
        self.ipc_sections = self.load_ipc_sections()
        self.section_embeddings = None
        self.tfidf_matrix = None
        
        # Pre-compute embeddings if semantic search is enabled
        if self.use_semantic_search and self.sentence_model:
            self.precompute_embeddings()
    
    def load_ipc_sections(self) -> List[Dict]:
        """Load IPC sections from JSON file"""
        try:
            with open('data/ipc_sections.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sections', [])
        except Exception as e:
            logger.error(f"Failed to load IPC sections: {e}")
            return []
    
    def precompute_embeddings(self):
        """Pre-compute embeddings for all IPC sections"""
        try:
            # Create combined text for each section
            section_texts = []
            for section in self.ipc_sections:
                text = f"{section['title']} {section['description']} {' '.join(section['keywords'])}"
                section_texts.append(text)
            
            # Compute TF-IDF matrix (sentence embeddings temporarily disabled)
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(section_texts)
            
            logger.info(f"Pre-computed TF-IDF embeddings for {len(self.ipc_sections)} sections")
        except Exception as e:
            logger.error(f"Failed to precompute embeddings: {e}")
    
    def extract_keywords_advanced(self, text: str) -> List[str]:
        """Advanced keyword extraction using multiple techniques"""
        # Convert to lowercase and clean
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Remove stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add bigrams for better context
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram.split()) == 2 and all(len(word) > 2 for word in bigram.split()):
                bigrams.append(bigram)
        
        return keywords + bigrams
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Perform semantic search using sentence transformers (temporarily disabled)"""
        # Temporarily disabled due to NumPy compatibility issues
        return []
    
    def tfidf_search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Perform TF-IDF based search as fallback"""
        try:
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > self.similarity_threshold]
            return results
        except Exception as e:
            logger.error(f"TF-IDF search failed: {e}")
            return []
    
    def llm_enhance_analysis(self, query: str, relevant_sections: List[Dict]) -> Dict:
        """Use Gemini to enhance the analysis and provide suggestions"""
        if not self.gemini_client:
            return {}
        
        try:
            # Prepare context for LLM
            sections_context = ""
            for i, section in enumerate(relevant_sections[:3], 1):
                sections_context += f"{i}. IPC Section {section['section_number']} - {section['title']}\n"
                sections_context += f"   Description: {section['description']}\n"
                sections_context += f"   Punishment: {section['punishment']}\n\n"
            
            prompt = f"""
You are an expert legal AI assistant specializing in Indian Penal Code (IPC) analysis. 

User Query: "{query}"

Relevant IPC Sections:
{sections_context}

Please provide:
1. A detailed analysis of which IPC sections apply to this case
2. Additional relevant sections that might apply
3. Legal suggestions and recommendations
4. Important considerations the user should be aware of
5. Suggested next steps

Format your response as JSON with the following structure:
{{
    "analysis": "Detailed legal analysis",
    "additional_sections": ["section1", "section2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "considerations": ["consideration1", "consideration2"],
    "next_steps": ["step1", "step2"]
}}

Keep the response concise but comprehensive.
"""
            
            # Use Gemini for analysis
            response = self.gemini_client.generate_content(
                f"You are a legal expert specializing in Indian Penal Code analysis.\n\n{prompt}"
            )
            content = response.text
            
            # Parse JSON response
            try:
                llm_response = json.loads(content)
                return llm_response
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                return {"analysis": content}
                
        except Exception as e:
            logger.error(f"Gemini enhancement failed: {e}")
            return {}
    
    def find_relevant_sections_enhanced(self, user_input: str) -> List[Dict]:
        """Enhanced section finding using multiple ML techniques"""
        results = []
        
        # Extract keywords
        keywords = self.extract_keywords_advanced(user_input)
        
        # Method 1: Semantic Search
        if self.use_semantic_search:
            semantic_results = self.semantic_search(user_input)
            for idx, score in semantic_results:
                section = self.ipc_sections[idx].copy()
                section['score'] = score
                section['method'] = 'semantic_search'
                section['matched_keywords'] = [kw for kw in keywords if any(
                    SequenceMatcher(None, kw.lower(), sk.lower()).ratio() > 0.7 
                    for sk in section['keywords']
                )]
                results.append(section)
        
        # Method 2: TF-IDF Search (if semantic search failed or as backup)
        if not results and self.tfidf_matrix is not None:
            tfidf_results = self.tfidf_search(user_input)
            for idx, score in tfidf_results:
                section = self.ipc_sections[idx].copy()
                section['score'] = score
                section['method'] = 'tfidf_search'
                section['matched_keywords'] = [kw for kw in keywords if any(
                    SequenceMatcher(None, kw.lower(), sk.lower()).ratio() > 0.7 
                    for sk in section['keywords']
                )]
                results.append(section)
        
        # Method 3: Traditional keyword matching (fallback)
        if not results:
            for section in self.ipc_sections:
                score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    for section_keyword in section['keywords']:
                        similarity = SequenceMatcher(None, keyword.lower(), section_keyword.lower()).ratio()
                        if similarity > 0.7:
                            score += similarity * 2
                            matched_keywords.append(keyword)
                        elif similarity > 0.5:
                            score += similarity
                
                if score > 0:
                    section_copy = section.copy()
                    section_copy['score'] = score / len(keywords) if keywords else 0
                    section_copy['method'] = 'keyword_matching'
                    section_copy['matched_keywords'] = matched_keywords
                    results.append(section_copy)
        
        # Sort by score and remove duplicates
        seen_sections = set()
        unique_results = []
        for result in sorted(results, key=lambda x: x['score'], reverse=True):
            if result['section_number'] not in seen_sections:
                seen_sections.add(result['section_number'])
                unique_results.append(result)
        
        return unique_results[:5]
    
    def generate_enhanced_response(self, user_input: str, relevant_sections: List[Dict]) -> Dict:
        """Generate enhanced response with LLM suggestions"""
        if not relevant_sections:
            return {
                "message": "I couldn't find any specific IPC sections that match your description. Please try rephrasing your query or provide more details about the incident.",
                "sections": [],
                "confidence": 0,
                "suggestions": [],
                "enhanced_analysis": None
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
        
        # Get LLM enhancement if available
        enhanced_analysis = None
        suggestions = []
        if self.use_llm:
            logger.info("Attempting LLM enhancement...")
            enhanced_analysis = self.llm_enhance_analysis(user_input, relevant_sections)
            logger.info(f"LLM enhancement result: {enhanced_analysis}")
            if enhanced_analysis:
                suggestions = enhanced_analysis.get('suggestions', [])
                
                # Format AI analysis nicely
                if enhanced_analysis.get('analysis'):
                    analysis_text = enhanced_analysis['analysis']
                    
                    # Remove JSON code blocks if present
                    if analysis_text.startswith('```json'):
                        # Find the end of the JSON block
                        end_marker = analysis_text.find('```', 7)
                        if end_marker != -1:
                            analysis_text = analysis_text[7:end_marker].strip()
                        else:
                            # If no end marker found, remove just the start
                            analysis_text = analysis_text[7:].strip()
                    elif analysis_text.startswith('```') and analysis_text.endswith('```'):
                        analysis_text = analysis_text[3:-3].strip()
                    
                    # Try to parse JSON and format it nicely
                    try:
                        import json
                        analysis_data = json.loads(analysis_text)
                        
                        # Format the analysis nicely
                        formatted_analysis = f"\n\n🤖 **AI Analysis:**\n\n"
                        
                        if analysis_data.get('analysis'):
                            formatted_analysis += f"**Legal Analysis:** {analysis_data['analysis']}\n\n"
                        
                        if analysis_data.get('additional_sections'):
                            formatted_analysis += f"**Additional Relevant Sections:**\n"
                            for section in analysis_data['additional_sections']:
                                formatted_analysis += f"• {section}\n"
                            formatted_analysis += "\n"
                        
                        if analysis_data.get('suggestions'):
                            formatted_analysis += f"**Legal Suggestions:**\n"
                            for i, suggestion in enumerate(analysis_data['suggestions'], 1):
                                formatted_analysis += f"{i}. {suggestion}\n"
                            formatted_analysis += "\n"
                        
                        if analysis_data.get('considerations'):
                            formatted_analysis += f"**Important Considerations:**\n"
                            for i, consideration in enumerate(analysis_data['considerations'], 1):
                                formatted_analysis += f"{i}. {consideration}\n"
                            formatted_analysis += "\n"
                        
                        if analysis_data.get('next_steps'):
                            formatted_analysis += f"**Recommended Next Steps:**\n"
                            for i, step in enumerate(analysis_data['next_steps'], 1):
                                formatted_analysis += f"{i}. {step}\n"
                        
                        message += formatted_analysis
                        
                    except json.JSONDecodeError:
                        # If JSON parsing fails, show the raw analysis
                        message += f"\n\n🤖 **AI Analysis:**\n\n{analysis_text}"
        
        return {
            "message": message,
            "sections": relevant_sections,
            "confidence": avg_confidence,
            "matched_keywords": [kw for section in relevant_sections for kw in section.get('matched_keywords', [])],
            "suggestions": suggestions,
            "enhanced_analysis": enhanced_analysis
        }

# Global instance
ml_enhancer = MLEnhancer()
