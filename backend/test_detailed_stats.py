"""
Test detailed statistics logging functionality
"""

import asyncio
import tempfile
import os
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.append('.')

from services.query_logger import QueryLogger
from logging_models.logging_models import LoggingConfig, QueryLogData, ResponseLogData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_detailed_stats():
    """Test that detailed statistics are properly populated"""
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Initialize logger
        config = LoggingConfig(
            enabled=True,
            db_path=db_path,
            retention_days=90,
            anonymize_after_days=30,
            hash_salt="test-salt-12345",
            gdpr_compliance_mode=True
        )
        
        query_logger = QueryLogger(config)
        
        # Test query 1: Gemini Flash query
        query_data_1 = QueryLogData(
            query_text="What are the welcome benefits for Axis Atlas?",
            enhanced_query="What are the welcome benefits for Axis Atlas credit card?",
            selected_model="gemini-1.5-flash",
            query_mode="Specific Card",
            card_filter="Axis Atlas",
            top_k=7,
            user_ip="192.168.1.100",
            user_agent="Mozilla/5.0 Test Browser"
        )
        
        session_id_1 = await query_logger.log_query(query_data_1)
        logger.info(f"Logged query 1 with session ID: {session_id_1}")
        
        # Log response for query 1
        response_data_1 = ResponseLogData(
            response_status=200,
            execution_time_ms=2500,
            llm_tokens_used=3119,  # Based on user's actual data
            llm_cost=0.0009357,    # Gemini Flash pricing
            search_results_count=5
        )
        
        await query_logger.log_response(session_id_1, response_data_1)
        logger.info("Logged response 1")
        
        # Test query 2: Gemini Pro query (comparison)
        query_data_2 = QueryLogData(
            query_text="Compare cash withdrawal fees between Axis Atlas and ICICI EPM",
            enhanced_query="Compare cash withdrawal fees between Axis Atlas and ICICI EPM credit cards",
            selected_model="gemini-1.5-pro",
            query_mode="General Query",
            card_filter=None,
            top_k=7,
            user_ip="192.168.1.101",
            user_agent="Mozilla/5.0 Test Browser"
        )
        
        session_id_2 = await query_logger.log_query(query_data_2)
        logger.info(f"Logged query 2 with session ID: {session_id_2}")
        
        # Log response for query 2
        response_data_2 = ResponseLogData(
            response_status=200,
            execution_time_ms=4200,
            llm_tokens_used=2847,
            llm_cost=0.014235,  # Gemini Pro pricing
            search_results_count=8
        )
        
        await query_logger.log_response(session_id_2, response_data_2)
        logger.info("Logged response 2")
        
        # Get daily statistics
        stats = await query_logger.get_query_stats(days=1)
        
        if stats:
            stat = stats[0]
            logger.info("=== DAILY STATISTICS ===")
            logger.info(f"Date: {stat.date}")
            logger.info(f"Total queries: {stat.total_queries}")
            logger.info(f"Successful queries: {stat.successful_queries}")
            logger.info(f"Failed queries: {stat.failed_queries}")
            logger.info(f"Gemini Flash queries: {stat.gemini_flash_queries}")
            logger.info(f"Gemini Pro queries: {stat.gemini_pro_queries}")
            logger.info(f"General queries: {stat.general_queries}")
            logger.info(f"Specific card queries: {stat.specific_card_queries}")
            logger.info(f"Comparison queries: {stat.comparison_queries}")
            logger.info(f"Average execution time: {stat.avg_execution_time_ms} ms")
            logger.info(f"Average tokens used: {stat.avg_tokens_used}")
            logger.info(f"Total cost: ${stat.total_cost}")
            
            # Validate detailed stats
            assert stat.total_queries == 2, f"Expected 2 total queries, got {stat.total_queries}"
            assert stat.successful_queries == 2, f"Expected 2 successful queries, got {stat.successful_queries}"
            assert stat.gemini_flash_queries == 1, f"Expected 1 Gemini Flash query, got {stat.gemini_flash_queries}"
            assert stat.gemini_pro_queries == 1, f"Expected 1 Gemini Pro query, got {stat.gemini_pro_queries}"
            assert stat.specific_card_queries == 1, f"Expected 1 specific card query, got {stat.specific_card_queries}"
            assert stat.general_queries == 1, f"Expected 1 general query, got {stat.general_queries}"
            assert stat.comparison_queries == 1, f"Expected 1 comparison query, got {stat.comparison_queries}"
            assert stat.avg_execution_time_ms is not None, "Average execution time should not be None"
            assert stat.avg_tokens_used is not None, "Average tokens used should not be None"
            assert stat.total_cost > 0, f"Total cost should be > 0, got {stat.total_cost}"
            
            logger.info("✅ All detailed statistics are properly populated!")
            return True
        else:
            logger.error("❌ No statistics found!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    success = asyncio.run(test_detailed_stats())
    if success:
        print("\n🎉 Detailed statistics logging test PASSED!")
    else:
        print("\n❌ Detailed statistics logging test FAILED!")
        sys.exit(1)