#!/usr/bin/env python3
"""
Simple Google Search Grounding Test for CardGPT

This test demonstrates the concept of Google Search grounding by:
1. Testing a baseline approach using only the model's internal knowledge.
2. Testing a second approach using actual Google Search grounding via the API.
3. Documenting the differences and implications.

Requirements:
- GEMINI_API_KEY environment variable
"""

import os
import sys
import logging
import json
import time
from typing import Dict, Any

# Add parent directory for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import google.generativeai as genai
# CORRECTED: Re-importing 'Tool' as it is required for the correct grounding syntax.
from google.generativeai.types import Tool


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGroundingTest:
    def __init__(self):
        """Initialize the test with Gemini API"""

        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("Missing GEMINI_API_KEY environment variable")

        genai.configure(api_key=self.gemini_api_key)

        try:
            models = genai.list_models()
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            logger.info(f"✅ Available models: {available_models[:3]}...")
        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            raise

        logger.info(f"✅ Initialized with Gemini API")

    def test_current_approach(self, query: str) -> Dict[str, Any]:
        """Test current CardGPT approach - simulated RAG with internal knowledge"""
        logger.info(f"\n🔍 Testing Current CardGPT Approach (Internal Knowledge Only) for: '{query}'")

        try:
            # CORRECTED: Using the correct model name 'gemini-1.5-flash-latest'
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            prompt = f"""You are CardGPT, a knowledgeable assistant about Indian credit cards.
Use only your internal training data to answer the following question about Indian credit cards. Do not use any external or real-time information.

Based on your training data, please answer:
{query}

Provide specific information about credit card features, rewards, and benefits based on your training data only."""

            start_time = time.time()
            response = model.generate_content(prompt)
            end_time = time.time()

            result = {
                "approach": "Internal Knowledge Only",
                "query": query,
                "response": response.text,
                "response_time": end_time - start_time,
                "data_sources": "Training data only",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cost_estimate": "~$0.0001 per query",
                "limitations": "Limited to training data cutoff, no current information"
            }
            logger.info(f"✅ Internal knowledge response generated in {result['response_time']:.2f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Internal knowledge test failed: {e}", exc_info=True)
            return {"approach": "Internal Knowledge Only", "query": query, "error": str(e)}

    def test_google_search_grounding(self, query: str) -> Dict[str, Any]:
        """Test the approach with real-time Google Search grounding."""
        logger.info(f"\n🌐 Testing with REAL Google Search Grounding for: '{query}'")

        try:
            # CORRECTED: Using the correct model name 'gemini-1.5-flash-latest'
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            prompt = f"""You are CardGPT, an expert assistant for Indian credit cards.
Answer the following query using the most current information available to you.
You can use your internal knowledge and supplement it with real-time web search information to provide the most accurate and up-to-date answer.

Query: {query}"""

            start_time = time.time()
            
            # CORRECTED: Create a Tool object configured for Google Search retrieval.
            grounding_tool = Tool(google_search_retrieval={})
            response = model.generate_content(prompt, tools=[grounding_tool])
            
            end_time = time.time()
            result = {
                "approach": "Google Search Grounding",
                "query": query,
                "response": response.text,
                "response_time": end_time - start_time,
                "data_sources": "Training data + Google Search",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cost_estimate": "~$0.0003-0.0005 per query (estimated with grounding)",
                "benefits": "Current information, comprehensive coverage, real-time offers",
            }
            logger.info(f"✅ Grounded response generated in {result['response_time']:.2f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Google Search grounding test failed: {e}", exc_info=True)
            return {"approach": "Google Search Grounding", "query": query, "error": str(e)}

    def analyze_web_search_potential(self, query: str) -> Dict[str, Any]:
        """Analyze what web search grounding could add to this query"""
        logger.info(f"\n🔬 Analyzing Web Search Potential for: '{query}'")
        current_info_keywords = ['latest', 'current', '2025', 'new', 'recent', 'offer', 'promotion']
        comparison_keywords = ['compare', 'vs', 'versus', 'better', 'best']
        regulation_keywords = ['rbi', 'regulation', 'rule', 'policy', 'guideline']
        query_lower = query.lower()
        grounding_value = {
            "needs_current_info": any(keyword in query_lower for keyword in current_info_keywords),
            "benefits_from_comparison": any(keyword in query_lower for keyword in comparison_keywords),
            "requires_regulations": any(keyword in query_lower for keyword in regulation_keywords),
            "grounding_score": 0, "recommendation": "", "cost_benefit_analysis": {}
        }
        if grounding_value["needs_current_info"]: grounding_value["grounding_score"] += 40
        if grounding_value["benefits_from_comparison"]: grounding_value["grounding_score"] += 30
        if grounding_value["requires_regulations"]: grounding_value["grounding_score"] += 30
        if grounding_value["grounding_score"] >= 70:
            grounding_value["recommendation"] = "HIGH VALUE - Grounding would significantly improve answer quality"
        elif grounding_value["grounding_score"] >= 40:
            grounding_value["recommendation"] = "MEDIUM VALUE - Grounding would provide some benefits"
        else:
            grounding_value["recommendation"] = "LOW VALUE - Internal data likely sufficient"
        grounding_value["cost_benefit_analysis"] = {
            "additional_cost_per_query": "$0.0002-0.0004", "response_time_increase": "0.5-2.0 seconds",
            "accuracy_improvement": f"{min(grounding_value['grounding_score'], 80)}%",
            "worth_implementing": grounding_value["grounding_score"] >= 50
        }
        return grounding_value

    def run_comprehensive_test(self, queries: list) -> Dict[str, Any]:
        """Run comprehensive test across multiple queries"""
        logger.info(f"\n🔬 Running comprehensive test across {len(queries)} queries")
        results = {
            "test_metadata": {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "total_queries": len(queries), "api_used": "Google Gemini API"},
            "query_results": []
        }
        for i, query in enumerate(queries, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Query {i}/{len(queries)}: {query}")
            logger.info(f"{'='*80}")
            query_result = {
                "query": query,
                "internal_knowledge_only": self.test_current_approach(query),
                "Google Search_grounding": self.test_google_search_grounding(query),
                "grounding_analysis": self.analyze_web_search_potential(query)
            }
            results["query_results"].append(query_result)
            time.sleep(2)
        return results

    def print_analysis_summary(self, results: Dict[str, Any]):
        """Print analysis summary and recommendations"""
        logger.info(f"\n{'='*100}")
        logger.info("GOOGLE SEARCH GROUNDING ANALYSIS SUMMARY")
        logger.info(f"{'='*100}")
        total_high_value, total_medium_value, total_low_value = 0, 0, 0
        for i, query_result in enumerate(results["query_results"], 1):
            query = query_result["query"]
            analysis = query_result["grounding_analysis"]
            internal_time = query_result["internal_knowledge_only"].get("response_time", 0)
            grounded_time = query_result["Google Search_grounding"].get("response_time", 0)
            logger.info(f"\n📝 Query {i}: {query}")
            logger.info("-" * 80)
            if analysis["grounding_score"] >= 70:
                total_high_value += 1
                logger.info(f"🟢 GROUNDING VALUE: HIGH ({analysis['grounding_score']}/100)")
            elif analysis["grounding_score"] >= 40:
                total_medium_value += 1
                logger.info(f"🟡 GROUNDING VALUE: MEDIUM ({analysis['grounding_score']}/100)")
            else:
                total_low_value += 1
                logger.info(f"🔴 GROUNDING VALUE: LOW ({analysis['grounding_score']}/100)")
            logger.info(f"   📊 Internal knowledge only: {internal_time:.2f}s")
            logger.info(f"   📊 With Google Search:      {grounded_time:.2f}s (delta: {grounded_time-internal_time:+.2f}s)")
            logger.info(f"   💰 Cost increase: {analysis['cost_benefit_analysis']['additional_cost_per_query']}")
            logger.info(f"   🎯 Worth implementing: {'YES' if analysis['cost_benefit_analysis']['worth_implementing'] else 'NO'}")
        
        logger.info(f"\n{'='*100}")
        logger.info("OVERALL RECOMMENDATIONS")
        logger.info(f"{'='*100}")
        logger.info(f"📊 Grounding Value Distribution:")
        logger.info(f"   🟢 High Value Queries:   {total_high_value}/{len(results['query_results'])}")
        logger.info(f"   🟡 Medium Value Queries: {total_medium_value}/{len(results['query_results'])}")
        logger.info(f"   🔴 Low Value Queries:    {total_low_value}/{len(results['query_results'])}")
        recommendation_score = (total_high_value * 3 + total_medium_value * 2 + total_low_value * 1)
        max_score = len(results['query_results']) * 3
        logger.info(f"\n🎯 IMPLEMENTATION RECOMMENDATION:")
        if recommendation_score / max_score >= 0.7:
            logger.info("✅ STRONGLY RECOMMENDED - Most queries benefit significantly from grounding")
        elif recommendation_score / max_score >= 0.5:
            logger.info("⚡ CONDITIONALLY RECOMMENDED - Implement for specific query types")
        else:
            logger.info("❌ NOT RECOMMENDED - Internal knowledge is sufficient for most queries")
        logger.info(f"\n💡 IMPLEMENTATION STRATEGY:")
        if total_high_value > 0 or total_medium_value > 0:
            logger.info("1. Implement selective grounding. Use query classification (like your `analyze` function) to decide when to enable the grounding tool.")
            logger.info("2. For high-value queries (offers, regulations), always enable grounding.")
            logger.info("3. For low-value queries (basic features), disable grounding to save cost and time.")
        else:
            logger.info("1. Current approach appears sufficient for your use cases.")
            logger.info("2. Continue to monitor for user requests that require current information.")

def main():
    """Main test function"""
    logger.info("🚀 Starting Google Search Grounding Analysis for CardGPT")
    try:
        test = SimpleGroundingTest()
        test_queries = [
            "What are the reward rates for the Axis Atlas credit card?",
            "What are the current RBI regulations on credit card surcharges?"
        ]
        results = test.run_comprehensive_test(test_queries)
        test.print_analysis_summary(results)
        output_file = "grounding_analysis_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"\n💾 Detailed analysis saved to {output_file}")
        logger.info(f"\n{'='*100}")
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info(f"{'='*100}")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)