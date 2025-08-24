import json
import numpy as np
from typing import List, Dict
import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccuracyImprover:
    def __init__(self):
        self.ipc_sections = self.load_ipc_sections()
        self.expanded_sections = self.expand_sections()
        
        # Better TF-IDF parameters
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=2000,  # Increased from 1000
            stop_words='english',
            ngram_range=(1, 3),  # Increased from (1, 2)
            min_df=1,
            max_df=0.95
        )
        self.similarity_threshold = 0.15  # Lowered for better recall
        self.precompute_embeddings()
    
    def load_ipc_sections(self) -> List[Dict]:
        try:
            with open('data/ipc_sections.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sections', [])
        except Exception as e:
            logger.error(f"Failed to load IPC sections: {e}")
            return []
    
    def expand_sections(self) -> List[Dict]:
        """Expand sections with additional keywords"""
        expanded = []
        
        # Legal synonyms database
        legal_synonyms = {
            "theft": ["steal", "stolen", "robbery", "pickpocket", "burglary", "larceny", "thief", "stole", "took", "snatched"],
            "assault": ["hit", "beat", "punch", "slap", "kick", "attack", "physical assault", "bodily harm", "battery", "strike"],
            "murder": ["kill", "murder", "homicide", "death", "dead", "killed", "killing", "assassination", "slay", "slain"],
            "rape": ["rape", "sexual assault", "forced sex", "sexual violence", "sexual abuse", "molestation", "violation"],
            "extortion": ["extortion", "blackmail", "threat for money", "demand money", "coercion", "threaten for money"],
            "robbery": ["robbery", "armed robbery", "highway robbery", "mugging", "snatching", "forceful theft"],
            "kidnapping": ["kidnap", "abduct", "abduction", "kidnapping", "snatch", "seize", "capture"],
            "defamation": ["defamation", "slander", "libel", "false rumors", "character assassination", "smear"],
            "cyber_crime": ["cyber", "online", "internet", "digital", "computer", "hacking", "phishing"],
            "fraud": ["fraud", "cheat", "deceive", "swindle", "con", "scam", "dupe", "trick"],
            "forgery": ["forge", "counterfeit", "fake", "falsify", "fabricate", "alter", "tamper"],
            "arson": ["arson", "burn", "fire", "incendiary", "torch", "ignite", "set fire"],
            "drugs": ["drugs", "narcotics", "substance", "trafficking", "possession", "smuggling"],
            "corruption": ["corruption", "bribe", "bribery", "graft", "kickback", "payoff", "embezzlement"]
        }
        
        for section in self.ipc_sections:
            expanded_section = section.copy()
            expanded_keywords = set(section['keywords'])
            
            # Add synonyms
            for keyword in section['keywords']:
                for category, synonyms in legal_synonyms.items():
                    if keyword.lower() in synonyms or any(syn.lower() in keyword.lower() for syn in synonyms):
                        expanded_keywords.update(synonyms)
            
            # Add common legal terms
            legal_terms = ["offense", "crime", "criminal", "illegal", "unlawful", "prohibited", "punishable", "liable"]
            expanded_keywords.update(legal_terms)
            
            expanded_section['expanded_keywords'] = list(expanded_keywords)
            expanded.append(expanded_section)
        
        return expanded
    
    def precompute_embeddings(self):
        try:
            section_texts = []
            for section in self.expanded_sections:
                text = f"{section['title']} {section['description']} {' '.join(section['keywords'])} {' '.join(section.get('expanded_keywords', []))}"
                section_texts.append(text)
            
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(section_texts)
            logger.info(f"Pre-computed enhanced TF-IDF embeddings for {len(self.expanded_sections)} sections")
        except Exception as e:
            logger.error(f"Failed to precompute embeddings: {e}")
    
    def extract_keywords_enhanced(self, text: str) -> List[str]:
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add bigrams
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram.split()) == 2 and all(len(word) > 2 for word in bigram.split()):
                bigrams.append(bigram)
        
        return keywords + bigrams
    
    def pattern_matching(self, query: str) -> Dict[str, float]:
        patterns = {
            "theft": [r"stole my", r"took my", r"stolen", r"missing", r"lost my", r"someone took"],
            "assault": [r"hit me", r"beat me", r"attacked me", r"assaulted me", r"punch", r"slap", r"kick"],
            "murder": [r"killed", r"murdered", r"dead", r"death", r"killing", r"homicide"],
            "rape": [r"raped", r"sexual assault", r"molested", r"violated", r"forced"],
            "extortion": [r"demanded money", r"threatened for money", r"blackmail", r"extortion"],
            "robbery": [r"robbed", r"robbery", r"mugged", r"snatched", r"held up"],
            "kidnapping": [r"kidnapped", r"abducted", r"snatched", r"taken away", r"disappeared"],
            "defamation": [r"spread rumors", r"false rumors", r"defamed", r"slandered", r"libel"],
            "cyber_crime": [r"online", r"internet", r"cyber", r"digital", r"computer", r"hacking"]
        }
        
        scores = {}
        for category, pattern_list in patterns.items():
            score = 0
            for pattern in pattern_list:
                if re.search(pattern, query.lower()):
                    score += 1.0
            if score > 0:
                scores[category] = score
        
        return scores
    
    def tfidf_search_enhanced(self, query: str, top_k: int = 10):
        try:
            query_vector = self.tfidf_vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > self.similarity_threshold]
            return results
        except Exception as e:
            logger.error(f"Enhanced TF-IDF search failed: {e}")
            return []
    
    def find_relevant_sections_enhanced(self, user_input: str) -> List[Dict]:
        results = []
        keywords = self.extract_keywords_enhanced(user_input)
        pattern_scores = self.pattern_matching(user_input)
        
        # Enhanced TF-IDF Search
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
        
        # Enhanced keyword matching as fallback
        if not results:
            for section in self.expanded_sections:
                score = 0
                matched_keywords = []
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
        
        # Sort and remove duplicates
        seen_sections = set()
        unique_results = []
        for result in sorted(results, key=lambda x: x['score'], reverse=True):
            if result['section_number'] not in seen_sections:
                seen_sections.add(result['section_number'])
                unique_results.append(result)
        
        return unique_results[:5]

def test_improvements():
    """Test the improved system"""
    improver = AccuracyImprover()
    
    # Test cases
    test_cases = [
        "Someone stole my phone",
        "A person hit me with a stick during an argument",
        "Someone threatened me with a knife",
        "A person broke into my house and stole my laptop",
        "Someone posted my private photos online without permission"
    ]
    
    print("=" * 60)
    print("IMPROVED ACCURACY TEST RESULTS")
    print("=" * 60)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{i}. Query: \"{query}\"")
        results = improver.find_relevant_sections_enhanced(query)
        
        if results:
            print("   Predicted sections:")
            for j, result in enumerate(results[:3], 1):
                print(f"   {j}. IPC {result['section_number']} - {result['title']} (Score: {result['score']:.3f})")
        else:
            print("   No relevant sections found")
    
    # Save enhanced sections
    with open('data/enhanced_ipc_sections.json', 'w') as f:
        json.dump({'sections': improver.expanded_sections}, f, indent=2)
    
    print(f"\n📄 Enhanced IPC sections saved to 'data/enhanced_ipc_sections.json'")
    print(f"🔧 Improvements implemented:")
    print(f"   - Enhanced TF-IDF (2000 features, n-grams 1-3)")
    print(f"   - Legal synonyms database ({len(improver.expanded_sections)} sections expanded)")
    print(f"   - Pattern matching for crime detection")
    print(f"   - Lower similarity threshold (0.15)")
    print(f"   - Improved keyword extraction with bigrams")

if __name__ == "__main__":
    test_improvements()
