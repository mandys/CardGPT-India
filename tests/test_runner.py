#!/usr/bin/env python3
"""
Automated Test Runner for Credit Card RAG Assistant
Tests key functionality to prevent regressions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from typing import Dict, List
from src.embedder import EmbeddingService
from src.llm import LLMService
from src.retriever import DocumentRetriever
from src.query_enhancer import QueryEnhancer

class CreditCardTestRunner:
    def __init__(self, model: str = "gemini-1.5-flash"):
        """Initialize test runner with current RAG system"""
        self.model = model
        self.test_cases = self._load_test_cases()
        self.results = []
        
        # Initialize services (similar to app.py)
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            gemini_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            self.embedder = EmbeddingService(api_key)
            self.llm = LLMService(api_key, gemini_key)
            self.retriever = DocumentRetriever()
            self.query_enhancer = QueryEnhancer()
            
            # Load and process data (similar to app.py)
            print("🔄 Loading credit card data...")
            documents = self.retriever.load_documents_from_json("data")
            embeddings, _ = self.embedder.generate_batch_embeddings(documents)
            self.retriever.store_documents_and_embeddings(documents, embeddings)
            print(f"✅ Loaded {len(documents)} documents")
            
        except Exception as e:
            print(f"❌ Failed to initialize test system: {e}")
            raise
    
    def _load_test_cases(self) -> List[Dict]:
        """Load test cases adapted for current system"""
        return [
            # Milestone Calculation Tests (Critical)
            {
                "category": "Milestone Calculation",
                "query": "If I spend ₹7.5 lakh yearly on Atlas, how many miles do I get?",
                "expected_keywords": ["15,000", "2,500", "milestone", "₹7.5", "cumulative"],
                "expected_calculation": "base (15,000) + milestones (5,000) = 20,000",
                "critical": True
            },
            {
                "category": "Milestone Calculation", 
                "query": "For ₹3 lakh spend on Axis Atlas, what rewards do I get?",
                "expected_keywords": ["6,000", "2,500", "milestone", "₹3", "8,500"],
                "expected_calculation": "base (6,000) + milestone (2,500) = 8,500",
                "critical": True
            },
            
            # Hotel/Flight Cap Tests (Critical)
            {
                "category": "Hotel Cap Logic",
                "query": "If I spend ₹3 lakh on hotels which card wins?",
                "expected_keywords": ["10,000", "2,000", "2,500", "14,500", "Atlas"],
                "expected_calculation": "₹2L@5x (10,000) + ₹1L@2x (2,000) + milestone (2,500)",
                "critical": True
            },
            {
                "category": "Hotel Cap Logic",
                "query": "For ₹1 lakh hotel spend on Atlas, how many miles?",
                "expected_keywords": ["5,000", "hotel", "₹1", "under cap"],
                "expected_calculation": "₹1L@5x = 5,000 (under ₹2L cap)",
                "critical": True
            },
            
            # Utility Spending Tests
            {
                "category": "Utility Spending",
                "query": "Which card is better for ₹55K utility spends?",
                "expected_keywords": ["1,000", "₹50", "surcharge", "ICICI", "cap"],
                "expected_content": "ICICI EPM better with capped rewards + surcharge"
            },
            {
                "category": "Utility Spending",
                "query": "Do I get points on utility spends using ICICI EPM?",
                "expected_keywords": ["6 points", "₹200", "1,000", "cap", "utility"],
                "expected_content": "yes with 1,000 point cap"
            },
            
            # Exclusion Tests
            {
                "category": "Exclusions",
                "query": "Do I get rewards on fuel with Atlas?",
                "expected_keywords": ["excluded", "no rewards", "fuel", "0"],
                "expected_content": "fuel excluded from rewards"
            },
            {
                "category": "Exclusions",
                "query": "Can I earn points on rent payments with both cards?",
                "expected_keywords": ["excluded", "no rewards", "rent", "both"],
                "expected_content": "both cards exclude rent"
            },
            
            # Insurance Tests  
            {
                "category": "Insurance Spending",
                "query": "Do we get points on insurance payments using ICICI EPM?",
                "expected_keywords": ["6 points", "₹200", "5,000", "cap", "insurance"],
                "expected_content": "rewards with 5,000 point cap"
            },
            {
                "category": "Insurance Spending",
                "query": "Do we get points on insurance payments using Axis Atlas?",
                "expected_keywords": ["excluded", "no rewards", "insurance", "not"],
                "expected_content": "excluded from rewards"
            },
            
            # Education Tests
            {
                "category": "Education Spending",
                "query": "I have ₹30,000 education fees. Which card is better?",
                "expected_keywords": ["900", "600", "ICICI", "better", "education"],
                "expected_winner": "icici"
            },
            {
                "category": "Education Spending",
                "query": "I have ₹1,00,000 education fees. Which card is better?",
                "expected_keywords": ["2,000", "1,000", "cap", "Atlas", "better"],
                "expected_winner": "axis"
            },
            
            # General Comparison Tests
            {
                "category": "General Comparison",
                "query": "For ₹1 lakh general spend, which card gives more rewards?",
                "expected_keywords": ["3,000", "2,000", "ICICI", "better"],
                "expected_winner": "icici"
            },
            {
                "category": "Hotel Spending",
                "query": "Which card is better for hotel bookings?",
                "expected_keywords": ["5 miles", "₹100", "accelerated", "Atlas"],
                "expected_winner": "axis"
            },
            
            # Surcharge Tests
            {
                "category": "Surcharge Calculation",
                "query": "What surcharge will I pay for ₹55K utility spend on ICICI EPM?",
                "expected_keywords": ["₹50", "1%", "₹50,000", "threshold", "surcharge"],
                "expected_calculation": "1% × (55,000 - 50,000) = ₹50"
            },
            {
                "category": "Surcharge Calculation", 
                "query": "What surcharge for ₹30K utility spend on Atlas?",
                "expected_keywords": ["₹50", "1%", "₹25,000", "threshold", "surcharge"],
                "expected_calculation": "1% × (30,000 - 25,000) = ₹50"
            },
            
            # Additional Test Cases (User Requested)
            {
                "category": "Hotel Spending Detailed",
                "query": "If I spend ₹100,000 on hotel bookings which card gives more rewards?",
                "expected_keywords": ["5,000", "3,000", "Atlas", "better", "hotel"],
                "expected_winner": "axis"
            },
            {
                "category": "Government Exclusions",
                "query": "Do I get rewards on government payments?",
                "expected_keywords": ["excluded", "no rewards", "government", "both"],
                "expected_content": "excluded from both cards"
            },
            {
                "category": "Tier Benefits",
                "query": "Tell me about gold tier benefits of axis",
                "expected_keywords": ["Gold", "tier", "lounge", "benefits", "Atlas"],
                "expected_content": "Gold tier specific benefits"
            },
            {
                "category": "Dining Spending",
                "query": "If I spend ₹50,000 on dining which card is better?",
                "expected_keywords": ["1,500", "1,000", "ICICI", "dining"],
                "expected_winner": "icici"
            },
            {
                "category": "Insurance Comparison",
                "query": "Tell me which card is better for insurance spends",
                "expected_keywords": ["ICICI", "5,000", "cap", "excluded", "Atlas"],
                "expected_winner": "icici"
            },
            {
                "category": "Grocery Limits",
                "query": "What are the reward limits for grocery spending?",
                "expected_keywords": ["1,000", "cap", "ICICI", "grocery", "cycle"],
                "expected_content": "ICICI EPM grocery spending caps"
            },
            {
                "category": "Flight Spending Large",
                "query": "If I spend ₹2 lakh on flights which card wins?",
                "expected_keywords": ["10,000", "6,000", "Atlas", "flight", "accelerated"],
                "expected_winner": "axis"
            },
            {
                "category": "Lounge Access",
                "query": "Which card is better for Guest Lounge Access at airport?",
                "expected_keywords": ["Atlas", "tier", "lounge", "guest", "access"],
                "expected_winner": "axis"
            },
            {
                "category": "Complex Spend Distribution",
                "query": "I have monthly spends of 1L, split as 20% Rent, 10% Utility, 20% Grocery, 10% Uber, 20% on Food and Eating Out, 20% on Buying Gift cards. Which card is better for which spend?",
                "expected_keywords": ["excluded", "rent", "ICICI", "grocery", "1,000", "cap"],
                "expected_content": "category-wise breakdown with exclusions"
            },
            {
                "category": "Excluded Categories Combined",
                "query": "For 20K spend on rent and 20K spends on gift card, which card is better?",
                "expected_keywords": ["excluded", "rent", "no rewards", "neither"],
                "expected_content": "both categories excluded"
            },
            {
                "category": "Annual Milestone Validation",
                "query": "For a yearly spend of 7.5L on Atlas, how many miles I earn?",
                "expected_keywords": ["15,000", "2,500", "20,000", "milestone", "yearly"],
                "expected_calculation": "15,000 base + 5,000 milestones = 20,000",
                "critical": True
            },
            
            # Regression Tests (User Reported Issues)
            {
                "category": "Hotel Milestone Missing",
                "query": "how many points will i earn for spending 3L on hotel",
                "expected_keywords": ["10,000", "2,000", "2,500", "14,500", "milestone"],
                "expected_calculation": "10,000 + 2,000 + 2,500 = 14,500",
                "critical": True
            },
            {
                "category": "Complex Multi-Category Calculation",
                "query": "what points will i get for a spend of 10L in a month on axis atlas, where 2L is on flights, 2L on hotels, and rest are general spends",
                "expected_keywords": ["10,000", "4,000", "12,000", "5,000", "31,000", "milestone"],
                "expected_calculation": "flights(10K accelerated) + hotels(4K base, cap used) + general(12K) + milestones(5K) = 31K",
                "critical": True
            },
            
            # HSBC Premier Tests
            {
                "category": "HSBC Premier Utilities",
                "query": "are utilities capped for hsbc premier card?",
                "expected_keywords": ["capped", "₹1,00,000", "monthly", "utility", "reward points"],
                "expected_content": "utilities capped at monthly limit"
            },
            {
                "category": "HSBC Premier Welcome Benefits", 
                "query": "what are the joining benefits of HSBC Premier card?",
                "expected_keywords": ["Taj", "₹12,000", "Epicure", "EazyDiner", "welcome"],
                "expected_content": "Taj voucher and membership benefits"
            },
            {
                "category": "HSBC Premier Reward Rate",
                "query": "What is the reward rate for HSBC Premier?",
                "expected_keywords": ["3 points", "₹100", "reward points"],
                "expected_content": "3 points per ₹100 spending"
            },
            {
                "category": "HSBC Premier Utility Calculation",
                "query": "If I spend ₹50,000 on utilities with HSBC Premier, how many points?",
                "expected_keywords": ["1,500", "3 points", "₹100", "utility"],
                "expected_calculation": "(50000 ÷ 100) × 3 = 1,500 points"
            },
            {
                "category": "HSBC Premier Lounge Access",
                "query": "What lounge access does HSBC Premier provide?",
                "expected_keywords": ["unlimited", "complimentary", "LoungeKey", "international"],
                "expected_content": "unlimited domestic and international lounge access"
            },
            {
                "category": "HSBC Premier Miles Transfer",
                "query": "Can I transfer HSBC Premier points to airlines?",
                "expected_keywords": ["1:1", "airlines", "Singapore", "Qatar", "British Airways"],
                "expected_content": "1:1 conversion to multiple airlines"
            }
        ]
    
    def process_query(self, question: str) -> Dict:
        """Process query using current system (similar to app.py)"""
        try:
            # Enhance query
            enhanced_question, _ = self.query_enhancer.enhance_query(question)
            
            # Generate query embedding
            query_embedding, _ = self.embedder.generate_single_embedding(question)
            
            # Search for relevant documents
            relevant_docs = self.retriever.search_similar_documents(
                query_embedding=query_embedding,
                top_k=5,
                card_filter=None,
                boost_keywords=['reward', 'milestone', 'surcharge', 'fees']
            )
            
            # Generate answer
            answer, llm_usage = self.llm.generate_answer(
                question=enhanced_question,
                context_documents=relevant_docs,
                card_name=None,
                model_choice=self.model
            )
            
            return {
                "success": True,
                "answer": answer,
                "enhanced_question": enhanced_question,
                "docs_count": len(relevant_docs),
                "model": llm_usage.get("model", self.model),
                "tokens": llm_usage.get("total_tokens", 0),
                "cost": llm_usage.get("cost", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"ERROR: {str(e)}",
                "error": str(e)
            }
    
    def run_test(self, test_case: Dict) -> Dict:
        """Run a single test case"""
        query = test_case["query"]
        expected_keywords = test_case.get("expected_keywords", [])
        expected_winner = test_case.get("expected_winner", "")
        expected_content = test_case.get("expected_content", "")
        is_critical = test_case.get("critical", False)
        
        print(f"Testing: {query[:60]}...")
        
        # Process query
        result = self.process_query(query)
        
        if not result["success"]:
            return {
                "query": query,
                "category": test_case["category"],
                "response": result["answer"],
                "status": "ERROR",
                "score": 0.0,
                "error": result.get("error", "Unknown error"),
                "critical": is_critical,
                "timestamp": datetime.now().isoformat()
            }
        
        response = result["answer"]
        response_lower = response.lower()
        
        # Check keywords (with flexible number matching)
        keyword_matches = []
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            # For numbers, check both with and without commas
            if keyword_lower in response_lower:
                keyword_matches.append(keyword)
            elif ',' in keyword_lower:
                # Try without comma (e.g., "15,000" -> "15000")
                no_comma = keyword_lower.replace(',', '')
                if no_comma in response_lower:
                    keyword_matches.append(keyword)
        
        # Check winner (if applicable)
        winner_correct = True
        if expected_winner:
            if expected_winner.lower() not in response_lower:
                winner_correct = False
        
        # Check content expectations
        content_correct = True
        if expected_content:
            content_words = expected_content.lower().split()
            if not any(word in response_lower for word in content_words):
                content_correct = False
        
        # Calculate score
        keyword_score = len(keyword_matches) / len(expected_keywords) if expected_keywords else 1.0
        content_score = 1.0 if content_correct else 0.0
        winner_score = 1.0 if winner_correct else 0.0
        
        # Weighted scoring (keywords most important for calculations)
        overall_score = (keyword_score * 0.6 + content_score * 0.25 + winner_score * 0.15)
        
        # Determine status - stricter for critical tests
        if is_critical:
            if overall_score >= 0.9:
                status = "PASSING"
            elif overall_score >= 0.7:
                status = "PARTIAL"
            else:
                status = "FAILING"
        else:
            if overall_score >= 0.8:
                status = "PASSING"
            elif overall_score >= 0.5:
                status = "PARTIAL"
            else:
                status = "FAILING"
        
        return {
            "query": query,
            "category": test_case["category"],
            "response": response,
            "status": status,
            "score": overall_score,
            "keyword_matches": keyword_matches,
            "missing_keywords": [k for k in expected_keywords if k not in keyword_matches],
            "winner_correct": winner_correct,
            "content_correct": content_correct,
            "critical": is_critical,
            "model": result.get("model", self.model),
            "tokens": result.get("tokens", 0),
            "cost": result.get("cost", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_all_tests(self) -> List[Dict]:
        """Run all test cases"""
        print(f"🚀 Starting automated test run with {self.model}...")
        print("=" * 80)
        
        results = []
        critical_failures = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{len(self.test_cases)}] {test_case['category']}")
            result = self.run_test(test_case)
            results.append(result)
            
            # Track critical failures
            if result.get('critical') and result['status'] in ['FAILING', 'ERROR']:
                critical_failures.append(result)
            
            # Print status
            status_emoji = {"PASSING": "✅", "PARTIAL": "⚠️", "FAILING": "❌", "ERROR": "💥"}
            critical_marker = " 🔴 CRITICAL" if result.get('critical') else ""
            print(f"   {status_emoji.get(result['status'], '❓')} {result['status']} (Score: {result['score']:.2f}){critical_marker}")
            
            if result['missing_keywords']:
                print(f"   Missing: {', '.join(result['missing_keywords'][:3])}")
        
        self.results = results
        
        # Warn about critical failures
        if critical_failures:
            print(f"\n🚨 WARNING: {len(critical_failures)} CRITICAL test(s) failed!")
            for failure in critical_failures:
                print(f"   • {failure['category']}: {failure['query'][:50]}...")
        
        return results
    
    def generate_report(self) -> str:
        """Generate detailed test report"""
        if not self.results:
            return "No test results available."
        
        report = []
        report.append("=" * 80)
        report.append("🧪 CREDIT CARD RAG ASSISTANT TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Model Used: {self.model}")
        report.append(f"Total Tests: {len(self.results)}")
        
        # Summary stats
        passing = len([r for r in self.results if r['status'] == 'PASSING'])
        partial = len([r for r in self.results if r['status'] == 'PARTIAL'])
        failing = len([r for r in self.results if r['status'] == 'FAILING'])
        errors = len([r for r in self.results if r['status'] == 'ERROR'])
        
        critical_tests = [r for r in self.results if r.get('critical')]
        critical_passing = len([r for r in critical_tests if r['status'] == 'PASSING'])
        
        report.append(f"✅ Passing: {passing}")
        report.append(f"⚠️  Partial: {partial}")
        report.append(f"❌ Failing: {failing}")
        report.append(f"💥 Errors: {errors}")
        report.append(f"📊 Overall Score: {sum(r['score'] for r in self.results) / len(self.results):.1%}")
        report.append(f"🔴 Critical Tests: {critical_passing}/{len(critical_tests)} passing")
        
        # Cost analysis
        total_cost = sum(r.get('cost', 0) for r in self.results)
        total_tokens = sum(r.get('tokens', 0) for r in self.results)
        report.append(f"💰 Total Cost: ${total_cost:.4f}")
        report.append(f"🔢 Total Tokens: {total_tokens:,}")
        report.append("")
        
        # Category breakdown
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'passing': 0, 'total': 0}
            categories[cat]['total'] += 1
            if result['status'] == 'PASSING':
                categories[cat]['passing'] += 1
        
        report.append("📊 Category Breakdown:")
        for cat, stats in categories.items():
            pct = stats['passing'] / stats['total'] * 100
            report.append(f"   {cat}: {stats['passing']}/{stats['total']} ({pct:.0f}%)")
        report.append("")
        
        # Failed tests detail
        failed_tests = [r for r in self.results if r['status'] in ['FAILING', 'ERROR']]
        if failed_tests:
            report.append("❌ FAILED TESTS:")
            report.append("-" * 50)
            for test in failed_tests:
                critical_marker = " [CRITICAL]" if test.get('critical') else ""
                report.append(f"\n{test['category']}{critical_marker}")
                report.append(f"Query: {test['query']}")
                report.append(f"Status: {test['status']} (Score: {test['score']:.2f})")
                if test.get('missing_keywords'):
                    report.append(f"Missing Keywords: {', '.join(test['missing_keywords'])}")
                report.append(f"Response: {test['response'][:200]}...")
        
        return "\n".join(report)

def main():
    """Main function"""
    model = "gemini-1.5-flash"  # Default to our preferred model
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["gpt-4", "gpt-3.5-turbo", "gemini-1.5-flash", "gemini-1.5-pro"]:
            model = sys.argv[1]
        elif sys.argv[1] == "--help":
            print("Usage: python test_runner.py [model]")
            print("Models: gpt-4, gpt-3.5-turbo, gemini-1.5-flash, gemini-1.5-pro")
            return
    
    print(f"🧪 Running tests with model: {model}")
    
    try:
        runner = CreditCardTestRunner(model=model)
        results = runner.run_all_tests()
        
        # Generate report
        report = runner.generate_report()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"tests/test_report_{model.replace('.', '_').replace('-', '_')}_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passing = len([r for r in results if r['status'] == 'PASSING'])
        total = len(results)
        critical_tests = [r for r in results if r.get('critical')]
        critical_passing = len([r for r in critical_tests if r['status'] == 'PASSING'])
        
        print(f"✅ Overall: {passing}/{total} tests passing ({passing/total:.1%})")
        print(f"🔴 Critical: {critical_passing}/{len(critical_tests)} passing ({critical_passing/len(critical_tests):.1%})")
        
        # Cost summary
        total_cost = sum(r.get('cost', 0) for r in results)
        print(f"💰 Total cost: ${total_cost:.4f}")
        
        failed_tests = [r for r in results if r['status'] in ['FAILING', 'ERROR']]
        if failed_tests:
            print(f"\n❌ Failed tests:")
            for test in failed_tests:
                critical_marker = " [CRITICAL]" if test.get('critical') else ""
                print(f"   • {test['category']}: {test['query'][:50]}...{critical_marker}")
        
        print(f"\n📄 Detailed report: {report_file}")
        
        # Exit with error code if critical tests failed
        critical_failures = [r for r in critical_tests if r['status'] in ['FAILING', 'ERROR']]
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES DETECTED! Exiting with error code.")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()