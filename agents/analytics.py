"""
Analytics Agent - Tracks performance and generates insights
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import pandas as pd
import json


class AnalyticsAgent:
    """
    AI agent that tracks KPIs and generates performance insights
    """
    
    def __init__(self, brand_config: Dict):
        """
        Initialize analytics agent
        
        Args:
            brand_config: Brand configuration dictionary
        """
        self.brand_config = brand_config
        logger.info("Analytics Agent initialized")
    
    def generate_report(
        self,
        start_date: datetime,
        end_date: datetime,
        platforms: List[str]
    ) -> Dict:
        """
        Generate comprehensive performance report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            platforms: Platforms to include
        
        Returns:
            Performance report dictionary
        """
        logger.info(f"Generating report: {start_date.date()} to {end_date.date()}")
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'platforms': {},
            'summary': {},
            'top_posts': [],
            'recommendations': []
        }
        
        # Collect metrics for each platform
        for platform in platforms:
            metrics = self._get_platform_metrics(platform, start_date, end_date)
            report['platforms'][platform] = metrics
        
        # Calculate summary
        report['summary'] = self._calculate_summary(report['platforms'])
        
        # Identify top posts
        report['top_posts'] = self._get_top_posts(platforms, start_date, end_date)
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        logger.success("Report generated successfully")
        return report
    
    def _get_platform_metrics(
        self,
        platform: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get metrics for specific platform"""
        
        # In production, would fetch from platform APIs
        # Returning sample data structure
        
        return {
            'reach': {
                'total_impressions': 45000,
                'unique_reach': 28000,
                'follower_growth': 1250
            },
            'engagement': {
                'total_likes': 3200,
                'total_comments': 485,
                'total_shares': 320,
                'engagement_rate': 4.2,
                'clicks': 1850
            },
            'content': {
                'posts_published': 28,
                'avg_engagement_per_post': 143,
                'best_performing_type': 'carousel',
                'best_posting_time': '7:00 PM'
            },
            'audience': {
                'top_demographics': {'25-34': 45, '35-44': 30, '18-24': 15},
                'top_locations': ['New York', 'Los Angeles', 'Chicago'],
                'active_hours': ['12-2 PM', '7-9 PM']
            }
        }
    
    def _calculate_summary(self, platforms_data: Dict) -> Dict:
        """Calculate overall summary across platforms"""
        
        total_impressions = sum(
            p['reach']['total_impressions']
            for p in platforms_data.values()
        )
        
        total_engagement = sum(
            p['engagement']['total_likes'] +
            p['engagement']['total_comments'] +
            p['engagement']['total_shares']
            for p in platforms_data.values()
        )
        
        avg_engagement_rate = sum(
            p['engagement']['engagement_rate']
            for p in platforms_data.values()
        ) / len(platforms_data) if platforms_data else 0
        
        total_posts = sum(
            p['content']['posts_published']
            for p in platforms_data.values()
        )
        
        return {
            'total_reach': total_impressions,
            'total_engagement': total_engagement,
            'avg_engagement_rate': round(avg_engagement_rate, 2),
            'total_posts': total_posts,
            'engagement_per_post': round(total_engagement / total_posts, 2) if total_posts else 0
        }
    
    def _get_top_posts(
        self,
        platforms: List[str],
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[Dict]:
        """Identify top performing posts"""
        
        # In production, would fetch actual post data
        # Returning sample structure
        
        top_posts = [
            {
                'platform': 'instagram',
                'post_id': 'post_123',
                'content': 'How to boost your productivity...',
                'engagement': 523,
                'reach': 12000,
                'posted_at': '2024-12-15T14:00:00'
            },
            {
                'platform': 'linkedin',
                'post_id': 'post_456',
                'content': '5 data-driven strategies...',
                'engagement': 412,
                'reach': 8500,
                'posted_at': '2024-12-18T09:00:00'
            }
        ]
        
        return top_posts[:limit]
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable recommendations based on data"""
        
        recommendations = []
        
        summary = report['summary']
        
        # Engagement rate recommendations
        if summary['avg_engagement_rate'] < 3.0:
            recommendations.append(
                "Engagement rate is below industry average (3-5%). "
                "Try more interactive content like polls, questions, and user-generated content."
            )
        
        # Posting frequency
        posts_per_day = summary['total_posts'] / report['period']['days']
        if posts_per_day < 1:
            recommendations.append(
                f"Currently posting {posts_per_day:.1f} times per day. "
                "Increase frequency to 1-2 posts per day for optimal reach."
            )
        
        # Platform-specific recommendations
        for platform, data in report['platforms'].items():
            best_time = data['content']['best_posting_time']
            recommendations.append(
                f"{platform.title()}: Continue posting around {best_time} for maximum engagement"
            )
        
        # Content type recommendations
        recommendations.append(
            "Focus on carousel posts and video content, which show 3x higher engagement"
        )
        
        return recommendations
    
    def track_ab_test(
        self,
        post_a_id: str,
        post_b_id: str,
        duration_hours: int = 24
    ) -> Dict:
        """
        Track A/B test performance
        
        Args:
            post_a_id: ID of first post variant
            post_b_id: ID of second post variant
            duration_hours: Test duration
        
        Returns:
            Test results
        """
        logger.info(f"Tracking A/B test: {post_a_id} vs {post_b_id}")
        
        # In production, would fetch actual metrics
        results = {
            'post_a': {
                'id': post_a_id,
                'impressions': 5200,
                'engagement': 245,
                'engagement_rate': 4.7,
                'clicks': 180
            },
            'post_b': {
                'id': post_b_id,
                'impressions': 4800,
                'engagement': 290,
                'engagement_rate': 6.0,
                'clicks': 210
            },
            'winner': 'b',
            'confidence': 0.85,
            'recommendation': "Post B performed 28% better. Use similar style for future content."
        }
        
        return results
    
    def export_report(
        self,
        report: Dict,
        format: str = 'json',
        filepath: Optional[str] = None
    ) -> str:
        """
        Export report to file
        
        Args:
            report: Report dictionary
            format: Export format (json, csv, pdf)
            filepath: Output file path
        
        Returns:
            Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"reports/social_media_report_{timestamp}.{format}"
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif format == 'csv':
            # Convert to DataFrame and export
            df = pd.DataFrame([report['summary']])
            df.to_csv(filepath, index=False)
        
        logger.info(f"Report exported to {filepath}")
        return filepath


if __name__ == "__main__":
    # Test analytics
    config = {'brand_name': 'Test Brand'}
    analytics = AnalyticsAgent(config)
    
    # Generate report
    report = analytics.generate_report(
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        platforms=['instagram', 'linkedin', 'twitter']
    )
    
    print(json.dumps(report['summary'], indent=2))
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"- {rec}")
