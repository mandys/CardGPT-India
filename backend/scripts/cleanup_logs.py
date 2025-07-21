"""
Scheduled GDPR compliance cleanup script
Can be run via cron job or scheduled task
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.query_logger import QueryLogger
from models.logging_models import LoggingConfig
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cleanup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main cleanup function"""
    try:
        logger.info("Starting GDPR compliance cleanup...")
        
        # Initialize logging config from environment
        logging_config = LoggingConfig(
            enabled=True,  # Always enabled for cleanup
            db_path=os.getenv("QUERY_LOG_DB_PATH", "logs/query_logs.db"),
            retention_days=int(os.getenv("LOG_RETENTION_DAYS", "90")),
            anonymize_after_days=int(os.getenv("ANONYMIZE_AFTER_DAYS", "30")),
            hash_salt=os.getenv("HASH_SALT_SECRET", "default-salt-change-in-production"),
            gdpr_compliance_mode=True  # Always enabled for cleanup
        )
        
        # Initialize query logger
        query_logger = QueryLogger(logging_config)
        
        # Perform cleanup
        cleanup_result = await query_logger.cleanup_expired_logs()
        
        logger.info(f"Cleanup completed successfully:")
        logger.info(f"  - Deleted logs: {cleanup_result['deleted']}")
        logger.info(f"  - Anonymized logs: {cleanup_result['anonymized']}")
        
        # Get current stats for reporting
        stats = await query_logger.get_query_stats(days=7)
        total_recent_queries = sum(stat.total_queries for stat in stats)
        
        logger.info(f"Current status:")
        logger.info(f"  - Recent queries (7 days): {total_recent_queries}")
        logger.info(f"  - Retention policy: {logging_config.retention_days} days")
        logger.info(f"  - Anonymization: after {logging_config.anonymize_after_days} days")
        
        return 0
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    """
    Usage:
    python scripts/cleanup_logs.py
    
    Environment variables:
    - QUERY_LOG_DB_PATH: Path to SQLite database (default: logs/query_logs.db)
    - LOG_RETENTION_DAYS: Days to retain logs (default: 90)
    - ANONYMIZE_AFTER_DAYS: Days after which to anonymize (default: 30)
    - HASH_SALT_SECRET: Salt for hashing PII (required)
    - GDPR_COMPLIANCE_MODE: Enable GDPR compliance (default: true)
    
    Cron example (daily at 2 AM):
    0 2 * * * cd /path/to/backend && python scripts/cleanup_logs.py >> logs/cleanup.log 2>&1
    """
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)