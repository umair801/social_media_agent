#!/usr/bin/env python3
"""
Run Engagement Agent
Monitors and responds to social media interactions
"""

import os
import sys
import argparse
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.engagement_handler import EngagementAgent
import yaml


def setup_logging(log_file: str = "logs/engagement.log"):
    """Setup logging configuration"""
    os.makedirs("logs", exist_ok=True)
    
    logger.add(
        log_file,
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    logger.info("="* 60)
    logger.info("Starting Engagement Agent")
    logger.info("="* 60)


def load_config(config_path: str) -> dict:
    """Load brand configuration"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Social Media Engagement Agent")
    parser.add_argument(
        '--config',
        type=str,
        default='config/brand_profiles.yaml',
        help='Path to brand configuration file'
    )
    parser.add_argument(
        '--platforms',
        type=str,
        nargs='+',
        default=['instagram', 'linkedin', 'twitter', 'facebook'],
        help='Platforms to monitor (space-separated)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Check interval in seconds (default: 300 = 5 minutes)'
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode (process sample comments only)'
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_logging()
    load_dotenv()
    
    # Load configuration
    try:
        brand_config = load_config(args.config)
        logger.info(f"Loaded configuration for: {brand_config['brand_name']}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        sys.exit(1)
    
    # Initialize engagement agent
    try:
        agent = EngagementAgent(brand_config)
        logger.success("Engagement agent initialized")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        sys.exit(1)
    
    # Test mode
    if args.test_mode:
        logger.info("Running in TEST MODE")
        test_comments = [
            {
                'comment': "Love this post! Very helpful insights.",
                'user_name': "Sarah Johnson",
                'platform': "instagram",
                'post_id': "test_123"
            },
            {
                'comment': "How can I integrate this with my existing workflow?",
                'user_name': "John Smith",
                'platform': "linkedin",
                'post_id': "test_456"
            },
            {
                'comment': "This product is terrible! I want my money back NOW!",
                'user_name': "Mike Davis",
                'platform': "twitter",
                'post_id': "test_789"
            }
        ]
        
        for comment_data in test_comments:
            logger.info(f"\n{'='*60}")
            result = agent.process_comment(**comment_data)
            
            print(f"\nUser: {result['user_name']}")
            print(f"Platform: {result['platform']}")
            print(f"Comment: {result['comment']}")
            print(f"Classification: {result['classification']}")
            print(f"Response: {result['response']}")
            print(f"Escalated: {result['escalated']}")
        
        logger.info("\nTest mode completed")
        return
    
    # Production mode
    logger.info(f"Monitoring platforms: {', '.join(args.platforms)}")
    logger.info(f"Check interval: {args.interval} seconds")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        agent.start_monitoring(platforms=args.platforms)
    except KeyboardInterrupt:
        logger.info("\n\nStopping engagement monitoring...")
        logger.success("Engagement agent stopped gracefully")
    except Exception as e:
        logger.error(f"Error running engagement agent: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
