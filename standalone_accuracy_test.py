import json
import numpy as np
from typing import List, Dict, Tuple
import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandaloneAccuracyEvaluator:
    def __init__(self):
        """Initialize the standalone accuracy evaluator"""
        self.ipc_sections = self.load_ipc_sections()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.similarity_threshold = 0.3
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
        """Pre-compute TF-IDF embeddings for all IPC sections"""
        try:
            # Create combined text for each section
            section_texts = []
            for section in self.ipc_sections:
                text = f"{section['title']} {section['description']} {' '.join(section['keywords'])}"
                section_texts.append(text)
            
            # Compute TF-IDF matrix
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
    
    def tfidf_search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Perform TF-IDF based search"""
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
    
    def find_relevant_sections_enhanced(self, user_input: str) -> List[Dict]:
        """Enhanced section finding using multiple ML techniques"""
        results = []
        
        # Extract keywords
        keywords = self.extract_keywords_advanced(user_input)
        
        # Method 1: TF-IDF Search
        if self.tfidf_matrix is not None:
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
        
        # Method 2: Traditional keyword matching (fallback)
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
    
    def load_test_cases(self) -> List[Dict]:
        """Load test cases with ground truth data"""
        test_cases = [
            {
                "query": "Someone stole my phone",
                "expected_sections": ["379"],
                "category": "theft",
                "description": "Basic theft case"
            },
            {
                "query": "A person hit me with a stick during an argument",
                "expected_sections": ["323", "324"],
                "category": "assault",
                "description": "Assault with weapon"
            },
            {
                "query": "Someone threatened me with a knife",
                "expected_sections": ["324", "307"],
                "category": "assault",
                "description": "Assault with dangerous weapon"
            },
            {
                "query": "A person broke into my house and stole my laptop",
                "expected_sections": ["380", "379"],
                "category": "burglary",
                "description": "House burglary with theft"
            },
            {
                "query": "Someone posted my private photos online without permission",
                "expected_sections": ["354", "500"],
                "category": "cyber_crime",
                "description": "Cyber harassment and defamation"
            },
            {
                "query": "My neighbor killed my dog",
                "expected_sections": ["429"],
                "category": "animal_cruelty",
                "description": "Animal cruelty case"
            },
            {
                "query": "Someone demanded money from me by threatening to harm my family",
                "expected_sections": ["384", "506"],
                "category": "extortion",
                "description": "Extortion with threats"
            },
            {
                "query": "A group of people robbed me at gunpoint",
                "expected_sections": ["395", "392"],
                "category": "robbery",
                "description": "Armed gang robbery"
            },
            {
                "query": "Someone sexually assaulted me",
                "expected_sections": ["376"],
                "category": "sexual_assault",
                "description": "Rape case"
            },
            {
                "query": "My employee stole money from the company",
                "expected_sections": ["406"],
                "category": "white_collar",
                "description": "Criminal breach of trust"
            },
            {
                "query": "Someone tried to kill me but I survived",
                "expected_sections": ["307"],
                "category": "attempted_murder",
                "description": "Attempted murder"
            },
            {
                "query": "A person molested me in a crowded bus",
                "expected_sections": ["354"],
                "category": "molestation",
                "description": "Sexual harassment/molestation"
            },
            {
                "query": "Someone spread false rumors about me",
                "expected_sections": ["500"],
                "category": "defamation",
                "description": "Defamation case"
            },
            {
                "query": "My business partner embezzled company funds",
                "expected_sections": ["406"],
                "category": "white_collar",
                "description": "Embezzlement"
            },
            {
                "query": "Someone kidnapped my child",
                "expected_sections": ["363"],
                "category": "kidnapping",
                "description": "Kidnapping case"
            }
        ]
        return test_cases
    
    def evaluate_single_case(self, test_case: Dict) -> Dict:
        """Evaluate a single test case"""
        query = test_case["query"]
        expected_sections = set(test_case["expected_sections"])
        
        # Get predictions from ML enhancer
        relevant_sections = self.find_relevant_sections_enhanced(query)
        predicted_sections = set([section['section_number'] for section in relevant_sections])
        
        # Calculate metrics
        true_positives = len(expected_sections.intersection(predicted_sections))
        false_positives = len(predicted_sections - expected_sections)
        false_negatives = len(expected_sections - predicted_sections)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = 1 if expected_sections == predicted_sections else 0
        
        # Calculate confidence scores
        avg_confidence = np.mean([section['score'] for section in relevant_sections]) if relevant_sections else 0
        
        return {
            "query": query,
            "expected_sections": list(expected_sections),
            "predicted_sections": list(predicted_sections),
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "category": test_case["category"],
            "description": test_case["description"]
        }
    
    def evaluate_all_cases(self) -> Dict:
        """Evaluate all test cases and calculate overall metrics"""
        results = []
        test_cases = self.load_test_cases()
        
        for test_case in test_cases:
            result = self.evaluate_single_case(test_case)
            results.append(result)
            logger.info(f"Test case: {test_case['description']} - F1: {result['f1_score']:.3f}")
        
        # Calculate overall metrics
        overall_metrics = self.calculate_overall_metrics(results)
        
        return {
            "individual_results": results,
            "overall_metrics": overall_metrics,
            "category_metrics": self.calculate_category_metrics(results)
        }
    
    def calculate_overall_metrics(self, results: List[Dict]) -> Dict:
        """Calculate overall accuracy metrics"""
        total_cases = len(results)
        
        # Micro-averaging for precision, recall, F1
        total_tp = sum(r['true_positives'] for r in results)
        total_fp = sum(r['false_positives'] for r in results)
        total_fn = sum(r['false_negatives'] for r in results)
        
        micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        micro_f1 = 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0
        
        # Macro-averaging
        macro_precision = np.mean([r['precision'] for r in results])
        macro_recall = np.mean([r['recall'] for r in results])
        macro_f1 = np.mean([r['f1_score'] for r in results])
        
        # Overall accuracy
        overall_accuracy = np.mean([r['accuracy'] for r in results])
        avg_confidence = np.mean([r['avg_confidence'] for r in results])
        
        return {
            "total_cases": total_cases,
            "micro_precision": micro_precision,
            "micro_recall": micro_recall,
            "micro_f1": micro_f1,
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1,
            "overall_accuracy": overall_accuracy,
            "avg_confidence": avg_confidence
        }
    
    def calculate_category_metrics(self, results: List[Dict]) -> Dict:
        """Calculate metrics by category"""
        categories = {}
        
        for result in results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        category_metrics = {}
        for category, category_results in categories.items():
            category_metrics[category] = {
                "count": len(category_results),
                "avg_precision": np.mean([r['precision'] for r in category_results]),
                "avg_recall": np.mean([r['recall'] for r in category_results]),
                "avg_f1": np.mean([r['f1_score'] for r in category_results]),
                "avg_accuracy": np.mean([r['accuracy'] for r in category_results])
            }
        
        return category_metrics
    
    def generate_accuracy_report(self) -> str:
        """Generate a comprehensive accuracy report"""
        evaluation_results = self.evaluate_all_cases()
        
        report = "=" * 60 + "\n"
        report += "IPC CRIME ANALYZER - ACCURACY EVALUATION REPORT\n"
        report += "=" * 60 + "\n\n"
        
        # Overall metrics
        overall = evaluation_results['overall_metrics']
        report += "📊 OVERALL PERFORMANCE METRICS\n"
        report += "-" * 40 + "\n"
        report += f"Total Test Cases: {overall['total_cases']}\n"
        report += f"Overall Accuracy: {overall['overall_accuracy']:.1%}\n"
        report += f"Micro F1-Score: {overall['micro_f1']:.1%}\n"
        report += f"Macro F1-Score: {overall['macro_f1']:.1%}\n"
        report += f"Micro Precision: {overall['micro_precision']:.1%}\n"
        report += f"Micro Recall: {overall['micro_recall']:.1%}\n"
        report += f"Average Confidence: {overall['avg_confidence']:.1%}\n\n"
        
        # Category performance
        report += "📈 PERFORMANCE BY CRIME CATEGORY\n"
        report += "-" * 40 + "\n"
        for category, metrics in evaluation_results['category_metrics'].items():
            report += f"{category.upper()}:\n"
            report += f"  Cases: {metrics['count']}\n"
            report += f"  Accuracy: {metrics['avg_accuracy']:.1%}\n"
            report += f"  F1-Score: {metrics['avg_f1']:.1%}\n"
            report += f"  Precision: {metrics['avg_precision']:.1%}\n"
            report += f"  Recall: {metrics['avg_recall']:.1%}\n\n"
        
        # Individual case results
        report += "🔍 INDIVIDUAL TEST CASE RESULTS\n"
        report += "-" * 40 + "\n"
        for i, result in enumerate(evaluation_results['individual_results'], 1):
            report += f"{i}. {result['description']}\n"
            report += f"   Query: \"{result['query']}\"\n"
            report += f"   Expected: {result['expected_sections']}\n"
            report += f"   Predicted: {result['predicted_sections']}\n"
            report += f"   F1-Score: {result['f1_score']:.1%} | Accuracy: {result['accuracy']:.1%}\n"
            report += f"   Confidence: {result['avg_confidence']:.1%}\n\n"
        
        # Accuracy assessment
        report += "🎯 ACCURACY ASSESSMENT\n"
        report += "-" * 40 + "\n"
        
        if overall['micro_f1'] >= 0.9:
            report += "✅ EXCELLENT: System shows high accuracy (90%+)\n"
        elif overall['micro_f1'] >= 0.8:
            report += "✅ GOOD: System shows good accuracy (80-90%)\n"
        elif overall['micro_f1'] >= 0.7:
            report += "⚠️  FAIR: System shows fair accuracy (70-80%)\n"
        else:
            report += "❌ POOR: System needs improvement (<70%)\n"
        
        report += f"\nCurrent Claim: 95%+ Accuracy\n"
        report += f"Actual Performance: {overall['micro_f1']:.1%} F1-Score\n"
        
        if overall['micro_f1'] >= 0.95:
            report += "✅ Claim is VALIDATED\n"
        else:
            report += "❌ Claim is NOT VALIDATED\n"
        
        report += "\n" + "=" * 60 + "\n"
        
        return report

def main():
    """Run accuracy evaluation"""
    evaluator = StandaloneAccuracyEvaluator()
    report = evaluator.generate_accuracy_report()
    print(report)
    
    # Save detailed results to JSON
    evaluation_results = evaluator.evaluate_all_cases()
    with open('accuracy_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print("📄 Detailed results saved to 'accuracy_results.json'")

if __name__ == "__main__":
    main()
