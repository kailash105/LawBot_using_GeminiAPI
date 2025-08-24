import json
import numpy as np
from typing import List, Dict, Tuple
import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccuracyImprover:
    def __init__(self):
        """Initialize the accuracy improver"""
        self.ipc_sections = self.load_ipc_sections()
        self.expanded_sections = self.expand_ipc_sections()
        self.legal_synonyms = self.load_legal_synonyms()
        self.crime_patterns = self.load_crime_patterns()
        
        # Enhanced TF-IDF with better parameters
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=2000,  # Increased from 1000
            stop_words='english',
            ngram_range=(1, 3),  # Increased from (1, 2)
            min_df=1,
            max_df=0.95
        )
        self.similarity_threshold = 0.2  # Lowered from 0.3 for better recall
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
    
    def load_legal_synonyms(self) -> Dict[str, List[str]]:
        """Load legal synonyms and terminology"""
        return {
            "theft": ["steal", "stolen", "robbery", "pickpocket", "burglary", "larceny", "thief", "stole", "took", "snatched", "appropriated", "misappropriated"],
            "assault": ["hit", "beat", "punch", "slap", "kick", "attack", "physical assault", "bodily harm", "battery", "strike", "thrash", "pummel"],
            "murder": ["kill", "murder", "homicide", "death", "dead", "killed", "killing", "assassination", "slay", "slain", "eliminate", "terminate"],
            "rape": ["rape", "sexual assault", "forced sex", "sexual violence", "sexual abuse", "molestation", "violation", "defilement"],
            "extortion": ["extortion", "blackmail", "threat for money", "demand money", "coercion", "threaten for money", "ransom", "compulsion"],
            "robbery": ["robbery", "armed robbery", "highway robbery", "mugging", "snatching", "forceful theft", "hold-up", "stick-up"],
            "kidnapping": ["kidnap", "abduct", "abduction", "kidnapping", "snatch", "seize", "capture", "detain unlawfully"],
            "defamation": ["defamation", "slander", "libel", "false rumors", "character assassination", "smear", "malign", "disparage"],
            "cyber_crime": ["cyber", "online", "internet", "digital", "computer", "hacking", "phishing", "cyberbullying", "online harassment"],
            "fraud": ["fraud", "cheat", "deceive", "swindle", "con", "scam", "dupe", "trick", "mislead"],
            "forgery": ["forge", "counterfeit", "fake", "falsify", "fabricate", "alter", "tamper"],
            "arson": ["arson", "burn", "fire", "incendiary", "torch", "ignite", "set fire"],
            "drugs": ["drugs", "narcotics", "substance", "trafficking", "possession", "smuggling", "peddling"],
            "corruption": ["corruption", "bribe", "bribery", "graft", "kickback", "payoff", "embezzlement"],
            "terrorism": ["terrorism", "terrorist", "bomb", "explosive", "threat", "intimidation", "coercion"]
        }
    
    def load_crime_patterns(self) -> Dict[str, List[str]]:
        """Load crime-specific patterns and phrases"""
        return {
            "theft": [
                r"stole my", r"took my", r"stolen", r"missing", r"disappeared", r"lost my",
                r"someone took", r"got stolen", r"was stolen", r"stole from", r"theft of"
            ],
            "assault": [
                r"hit me", r"beat me", r"attacked me", r"assaulted me", r"punch", r"slap",
                r"kick", r"strike", r"hit with", r"beat with", r"attacked with", r"assaulted with"
            ],
            "murder": [
                r"killed", r"murdered", r"dead", r"death", r"killing", r"homicide",
                r"someone killed", r"was killed", r"got killed", r"murder of", r"killed by"
            ],
            "rape": [
                r"raped", r"sexual assault", r"molested", r"violated", r"forced",
                r"sexually assaulted", r"molestation", r"sexual violence", r"rape of"
            ],
            "extortion": [
                r"demanded money", r"threatened for money", r"blackmail", r"extortion",
                r"forced to pay", r"demanded payment", r"threatened to", r"extorted"
            ],
            "robbery": [
                r"robbed", r"robbery", r"mugged", r"snatched", r"held up", r"stick up",
                r"armed robbery", r"robbed at gunpoint", r"robbed with weapon"
            ],
            "kidnapping": [
                r"kidnapped", r"abducted", r"snatched", r"taken away", r"disappeared",
                r"missing person", r"kidnapping", r"abduction", r"taken against will"
            ],
            "defamation": [
                r"spread rumors", r"false rumors", r"defamed", r"slandered", r"libel",
                r"character assassination", r"smear campaign", r"defamation", r"false statements"
            ],
            "cyber_crime": [
                r"online", r"internet", r"cyber", r"digital", r"computer", r"hacking",
                r"phishing", r"cyberbullying", r"online harassment", r"social media"
            ]
        }
    
    def expand_ipc_sections(self) -> List[Dict]:
        """Expand IPC sections with additional keywords and patterns"""
        expanded = []
        
        for section in self.ipc_sections:
            expanded_section = section.copy()
            
            # Add synonyms for existing keywords
            expanded_keywords = set(section['keywords'])
            for keyword in section['keywords']:
                for category, synonyms in self.legal_synonyms.items():
                    if keyword.lower() in synonyms or any(syn.lower() in keyword.lower() for syn in synonyms):
                        expanded_keywords.update(synonyms)
            
            # Add crime patterns
            for category, patterns in self.crime_patterns.items():
                if any(keyword.lower() in category for keyword in section['keywords']):
                    # Extract words from patterns
                    for pattern in patterns:
                        words = re.findall(r'\b\w+\b', pattern)
                        expanded_keywords.update(words)
            
            # Add common legal terms
            legal_terms = [
                "offense", "crime", "criminal", "illegal", "unlawful", "prohibited",
                "punishable", "liable", "guilty", "conviction", "sentence", "penalty"
            ]
            expanded_keywords.update(legal_terms)
            
            expanded_section['expanded_keywords'] = list(expanded_keywords)
            expanded.append(expanded_section)
        
        return expanded
    
    def precompute_embeddings(self):
        """Pre-compute enhanced TF-IDF embeddings"""
        try:
            # Create enhanced text for each section
            section_texts = []
            for section in self.expanded_sections:
                # Combine title, description, keywords, and expanded keywords
                text = f"{section['title']} {section['description']} {' '.join(section['keywords'])} {' '.join(section.get('expanded_keywords', []))}"
                section_texts.append(text)
            
            # Compute TF-IDF matrix
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(section_texts)
            logger.info(f"Pre-computed enhanced TF-IDF embeddings for {len(self.expanded_sections)} sections")
        except Exception as e:
            logger.error(f"Failed to precompute embeddings: {e}")
    
    def extract_keywords_enhanced(self, text: str) -> List[str]:
        """Enhanced keyword extraction with legal terminology"""
        # Convert to lowercase and clean
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Enhanced stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs',
            'very', 'much', 'many', 'some', 'any', 'all', 'each', 'every', 'no', 'not', 'never', 'always',
            'here', 'there', 'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose'
        }
        
        # Extract keywords
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add bigrams and trigrams
        bigrams = []
        trigrams = []
        
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram.split()) == 2 and all(len(word) > 2 for word in bigram.split()):
                bigrams.append(bigram)
        
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(trigram.split()) == 3 and all(len(word) > 2 for word in trigram.split()):
                trigrams.append(trigram)
        
        # Add legal synonyms
        legal_keywords = []
        for keyword in keywords:
            for category, synonyms in self.legal_synonyms.items():
                if keyword.lower() in synonyms:
                    legal_keywords.extend(synonyms)
        
        return keywords + bigrams + trigrams + legal_keywords
    
    def pattern_matching(self, query: str) -> Dict[str, float]:
        """Enhanced pattern matching for crime detection"""
        pattern_scores = defaultdict(float)
        
        for category, patterns in self.crime_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query.lower()):
                    pattern_scores[category] += 1.0
        
        return dict(pattern_scores)
    
    def tfidf_search_enhanced(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Enhanced TF-IDF search with better parameters"""
        try:
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top-k results with lower threshold
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > self.similarity_threshold]
            return results
        except Exception as e:
            logger.error(f"Enhanced TF-IDF search failed: {e}")
            return []
    
    def find_relevant_sections_enhanced(self, user_input: str) -> List[Dict]:
        """Enhanced section finding with multiple techniques"""
        results = []
        
        # Extract enhanced keywords
        keywords = self.extract_keywords_enhanced(user_input)
        
        # Get pattern matching scores
        pattern_scores = self.pattern_matching(user_input)
        
        # Method 1: Enhanced TF-IDF Search
        if self.tfidf_matrix is not None:
            tfidf_results = self.tfidf_search_enhanced(user_input)
            for idx, score in tfidf_results:
                section = self.expanded_sections[idx].copy()
                
                # Boost score based on pattern matching
                pattern_boost = 0
                for category, pattern_score in pattern_scores.items():
                    if any(cat in section['title'].lower() or cat in ' '.join(section['keywords']).lower() for cat in [category]):
                        pattern_boost += pattern_score * 0.3
                
                section['score'] = score + pattern_boost
                section['method'] = 'enhanced_tfidf'
                section['matched_keywords'] = [kw for kw in keywords if any(
                    SequenceMatcher(None, kw.lower(), sk.lower()).ratio() > 0.6 
                    for sk in section.get('expanded_keywords', section['keywords'])
                )]
                results.append(section)
        
        # Method 2: Enhanced keyword matching
        if not results:
            for section in self.expanded_sections:
                score = 0
                matched_keywords = []
                
                # Check against expanded keywords
                expanded_keywords = section.get('expanded_keywords', section['keywords'])
                
                for keyword in keywords:
                    for section_keyword in expanded_keywords:
                        similarity = SequenceMatcher(None, keyword.lower(), section_keyword.lower()).ratio()
                        if similarity > 0.8:
                            score += similarity * 3
                            matched_keywords.append(keyword)
                        elif similarity > 0.6:
                            score += similarity * 2
                            matched_keywords.append(keyword)
                        elif similarity > 0.4:
                            score += similarity
                
                # Add pattern matching boost
                for category, pattern_score in pattern_scores.items():
                    if any(cat in section['title'].lower() or cat in ' '.join(expanded_keywords).lower() for cat in [category]):
                        score += pattern_score * 0.5
                
                if score > 0:
                    section_copy = section.copy()
                    section_copy['score'] = score / len(keywords) if keywords else 0
                    section_copy['method'] = 'enhanced_keyword_matching'
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
    
    def generate_improvement_report(self) -> str:
        """Generate a report on accuracy improvements"""
        report = "=" * 60 + "\n"
        report += "ACCURACY IMPROVEMENT IMPLEMENTATION REPORT\n"
        report += "=" * 60 + "\n\n"
        
        report += "🔧 IMPROVEMENTS IMPLEMENTED\n"
        report += "-" * 40 + "\n"
        report += "✅ Enhanced TF-IDF Vectorization:\n"
        report += "   - Increased max_features from 1000 to 2000\n"
        report += "   - Extended ngram_range from (1,2) to (1,3)\n"
        report += "   - Added min_df and max_df parameters\n\n"
        
        report += "✅ Legal Synonyms Database:\n"
        report += f"   - Added {len(self.legal_synonyms)} legal categories\n"
        report += "   - Expanded keyword coverage with synonyms\n"
        report += "   - Improved semantic understanding\n\n"
        
        report += "✅ Crime Pattern Matching:\n"
        report += f"   - Added {len(self.crime_patterns)} crime patterns\n"
        report += "   - Regex-based pattern detection\n"
        report += "   - Context-aware scoring\n\n"
        
        report += "✅ Enhanced Keyword Extraction:\n"
        report += "   - Added bigrams and trigrams\n"
        report += "   - Legal terminology integration\n"
        report += "   - Improved stop word filtering\n\n"
        
        report += "✅ Expanded IPC Sections:\n"
        report += f"   - Enhanced {len(self.expanded_sections)} sections\n"
        report += "   - Added expanded keywords\n"
        report += "   - Better coverage of legal terms\n\n"
        
        report += "✅ Improved Scoring System:\n"
        report += "   - Pattern matching boost\n"
        report += "   - Multi-method score combination\n"
        report += "   - Lower similarity threshold (0.2)\n\n"
        
        report += "📊 EXPECTED IMPROVEMENTS\n"
        report += "-" * 40 + "\n"
        report += "🎯 Precision: 16.9% → 35-45% (+100-150% improvement)\n"
        report += "🎯 Recall: 52.4% → 70-80% (+30-50% improvement)\n"
        report += "🎯 F1-Score: 25.6% → 45-55% (+75-115% improvement)\n"
        report += "🎯 Overall Accuracy: 0% → 15-25% (significant improvement)\n\n"
        
        report += "🚀 NEXT STEPS\n"
        report += "-" * 40 + "\n"
        report += "1. Test the improved system with the same evaluation\n"
        report += "2. Fine-tune similarity thresholds based on results\n"
        report += "3. Add more legal synonyms and patterns\n"
        report += "4. Implement sentence transformer integration\n"
        report += "5. Add legal expert validation\n\n"
        
        report += "=" * 60 + "\n"
        
        return report

def main():
    """Run accuracy improvement implementation"""
    improver = AccuracyImprover()
    report = improver.generate_improvement_report()
    print(report)
    
    # Save enhanced sections
    with open('data/enhanced_ipc_sections.json', 'w') as f:
        json.dump({'sections': improver.expanded_sections}, f, indent=2)
    
    print("📄 Enhanced IPC sections saved to 'data/enhanced_ipc_sections.json'")

if __name__ == "__main__":
    main()
