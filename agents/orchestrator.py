"""
Main Orchestrator for Social Media Agent System
Coordinates all agents and manages workflow
"""

import os
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from agents.content_creator import ContentCreatorAgent
from agents.scheduler import SchedulerAgent
from agents.engagement_handler import EngagementAgent
from agents.analytics import AnalyticsAgent
from tools.brand_voice_checker import BrandVoiceValidator
from tools.platform_apis import PlatformManager


class SocialMediaOrchestrator:
    """
    Main orchestrator that coordinates all social media agents
    """
    
    def __init__(self, brand_config_path: str):
        """
        Initialize orchestrator with brand configuration
        
        Args:
            brand_config_path: Path to brand configuration YAML file
        """
        logger.info("Initializing Social Media Orchestrator")
        
        # Load brand configuration
        with open(brand_config_path, 'r') as f:
            self.brand_config = yaml.safe_load(f)
        
        # Initialize agents
        self.content_creator = ContentCreatorAgent(self.brand_config)
        self.scheduler = SchedulerAgent(self.brand_config)
        self.engagement_handler = EngagementAgent(self.brand_config)
        self.analytics = AnalyticsAgent(self.brand_config)
        
        # Initialize tools
        self.brand_validator = BrandVoiceValidator(self.brand_config)
        self.platform_manager = PlatformManager()
        
        logger.success("Orchestrator initialized successfully")
    
    def generate_content_calendar(
        self,
        days: int = 30,
        platforms: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate complete content calendar for specified days
        
        Args:
            days: Number of days to generate content for
            platforms: List of platforms (default: all configured platforms)
        
        Returns:
            Dictionary containing content calendar
        """
        logger.info(f"Generating {days}-day content calendar")
        
        if platforms is None:
            platforms = self.brand_config.get('target_audience', {}).get('platforms', [])
        
        calendar = {
            'generated_at': datetime.now().isoformat(),
            'duration_days': days,
            'platforms': platforms,
            'posts': []
        }
        
        # Generate posts for each day
        for day_offset in range(days):
            target_date = datetime.now() + timedelta(days=day_offset)
            
            # Generate platform-specific content
            for platform in platforms:
                daily_posts = self._generate_daily_posts(platform, target_date)
                
                # Validate brand voice
                for post in daily_posts:
                    if self.brand_validator.validate(post['content']):
                        calendar['posts'].append(post)
                    else:
                        logger.warning(f"Post failed brand voice validation: {post['content'][:50]}...")
                        # Regenerate or skip
                        continue
        
        logger.success(f"Generated {len(calendar['posts'])} posts")
        return calendar
    
    def _generate_daily_posts(self, platform: str, date: datetime) -> List[Dict]:
        """
        Generate posts for a specific platform and date
        
        Args:
            platform: Social media platform
            date: Target date for posts
        
        Returns:
            List of post dictionaries
        """
        # Platform-specific posting frequency
        posts_per_day = {
            'instagram': 2,  # 1 feed + 1 story/reel
            'linkedin': 1,
            'twitter': 3,
            'facebook': 1
        }
        
        count = posts_per_day.get(platform.lower(), 1)
        
        posts = self.content_creator.create_posts(
            platform=platform,
            count=count,
            target_date=date
        )
        
        return posts
    
    def schedule_all_posts(self, content_calendar: Dict) -> Dict:
        """
        Schedule all posts in the content calendar
        
        Args:
            content_calendar: Generated content calendar
        
        Returns:
            Scheduling results
        """
        logger.info("Scheduling all posts")
        
        results = {
            'scheduled': [],
            'failed': [],
            'total': len(content_calendar['posts'])
        }
        
        for post in content_calendar['posts']:
            try:
                # Determine optimal posting time
                optimal_time = self.scheduler.get_optimal_time(
                    platform=post['platform'],
                    date=post['scheduled_date']
                )
                
                # Schedule via platform API
                scheduled = self.platform_manager.schedule_post(
                    platform=post['platform'],
                    content=post['content'],
                    media=post.get('media'),
                    scheduled_time=optimal_time
                )
                
                if scheduled:
                    results['scheduled'].append({
                        'post_id': scheduled['id'],
                        'platform': post['platform'],
                        'time': optimal_time
                    })
                    logger.info(f"Scheduled {post['platform']} post for {optimal_time}")
                else:
                    results['failed'].append(post)
                    logger.error(f"Failed to schedule post: {post['content'][:50]}...")
                    
            except Exception as e:
                logger.error(f"Error scheduling post: {str(e)}")
                results['failed'].append(post)
        
        logger.success(f"Scheduled {len(results['scheduled'])} posts, {len(results['failed'])} failed")
        return results
    
    def run_engagement_monitoring(self, platforms: Optional[List[str]] = None):
        """
        Start engagement monitoring and auto-response
        
        Args:
            platforms: List of platforms to monitor (default: all)
        """
        logger.info("Starting engagement monitoring")
        
        if platforms is None:
            platforms = self.brand_config.get('target_audience', {}).get('platforms', [])
        
        self.engagement_handler.start_monitoring(platforms)
    
    def generate_performance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        platforms: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate comprehensive performance report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            platforms: Platforms to include (default: all)
        
        Returns:
            Performance report dictionary
        """
        logger.info(f"Generating performance report: {start_date} to {end_date}")
        
        if platforms is None:
            platforms = self.brand_config.get('target_audience', {}).get('platforms', [])
        
        report = self.analytics.generate_report(
            start_date=start_date,
            end_date=end_date,
            platforms=platforms
        )
        
        return report
    
    def run_ab_test(
        self,
        post_a: Dict,
        post_b: Dict,
        duration_hours: int = 24
    ) -> Dict:
        """
        Run A/B test on two post variations
        
        Args:
            post_a: First post variation
            post_b: Second post variation
            duration_hours: Test duration in hours
        
        Returns:
            Test results
        """
        logger.info(f"Starting A/B test for {duration_hours} hours")
        
        # Schedule both posts
        result_a = self.platform_manager.schedule_post(**post_a)
        result_b = self.platform_manager.schedule_post(**post_b)
        
        # Track performance
        test_results = self.analytics.track_ab_test(
            post_a_id=result_a['id'],
            post_b_id=result_b['id'],
            duration_hours=duration_hours
        )
        
        logger.success(f"A/B test complete: Winner is {'A' if test_results['winner'] == 'a' else 'B'}")
        return test_results
    
    def optimize_posting_schedule(self, historical_days: int = 30) -> Dict:
        """
        Analyze past performance and optimize posting schedule
        
        Args:
            historical_days: Days of historical data to analyze
        
        Returns:
            Optimized schedule recommendations
        """
        logger.info(f"Optimizing schedule based on {historical_days} days of data")
        
        optimized = self.scheduler.optimize_schedule(
            historical_days=historical_days
        )
        
        return optimized


if __name__ == "__main__":
    # Example usage
    orchestrator = SocialMediaOrchestrator("config/brand_profiles.yaml")
    
    # Generate 30-day content calendar
    calendar = orchestrator.generate_content_calendar(days=30)
    
    # Schedule all posts
    results = orchestrator.schedule_all_posts(calendar)
    
    # Start engagement monitoring
    orchestrator.run_engagement_monitoring()
    
    print(f"✅ Scheduled {len(results['scheduled'])} posts across platforms")
