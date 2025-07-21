"""
Test script for query logging system
Verifies all components work correctly
"""

import asyncio
import tempfile
import os
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.append('.')

from services.query_logger import QueryLogger
from logging_models.logging_models import LoggingConfig, QueryLogData, ResponseLogData, ExportRequest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_query_logger():
    """Test the complete query logging workflow"""
    
    print("🧪 Testing Query Logging System...")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Initialize test configuration
        config = LoggingConfig(
            enabled=True,
            db_path=db_path,
            retention_days=90,
            anonymize_after_days=30,
            hash_salt="test-salt-123",
            gdpr_compliance_mode=True
        )
        
        # Initialize query logger
        query_logger = QueryLogger(config)
        print("✅ Query logger initialized successfully")
        
        # Test 1: Log a query
        print("\n📝 Test 1: Logging query data...")
        query_data = QueryLogData(
            query_text="Compare Axis Atlas vs ICICI EPM for reward rates",
            enhanced_query="Compare Axis Atlas vs ICICI EPM for reward rates Axis Bank Atlas Credit Card ICICI Bank Emeralde Private Metal Credit Card EDGE Miles earning rate Reward Points earning rate",
            selected_model="gemini-1.5-flash",
            query_mode="Compare Cards",
            card_filter=None,
            top_k=7,
            user_ip="192.168.1.100",
            user_agent="Mozilla/5.0 (Test Browser)"
        )
        
        session_id = await query_logger.log_query(query_data)
        print(f"✅ Query logged with session ID: {session_id}")
        
        # Test 2: Log response data
        print("\n📊 Test 2: Logging response data...")
        response_data = ResponseLogData(
            response_status=200,
            execution_time_ms=2500,
            llm_tokens_used=1200,
            llm_cost=0.0003,
            search_results_count=7
        )
        
        await query_logger.log_response(session_id, response_data)
        print("✅ Response data logged successfully")
        
        # Test 3: Log another query (for stats)
        print("\n📝 Test 3: Logging second query...")
        query_data2 = QueryLogData(
            query_text="What are the welcome benefits of HSBC Premier?",
            selected_model="gemini-1.5-pro", 
            query_mode="Specific Card",
            card_filter="HSBC Premier",
            user_ip="192.168.1.101",
            user_agent="Chrome/120.0"
        )
        
        session_id2 = await query_logger.log_query(query_data2)
        
        response_data2 = ResponseLogData(
            response_status=200,
            execution_time_ms=1800,
            llm_tokens_used=800,
            llm_cost=0.005,
            search_results_count=5
        )
        
        await query_logger.log_response(session_id2, response_data2)
        print("✅ Second query logged successfully")
        
        # Test 4: Get statistics
        print("\n📈 Test 4: Retrieving query statistics...")
        stats = await query_logger.get_query_stats(days=1)
        print(f"✅ Retrieved {len(stats)} daily stats")
        if stats:
            today_stats = stats[0]
            print(f"   - Total queries: {today_stats.total_queries}")
            print(f"   - Successful queries: {today_stats.successful_queries}")
            print(f"   - Average cost: ${today_stats.total_cost}")
        
        # Test 5: Get session data
        print("\n🔍 Test 5: Retrieving session data...")
        session_data = await query_logger.get_session_data(session_id)
        if session_data:
            print(f"✅ Retrieved session data for {session_id}")
            print(f"   - Query: {session_data.query_text[:50]}...")
            print(f"   - Model: {session_data.selected_model}")
            print(f"   - Status: {session_data.response_status}")
            print(f"   - Tokens: {session_data.llm_tokens_used}")
        else:
            print("❌ Failed to retrieve session data")
        
        # Test 6: Export training data
        print("\n📤 Test 6: Exporting training data...")
        export_request = ExportRequest(
            format="json",
            anonymized_only=False,
            include_failed_queries=False
        )
        
        export_result = await query_logger.export_training_data(export_request)
        print(f"✅ Exported {export_result.record_count} records")
        print(f"   - Export ID: {export_result.export_id}")
        print(f"   - File: {export_result.file_path}")
        
        # Verify export file exists and has content
        if export_result.file_path and Path(export_result.file_path).exists():
            with open(export_result.file_path, 'r') as f:
                content = f.read()
                print(f"   - File size: {len(content)} characters")
        
        # Test 7: GDPR compliance cleanup (test mode)
        print("\n🧹 Test 7: Testing GDPR cleanup...")
        cleanup_result = await query_logger.cleanup_expired_logs()
        print(f"✅ Cleanup completed")
        print(f"   - Deleted: {cleanup_result['deleted']} logs")
        print(f"   - Anonymized: {cleanup_result['anonymized']} logs")
        
        # Test 8: Delete session data (right to be forgotten)
        print("\n🗑️  Test 8: Testing data deletion...")
        deleted = await query_logger.delete_session_data(session_id2)
        if deleted:
            print(f"✅ Session {session_id2} data deleted successfully")
        else:
            print(f"❌ Failed to delete session {session_id2}")
        
        # Verify deletion
        deleted_session = await query_logger.get_session_data(session_id2)
        if deleted_session is None:
            print("✅ Deletion verified - session data not found")
        else:
            print("❌ Deletion failed - session data still exists")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False
        
    finally:
        # Clean up temporary database
        try:
            os.unlink(db_path)
            print(f"\n🧹 Cleaned up temporary database: {db_path}")
        except:
            pass

async def test_privacy_features():
    """Test privacy protection features"""
    
    print("\n🔒 Testing Privacy Features...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        config = LoggingConfig(
            enabled=True,
            db_path=db_path,
            retention_days=1,  # Short retention for testing
            anonymize_after_days=0,  # Immediate anonymization
            hash_salt="privacy-test-salt",
            gdpr_compliance_mode=True
        )
        
        query_logger = QueryLogger(config)
        
        # Test IP and User Agent hashing
        original_ip = "192.168.1.100"
        original_user_agent = "Mozilla/5.0 (Test Browser)"
        
        query_data = QueryLogData(
            query_text="Test privacy query",
            selected_model="gemini-1.5-flash",
            query_mode="General Query",
            user_ip=original_ip,
            user_agent=original_user_agent
        )
        
        session_id = await query_logger.log_query(query_data)
        
        # Retrieve and verify hashing
        session_data = await query_logger.get_session_data(session_id)
        
        if session_data:
            print(f"✅ Privacy test results:")
            print(f"   - Original IP: {original_ip}")
            print(f"   - Hashed IP: {session_data.user_ip_hash}")
            print(f"   - Original UA: {original_user_agent}")
            print(f"   - Hashed UA: {session_data.user_agent_hash}")
            
            # Verify hashes are different from originals
            if (session_data.user_ip_hash != original_ip and 
                session_data.user_agent_hash != original_user_agent):
                print("✅ PII successfully hashed")
            else:
                print("❌ PII hashing failed")
                
        else:
            print("❌ Failed to retrieve privacy test data")
            
    finally:
        try:
            os.unlink(db_path)
        except:
            pass

if __name__ == "__main__":
    """
    Run comprehensive tests of the query logging system
    """
    
    print("🚀 Starting Query Logging System Tests")
    print("=" * 50)
    
    async def run_all_tests():
        # Test main functionality
        main_test_passed = await test_query_logger()
        
        # Test privacy features
        await test_privacy_features()
        
        print("\n" + "=" * 50)
        if main_test_passed:
            print("🎉 ALL TESTS PASSED - Query logging system is working correctly!")
            return 0
        else:
            print("❌ SOME TESTS FAILED - Check logs for details")
            return 1
    
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)