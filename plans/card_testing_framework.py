#!/usr/bin/env python3
"""
CardGPT Testing Framework
Automated testing framework for validating new credit card additions.

Usage:
    python card_testing_framework.py <card_name> [options]
    
Options:
    --backend-url: Backend API URL (default: http://localhost:8000)
    --output-dir: Test report directory (default: test_reports)
    --compare-cards: Comma-separated list of cards to compare against
    --full-suite: Run comprehensive test suite
    --benchmarks: Include performance benchmarks
    
Example:
    python card_testing_framework.py "HDFC Regalia" --full-suite
    python card_testing_framework.py "Axis Atlas" --compare-cards "HSBC Premier,ICICI EPM"
"""

import json
import logging
import requests
import time
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import argparse
import re
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result"""
    query: str
    response: str
    response_time: float
    status_code: int
    contains_card_name: bool
    response_length: int
    accuracy_score: float
    completeness_score: float
    clarity_score: float
    passed: bool
    issues: List[str]


@dataclass
class TestSuite:
    """Test suite configuration"""
    card_name: str
    test_categories: List[str]
    backend_url: str
    compare_cards: List[str]
    include_benchmarks: bool


@dataclass
class TestReport:
    """Comprehensive test report"""
    card_name: str
    test_date: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_response_time: float
    overall_score: float
    test_results: List[TestResult]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]


class CardTestingFramework:
    """Comprehensive testing framework for credit card data"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url.rstrip('/')
        self.session = requests.Session()
        
        # Standard test queries from schema
        self.test_queries = {
            'basic_information': [
                "What are the annual fees for {card_name}?",
                "What joining fee does {card_name} charge?", 
                "What is the foreign transaction fee for {card_name}?",
                "What are the eligibility criteria for {card_name}?",
                "What is the credit limit for {card_name}?"
            ],
            'rewards_queries': [
                "What rewards do I get with {card_name}?",
                "How much cashback on {card_name}?",
                "Travel rewards rate for {card_name}?",
                "What is the value per point for {card_name}?",
                "Are there any reward caps on {card_name}?"
            ],
            'specific_scenarios': [
                "Cash withdrawal charges {card_name}",
                "Fuel surcharge waiver {card_name}",
                "Welcome bonus {card_name}",
                "Lounge access with {card_name}",
                "Insurance benefits {card_name}",
                "Golf benefits {card_name}",
                "Dining benefits {card_name}"
            ],
            'spending_calculations': [
                "For ₹50,000 spend on {card_name}, how many points will I get?",
                "₹1 lakh hotel spend on {card_name} - calculate rewards",
                "Compare ₹2 lakh annual spend rewards on {card_name}",
                "Monthly ₹25,000 spend on {card_name} - what benefits?",
                "₹5,000 international transaction on {card_name} - total cost?"
            ],
            'policy_questions': [
                "What happens if I don't pay minimum due on {card_name}?",
                "How long is the grace period for {card_name}?",
                "What are the late payment charges for {card_name}?",
                "Can I convert purchases to EMI on {card_name}?",
                "How do I cancel {card_name}?"
            ]
        }
        
        # Comparison query templates
        self.comparison_templates = [
            "Compare {card_name} vs {compare_card}",
            "Which has better rewards {card_name} or {compare_card}?",
            "Annual fee comparison {card_name} vs {compare_card}",
            "Foreign transaction fees {card_name} vs {compare_card}",
            "Lounge access comparison {card_name} vs {compare_card}"
        ]
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time': 10.0,  # seconds
            'min_response_length': 50,   # characters
            'min_accuracy_score': 0.7,
            'min_completeness_score': 0.8,
            'min_clarity_score': 0.7
        }
    
    def test_card(self, test_suite: TestSuite) -> TestReport:
        """Run comprehensive test suite for a card"""
        logger.info(f"🧪 Starting test suite for: {test_suite.card_name}")
        
        test_results = []
        start_time = time.time()
        
        # Test basic backend connectivity
        if not self._check_backend_health():
            logger.error("❌ Backend health check failed")
            return self._create_failed_report(test_suite.card_name, "Backend unavailable")
        
        # Run different test categories
        for category in test_suite.test_categories:
            if category in self.test_queries:
                category_results = self._run_category_tests(
                    test_suite.card_name, 
                    category, 
                    self.test_queries[category]
                )
                test_results.extend(category_results)
        
        # Run comparison tests if specified
        if test_suite.compare_cards:
            comparison_results = self._run_comparison_tests(
                test_suite.card_name,
                test_suite.compare_cards
            )
            test_results.extend(comparison_results)
        
        # Calculate metrics
        total_time = time.time() - start_time
        performance_metrics = self._calculate_performance_metrics(test_results, total_time)
        
        # Generate report
        report = self._generate_test_report(
            test_suite.card_name,
            test_results,
            performance_metrics
        )
        
        logger.info(f"✅ Test suite completed: {report.passed_tests}/{report.total_tests} passed")
        return report
    
    def _check_backend_health(self) -> bool:
        """Check if backend is accessible"""
        try:
            response = self.session.get(f"{self.backend_url}/api/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            return False
    
    def _run_category_tests(self, card_name: str, category: str, queries: List[str]) -> List[TestResult]:
        """Run tests for a specific category"""
        logger.info(f"🔍 Testing category: {category}")
        results = []
        
        for query_template in queries:
            query = query_template.format(card_name=card_name)
            result = self._execute_test_query(query)
            result = self._analyze_response(result, card_name)
            results.append(result)
            
            # Brief pause between queries
            time.sleep(0.5)
        
        passed = sum(1 for r in results if r.passed)
        logger.info(f"  ✅ {category}: {passed}/{len(results)} passed")
        
        return results
    
    def _run_comparison_tests(self, card_name: str, compare_cards: List[str]) -> List[TestResult]:
        """Run comparison tests against other cards"""
        logger.info(f"🔄 Running comparison tests")
        results = []
        
        for compare_card in compare_cards:
            for template in self.comparison_templates:
                query = template.format(card_name=card_name, compare_card=compare_card)
                result = self._execute_test_query(query)
                result = self._analyze_comparison_response(result, card_name, compare_card)
                results.append(result)
                
                time.sleep(0.5)
        
        passed = sum(1 for r in results if r.passed)
        logger.info(f"  ✅ Comparisons: {passed}/{len(results)} passed")
        
        return results
    
    def _execute_test_query(self, query: str) -> TestResult:
        """Execute a single test query"""
        start_time = time.time()
        
        try:
            payload = {
                "message": query,
                "model": "gemini-2.5-flash-lite",
                "stream": False
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get('response', '')
                
                return TestResult(
                    query=query,
                    response=response_text,
                    response_time=response_time,
                    status_code=response.status_code,
                    contains_card_name=False,  # Will be set in analysis
                    response_length=len(response_text),
                    accuracy_score=0.0,
                    completeness_score=0.0,
                    clarity_score=0.0,
                    passed=False,
                    issues=[]
                )
            else:
                return TestResult(
                    query=query,
                    response=f"HTTP {response.status_code}: {response.text}",
                    response_time=response_time,
                    status_code=response.status_code,
                    contains_card_name=False,
                    response_length=0,
                    accuracy_score=0.0,
                    completeness_score=0.0,
                    clarity_score=0.0,
                    passed=False,
                    issues=[f"HTTP error {response.status_code}"]
                )
        
        except Exception as e:
            return TestResult(
                query=query,
                response=f"Error: {str(e)}",
                response_time=time.time() - start_time,
                status_code=0,
                contains_card_name=False,
                response_length=0,
                accuracy_score=0.0,
                completeness_score=0.0,
                clarity_score=0.0,
                passed=False,
                issues=[f"Request failed: {str(e)}"]
            )
    
    def _analyze_response(self, result: TestResult, card_name: str) -> TestResult:
        """Analyze response quality and accuracy"""
        issues = []
        
        # Check if response contains card name
        card_variations = [
            card_name.lower(),
            card_name.replace(' ', '').lower(),
            card_name.replace(' ', '-').lower()
        ]
        
        response_lower = result.response.lower()
        result.contains_card_name = any(var in response_lower for var in card_variations)
        
        if not result.contains_card_name:
            issues.append("Response doesn't mention the queried card")
        
        # Response time check
        if result.response_time > self.thresholds['max_response_time']:
            issues.append(f"Response time too slow: {result.response_time:.2f}s")
        
        # Response length check
        if result.response_length < self.thresholds['min_response_length']:
            issues.append(f"Response too short: {result.response_length} chars")
        
        # Calculate quality scores
        result.accuracy_score = self._calculate_accuracy_score(result, card_name)
        result.completeness_score = self._calculate_completeness_score(result)
        result.clarity_score = self._calculate_clarity_score(result)
        
        # Check quality thresholds
        if result.accuracy_score < self.thresholds['min_accuracy_score']:
            issues.append(f"Low accuracy score: {result.accuracy_score:.2f}")
        
        if result.completeness_score < self.thresholds['min_completeness_score']:
            issues.append(f"Low completeness score: {result.completeness_score:.2f}")
        
        if result.clarity_score < self.thresholds['min_clarity_score']:
            issues.append(f"Low clarity score: {result.clarity_score:.2f}")
        
        # Determine if test passed
        result.passed = (
            result.status_code == 200 and
            result.contains_card_name and
            result.response_time <= self.thresholds['max_response_time'] and
            result.response_length >= self.thresholds['min_response_length'] and
            result.accuracy_score >= self.thresholds['min_accuracy_score'] and
            result.completeness_score >= self.thresholds['min_completeness_score']
        )
        
        result.issues = issues
        return result
    
    def _analyze_comparison_response(self, result: TestResult, card1: str, card2: str) -> TestResult:
        """Analyze comparison response quality"""
        result = self._analyze_response(result, card1)
        
        # Additional checks for comparison queries
        response_lower = result.response.lower()
        card2_variations = [
            card2.lower(),
            card2.replace(' ', '').lower(),
            card2.replace(' ', '-').lower()
        ]
        
        contains_card2 = any(var in response_lower for var in card2_variations)
        
        if not contains_card2:
            result.issues.append(f"Comparison response doesn't mention {card2}")
            result.passed = False
        
        # Check for comparison indicators
        comparison_words = ['compare', 'vs', 'versus', 'better', 'difference', 'both']
        has_comparison = any(word in response_lower for word in comparison_words)
        
        if not has_comparison:
            result.issues.append("Response doesn't seem to be a proper comparison")
            result.completeness_score *= 0.8  # Reduce score
        
        return result
    
    def _calculate_accuracy_score(self, result: TestResult, card_name: str) -> float:
        """Calculate accuracy score based on response content"""
        score = 0.5  # Base score
        
        # Check for card name mention
        if result.contains_card_name:
            score += 0.2
        
        # Check for relevant financial terms
        financial_terms = [
            'fee', 'annual', 'joining', 'reward', 'point', 'cashback',
            'percentage', 'limit', 'eligibility', 'benefit', 'insurance'
        ]
        
        response_lower = result.response.lower()
        relevant_terms = sum(1 for term in financial_terms if term in response_lower)
        score += min(0.3, relevant_terms * 0.05)  # Up to 0.3 bonus
        
        # Check for specific numbers/amounts (indicates detailed information)
        if re.search(r'₹[\d,]+', result.response):
            score += 0.1
        
        if re.search(r'\d+%', result.response):
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_completeness_score(self, result: TestResult) -> float:
        """Calculate completeness score based on response comprehensiveness"""
        # Base score from response length
        length_score = min(1.0, result.response_length / 200)  # 200 chars = full score
        
        # Check for comprehensive coverage
        coverage_indicators = [
            'details', 'conditions', 'terms', 'applicable', 'subject to',
            'valid', 'excluding', 'including', 'minimum', 'maximum'
        ]
        
        response_lower = result.response.lower()
        coverage_count = sum(1 for indicator in coverage_indicators if indicator in response_lower)
        coverage_score = min(0.4, coverage_count * 0.08)  # Up to 0.4 bonus
        
        return min(1.0, length_score * 0.6 + coverage_score + 0.2)
    
    def _calculate_clarity_score(self, result: TestResult) -> float:
        """Calculate clarity score based on response readability"""
        text = result.response
        
        if not text.strip():
            return 0.0
        
        # Check sentence structure
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # Optimal sentence length is around 15-20 words
        sentence_score = 1.0 - abs(avg_sentence_length - 17.5) / 25
        sentence_score = max(0.0, sentence_score)
        
        # Check for clear structure indicators
        structure_indicators = ['first', 'second', 'additionally', 'however', 'therefore', 'specifically']
        structure_score = min(0.3, sum(1 for ind in structure_indicators if ind.lower() in text.lower()) * 0.1)
        
        # Penalize for confusion indicators
        confusion_indicators = ['unclear', 'not sure', 'might be', 'possibly', 'information not available']
        confusion_penalty = min(0.5, sum(1 for ind in confusion_indicators if ind.lower() in text.lower()) * 0.2)
        
        return max(0.0, sentence_score * 0.7 + structure_score - confusion_penalty + 0.3)
    
    def _calculate_performance_metrics(self, results: List[TestResult], total_time: float) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        if not results:
            return {}
        
        response_times = [r.response_time for r in results if r.response_time > 0]
        
        return {
            'total_execution_time': total_time,
            'average_response_time': statistics.mean(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'success_rate': sum(1 for r in results if r.status_code == 200) / len(results),
            'average_accuracy': statistics.mean([r.accuracy_score for r in results]),
            'average_completeness': statistics.mean([r.completeness_score for r in results]),
            'average_clarity': statistics.mean([r.clarity_score for r in results])
        }
    
    def _generate_test_report(self, card_name: str, results: List[TestResult], 
                            metrics: Dict[str, Any]) -> TestReport:
        """Generate comprehensive test report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Calculate overall score
        if total_tests > 0:
            overall_score = (
                (passed_tests / total_tests) * 0.4 +
                metrics.get('average_accuracy', 0) * 0.2 +
                metrics.get('average_completeness', 0) * 0.2 +
                metrics.get('average_clarity', 0) * 0.2
            )
        else:
            overall_score = 0.0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results, metrics)
        
        return TestReport(
            card_name=card_name,
            test_date=datetime.now().isoformat(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            average_response_time=metrics.get('average_response_time', 0),
            overall_score=overall_score,
            test_results=results,
            performance_metrics=metrics,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, results: List[TestResult], 
                                metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Performance recommendations
        if metrics.get('average_response_time', 0) > 5:
            recommendations.append("Consider optimizing backend performance - average response time is slow")
        
        # Accuracy recommendations
        if metrics.get('average_accuracy', 0) < 0.8:
            recommendations.append("Improve card data accuracy - responses may be missing key information")
        
        # Completeness recommendations  
        if metrics.get('average_completeness', 0) < 0.8:
            recommendations.append("Enhance data completeness - responses lack comprehensive details")
        
        # Specific issue recommendations
        common_issues = {}
        for result in results:
            for issue in result.issues:
                common_issues[issue] = common_issues.get(issue, 0) + 1
        
        # Report most common issues
        for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:3]:
            if count > len(results) * 0.2:  # If issue affects > 20% of tests
                recommendations.append(f"Address common issue: {issue} (affects {count} tests)")
        
        return recommendations
    
    def _create_failed_report(self, card_name: str, reason: str) -> TestReport:
        """Create a failed test report"""
        return TestReport(
            card_name=card_name,
            test_date=datetime.now().isoformat(),
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            average_response_time=0,
            overall_score=0,
            test_results=[],
            performance_metrics={},
            recommendations=[f"Fix critical issue: {reason}"]
        )
    
    def save_report(self, report: TestReport, output_dir: Path) -> Path:
        """Save test report to file"""
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        safe_card_name = re.sub(r'[^\w\-_]', '_', report.card_name.lower())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{safe_card_name}_{timestamp}.json"
        
        report_file = output_dir / filename
        
        # Convert to dict and save
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)
        
        # Also create a markdown summary
        md_file = report_file.with_suffix('.md')
        self._create_markdown_report(report, md_file)
        
        logger.info(f"📄 Test report saved: {report_file}")
        logger.info(f"📄 Summary report: {md_file}")
        
        return report_file
    
    def _create_markdown_report(self, report: TestReport, output_file: Path) -> None:
        """Create markdown summary report"""
        content = f"""# Test Report: {report.card_name}

## Summary
- **Test Date**: {report.test_date}
- **Overall Score**: {report.overall_score:.1%}
- **Tests Passed**: {report.passed_tests}/{report.total_tests}
- **Average Response Time**: {report.average_response_time:.2f}s

## Performance Metrics
- **Success Rate**: {report.performance_metrics.get('success_rate', 0):.1%}
- **Average Accuracy**: {report.performance_metrics.get('average_accuracy', 0):.2f}
- **Average Completeness**: {report.performance_metrics.get('average_completeness', 0):.2f}
- **Average Clarity**: {report.performance_metrics.get('average_clarity', 0):.2f}

## Test Results Summary
"""
        
        # Group results by pass/fail
        passed_tests = [r for r in report.test_results if r.passed]
        failed_tests = [r for r in report.test_results if not r.passed]
        
        if passed_tests:
            content += f"\n### ✅ Passed Tests ({len(passed_tests)})\n"
            for test in passed_tests[:5]:  # Show first 5
                content += f"- {test.query} ({test.response_time:.2f}s)\n"
            if len(passed_tests) > 5:
                content += f"- ... and {len(passed_tests) - 5} more\n"
        
        if failed_tests:
            content += f"\n### ❌ Failed Tests ({len(failed_tests)})\n"
            for test in failed_tests:
                content += f"- **{test.query}**\n"
                for issue in test.issues:
                    content += f"  - {issue}\n"
        
        if report.recommendations:
            content += "\n## Recommendations\n"
            for rec in report.recommendations:
                content += f"- {rec}\n"
        
        content += f"\n---\nGenerated by CardGPT Testing Framework"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """CLI interface for testing framework"""
    parser = argparse.ArgumentParser(
        description="CardGPT Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python card_testing_framework.py "HDFC Regalia" --full-suite
  python card_testing_framework.py "Axis Atlas" --compare-cards "HSBC Premier,ICICI EPM"
  python card_testing_framework.py "SBI Cashback" --backend-url http://localhost:8000
        """
    )
    
    parser.add_argument('card_name', help='Name of the card to test')
    parser.add_argument('--backend-url', default='http://localhost:8000',
                       help='Backend API URL')
    parser.add_argument('--output-dir', default='test_reports',
                       help='Output directory for reports')
    parser.add_argument('--compare-cards', 
                       help='Comma-separated list of cards to compare against')
    parser.add_argument('--full-suite', action='store_true',
                       help='Run comprehensive test suite')
    parser.add_argument('--benchmarks', action='store_true',
                       help='Include performance benchmarks')
    
    args = parser.parse_args()
    
    # Prepare test suite
    test_categories = ['basic_information', 'rewards_queries'] 
    
    if args.full_suite:
        test_categories.extend([
            'specific_scenarios', 
            'spending_calculations', 
            'policy_questions'
        ])
    
    compare_cards = []
    if args.compare_cards:
        compare_cards = [card.strip() for card in args.compare_cards.split(',')]
    
    test_suite = TestSuite(
        card_name=args.card_name,
        test_categories=test_categories,
        backend_url=args.backend_url,
        compare_cards=compare_cards,
        include_benchmarks=args.benchmarks
    )
    
    # Run tests
    framework = CardTestingFramework(args.backend_url)
    report = framework.test_card(test_suite)
    
    # Save report
    output_dir = Path(args.output_dir)
    report_file = framework.save_report(report, output_dir)
    
    # Print summary
    print(f"\n📊 Test Results for {args.card_name}:")
    print(f"   Overall Score: {report.overall_score:.1%}")
    print(f"   Tests Passed: {report.passed_tests}/{report.total_tests}")
    print(f"   Average Response Time: {report.average_response_time:.2f}s")
    
    if report.failed_tests > 0:
        print(f"   ⚠️  {report.failed_tests} tests failed")
        
    if report.recommendations:
        print("\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"   - {rec}")
    
    print(f"\n📄 Full report: {report_file}")
    
    # Exit with appropriate code
    success_rate = report.passed_tests / max(report.total_tests, 1)
    if success_rate >= 0.8 and report.overall_score >= 0.75:
        print("✅ Testing completed successfully!")
        return 0
    else:
        print("❌ Testing identified issues that need attention")
        return 1


if __name__ == "__main__":
    exit(main())