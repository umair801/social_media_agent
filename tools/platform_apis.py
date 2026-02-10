"""
Platform API Wrappers for social media posting and data retrieval
"""

import os
import requests
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class PlatformManager:
    """
    Manages API connections to social media platforms
    """
    
    def __init__(self):
        """Initialize platform API clients"""
        self.buffer_token = os.getenv('BUFFER_ACCESS_TOKEN')
        self.instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.linkedin_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        
        logger.info("Platform Manager initialized")
    
    def schedule_post(
        self,
        platform: str,
        content: str,
        scheduled_time: datetime,
        media: Optional[List[str]] = None
    ) -> Dict:
        """
        Schedule post via Buffer or platform API
        
        Args:
            platform: Target platform
            content: Post content/caption
            scheduled_time: When to post
            media: List of media URLs
        
        Returns:
            Scheduled post data
        """
        logger.info(f"Scheduling {platform} post for {scheduled_time}")
        
        if self.buffer_token:
            return self._schedule_via_buffer(platform, content, scheduled_time, media)
        else:
            return self._schedule_direct(platform, content, scheduled_time, media)
    
    def _schedule_via_buffer(
        self,
        platform: str,
        content: str,
        scheduled_time: datetime,
        media: Optional[List[str]]
    ) -> Dict:
        """Schedule post using Buffer API"""
        
        url = "https://api.bufferapp.com/1/updates/create.json"
        
        # Get Buffer profile IDs
        profile_ids = os.getenv('BUFFER_PROFILE_IDS', '').split(',')
        platform_map = {
            'instagram': profile_ids[0] if len(profile_ids) > 0 else '',
            'linkedin': profile_ids[1] if len(profile_ids) > 1 else '',
            'twitter': profile_ids[2] if len(profile_ids) > 2 else '',
            'facebook': profile_ids[3] if len(profile_ids) > 3 else ''
        }
        
        profile_id = platform_map.get(platform.lower(), '')
        
        data = {
            'text': content,
            'profile_ids[]': [profile_id],
            'scheduled_at': int(scheduled_time.timestamp()),
            'access_token': self.buffer_token
        }
        
        if media:
            data['media[photo]'] = media[0]  # Buffer supports one image per post
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            
            logger.success(f"Scheduled via Buffer: {result.get('id')}")
            return {
                'success': True,
                'id': result.get('id'),
                'platform': platform,
                'scheduled_time': scheduled_time.isoformat()
            }
        except Exception as e:
            logger.error(f"Buffer API error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _schedule_direct(
        self,
        platform: str,
        content: str,
        scheduled_time: datetime,
        media: Optional[List[str]]
    ) -> Dict:
        """Schedule directly via platform API"""
        
        if platform.lower() == 'instagram':
            return self._schedule_instagram(content, scheduled_time, media)
        elif platform.lower() == 'linkedin':
            return self._schedule_linkedin(content, scheduled_time, media)
        elif platform.lower() == 'twitter':
            return self._schedule_twitter(content, scheduled_time, media)
        elif platform.lower() == 'facebook':
            return self._schedule_facebook(content, scheduled_time, media)
        else:
            logger.error(f"Unsupported platform: {platform}")
            return {'success': False, 'error': 'Unsupported platform'}
    
    def _schedule_instagram(
        self,
        content: str,
        scheduled_time: datetime,
        media: Optional[List[str]]
    ) -> Dict:
        """Schedule Instagram post via Graph API"""
        
        # Instagram API endpoint
        account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        url = f"https://graph.facebook.com/v18.0/{account_id}/media"
        
        params = {
            'caption': content,
            'access_token': self.instagram_token
        }
        
        if media:
            params['image_url'] = media[0]
        
        try:
            # Create media container
            response = requests.post(url, params=params)
            response.raise_for_status()
            media_id = response.json()['id']
            
            # Publish (Instagram doesn't support scheduling via API without Business account)
            publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
            publish_params = {
                'creation_id': media_id,
                'access_token': self.instagram_token
            }
            
            publish_response = requests.post(publish_url, params=publish_params)
            publish_response.raise_for_status()
            
            logger.success(f"Posted to Instagram: {media_id}")
            return {
                'success': True,
                'id': media_id,
                'platform': 'instagram'
            }
        except Exception as e:
            logger.error(f"Instagram API error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _schedule_linkedin(
        self,
        content: str,
        scheduled_time: datetime,
        media: Optional[List[str]]
    ) -> Dict:
        """Schedule LinkedIn post"""
        
        org_id = os.getenv('LINKEDIN_ORGANIZATION_ID')
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            'Authorization': f'Bearer {self.linkedin_token}',
            'Content-Type': 'application/json'
        }
        
        post_data = {
            'author': f'urn:li:organization:{org_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': content
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=post_data)
            response.raise_for_status()
            result = response.json()
            
            logger.success(f"Posted to LinkedIn: {result.get('id')}")
            return {
                'success': True,
                'id': result.get('id'),
                'platform': 'linkedin'
            }
        except Exception as e:
            logger.error(f"LinkedIn API error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _schedule_twitter(
        self,
        content: str,
        scheduled_time: datetime,
        media: Optional[List[str]]
    ) -> Dict:
        """Schedule Twitter/X post"""
        
        # Using Twitter API v2
        import tweepy
        
        try:
            client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=self.twitter_api_key,
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
            )
            
            # Tweet
            response = client.create_tweet(text=content)
            
            logger.success(f"Posted to Twitter: {response.data['id']}")
            return {
                'success': True,
                'id': response.data['id'],
                'platform': 'twitter'
            }
        except Exception as e:
            logger.error(f"Twitter API error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _schedule_facebook(
        self,
        content: str,
        scheduled_time: datetime,
        media: Optional[List[str]]
    ) -> Dict:
        """Schedule Facebook post"""
        
        page_id = os.getenv('FACEBOOK_PAGE_ID')
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        
        params = {
            'message': content,
            'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN'),
            'published': True
        }
        
        if media:
            params['link'] = media[0]
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            logger.success(f"Posted to Facebook: {result.get('id')}")
            return {
                'success': True,
                'id': result.get('id'),
                'platform': 'facebook'
            }
        except Exception as e:
            logger.error(f"Facebook API error: {str(e)}")
            return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    # Test platform manager
    manager = PlatformManager()
    
    # Example schedule
    result = manager.schedule_post(
        platform='twitter',
        content='Testing automated posting! #AI #Automation',
        scheduled_time=datetime.now(),
        media=None
    )
    
    print(f"Result: {result}")
