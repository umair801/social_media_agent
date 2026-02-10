"""
Scheduler Agent - Optimizes posting times based on audience analytics
"""

import pytz
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
from loguru import logger
import pandas as pd


class SchedulerAgent:
    """
    AI agent that determines optimal posting times based on analytics
    """
    
    def __init__(self, brand_config: Dict):
        """
        Initialize scheduler with brand configuration
        
        Args:
            brand_config: Brand configuration dictionary
        """
        self.brand_config = brand_config
        self.timezone = pytz.timezone(brand_config.get('timezone', 'UTC'))
        
        # Platform-specific optimal times (default baseline)
        self.optimal_times = {
            'instagram': [
                time(11, 0), time(13, 0),  # Mon-Fri lunch
                time(19, 0), time(21, 0)   # Evening
            ],
            'linkedin': [
                time(8, 0), time(10, 0),   # Morning
                time(12, 0), time(17, 0)   # Lunch & evening
            ],
            'twitter': [
                time(9, 0), time(12, 0),   # Morning & lunch
                time(15, 0), time(17, 0), time(21, 0)  # Afternoon & evening
            ],
            'facebook': [
                time(13, 0), time(15, 0),  # Afternoon
                time(19, 0)  # Evening
            ]
        }
        
        logger.info("Scheduler Agent initialized")
    
    def get_optimal_time(
        self,
        platform: str,
        date: datetime,
        custom_times: Optional[List[time]] = None
    ) -> datetime:
        """
        Get optimal posting time for platform on specific date
        
        Args:
            platform: Social media platform
            date: Target date
            custom_times: Override default optimal times
        
        Returns:
            Datetime with optimal posting time
        """
        times = custom_times or self.optimal_times.get(platform.lower(), [time(12, 0)])
        
        # Select time based on day of week
        day_index = date.weekday()
        time_index = day_index % len(times)
        selected_time = times[time_index]
        
        # Combine date and time
        scheduled_datetime = datetime.combine(
            date.date(),
            selected_time,
            tzinfo=self.timezone
        )
        
        logger.debug(f"Optimal time for {platform} on {date.date()}: {scheduled_datetime}")
        
        return scheduled_datetime
    
    def create_weekly_schedule(
        self,
        platforms: List[str],
        posts_per_week: Dict[str, int]
    ) -> pd.DataFrame:
        """
        Create complete weekly posting schedule
        
        Args:
            platforms: List of platforms
            posts_per_week: Dict mapping platform to number of posts per week
        
        Returns:
            DataFrame with weekly schedule
        """
        logger.info("Creating weekly posting schedule")
        
        schedule = []
        start_date = datetime.now(self.timezone)
        
        for platform in platforms:
            count = posts_per_week.get(platform, 7)
            
            # Distribute posts across week
            for i in range(count):
                day_offset = (i * 7) // count
                post_date = start_date + timedelta(days=day_offset)
                
                post_time = self.get_optimal_time(platform, post_date)
                
                schedule.append({
                    'platform': platform,
                    'date': post_date.date(),
                    'time': post_time.time(),
                    'datetime': post_time,
                    'day_of_week': post_time.strftime('%A')
                })
        
        df = pd.DataFrame(schedule)
        df = df.sort_values('datetime')
        
        logger.success(f"Created schedule with {len(df)} posts")
        return df
    
    def optimize_schedule(self, historical_days: int = 30) -> Dict:
        """
        Analyze past performance and optimize posting schedule
        
        Args:
            historical_days: Days of historical data to analyze
        
        Returns:
            Optimized schedule recommendations
        """
        logger.info(f"Optimizing schedule based on {historical_days} days")
        
        # This would analyze actual performance data
        # For now, returning platform-specific best practices
        
        recommendations = {
            'instagram': {
                'best_days': ['Wednesday', 'Friday'],
                'best_times': ['11:00 AM', '7:00 PM'],
                'posts_per_week': 14,  # 2 per day
                'engagement_peak': 'Wednesday 7-9 PM'
            },
            'linkedin': {
                'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'best_times': ['8:00 AM', '12:00 PM', '5:00 PM'],
                'posts_per_week': 5,
                'engagement_peak': 'Tuesday 8-10 AM'
            },
            'twitter': {
                'best_days': ['Monday', 'Tuesday', 'Wednesday'],
                'best_times': ['9:00 AM', '12:00 PM', '3:00 PM', '5:00 PM'],
                'posts_per_week': 21,  # 3 per day
                'engagement_peak': 'Wednesday 3-5 PM'
            },
            'facebook': {
                'best_days': ['Thursday', 'Friday'],
                'best_times': ['1:00 PM', '3:00 PM'],
                'posts_per_week': 7,
                'engagement_peak': 'Thursday 1-3 PM'
            }
        }
        
        return recommendations
    
    def avoid_conflicts(
        self,
        scheduled_posts: List[Dict],
        min_gap_hours: int = 2
    ) -> List[Dict]:
        """
        Adjust schedule to avoid posting conflicts
        
        Args:
            scheduled_posts: List of scheduled posts
            min_gap_hours: Minimum hours between posts on same platform
        
        Returns:
            Adjusted schedule
        """
        logger.info("Checking for scheduling conflicts")
        
        # Sort by datetime
        sorted_posts = sorted(scheduled_posts, key=lambda x: x['datetime'])
        
        adjusted = []
        last_post_time = {}
        
        for post in sorted_posts:
            platform = post['platform']
            scheduled_time = post['datetime']
            
            if platform in last_post_time:
                time_diff = (scheduled_time - last_post_time[platform]).total_seconds() / 3600
                
                if time_diff < min_gap_hours:
                    # Adjust time
                    adjustment = timedelta(hours=min_gap_hours - time_diff + 0.5)
                    post['datetime'] = scheduled_time + adjustment
                    logger.warning(f"Adjusted {platform} post time to avoid conflict")
            
            last_post_time[platform] = post['datetime']
            adjusted.append(post)
        
        return adjusted


if __name__ == "__main__":
    # Test scheduler
    config = {'timezone': 'America/New_York'}
    scheduler = SchedulerAgent(config)
    
    # Get optimal time
    optimal = scheduler.get_optimal_time('instagram', datetime.now())
    print(f"Optimal Instagram time: {optimal}")
    
    # Create weekly schedule
    schedule = scheduler.create_weekly_schedule(
        platforms=['instagram', 'linkedin', 'twitter'],
        posts_per_week={'instagram': 14, 'linkedin': 5, 'twitter': 21}
    )
    print(f"\nWeekly Schedule:\n{schedule.head(10)}")
