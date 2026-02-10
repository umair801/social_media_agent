#!/usr/bin/env python3
"""
Quick Start Example
Generate your first batch of social media posts
"""

import os
import sys
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.content_creator import ContentCreatorAgent

def main():
    """Quick start demo"""
    
    print("=" * 60)
    print("Social Media Agent - Quick Start Demo")
    print("=" * 60)
    print()
    
    # Simple brand configuration
    brand_config = {
        'brand_name': 'Tech Innovators',
        'industry': 'Technology',
        'brand_voice': 'Professional yet approachable, innovative',
        'target_audience': {
            'age_range': '25-45',
            'interests': ['technology', 'innovation', 'business'],
            'platforms': ['Instagram', 'LinkedIn', 'Twitter']
        },
        'content_pillars': {
            'educational': 40,
            'inspirational': 20,
            'promotional': 20,
            'engagement': 20
        }
    }
    
    print(f"Brand: {brand_config['brand_name']}")
    print(f"Voice: {brand_config['brand_voice']}")
    print()
    
    # Create content creator
    print("Initializing AI content creator...")
    creator = ContentCreatorAgent(brand_config)
    print("✓ Creator initialized\n")
    
    # Generate sample posts for each platform
    platforms = ['instagram', 'linkedin', 'twitter']
    
    all_posts = {}
    
    for platform in platforms:
        print(f"Generating {platform.title()} post...")
        
        try:
            posts = creator.create_posts(
                platform=platform,
                count=1,
                target_date=datetime.now()
            )
            
            if posts:
                all_posts[platform] = posts[0]
                print(f"✓ {platform.title()} post generated\n")
            else:
                print(f"✗ Failed to generate {platform} post\n")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}\n")
            continue
    
    # Display results
    print("\n" + "=" * 60)
    print("GENERATED CONTENT")
    print("=" * 60)
    
    for platform, post in all_posts.items():
        print(f"\n{platform.upper()}:")
        print("-" * 60)
        print(f"\nCaption:\n{post['content']}\n")
        
        if post.get('hashtags'):
            print(f"Hashtags: {' '.join(post['hashtags'][:5])}\n")
        
        if post.get('image_prompt'):
            print(f"Image Concept:\n{post['image_prompt']}\n")
    
    # Save to file
    output_file = 'sample_posts.json'
    with open(output_file, 'w') as f:
        json.dump(all_posts, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print(f"✓ Sample posts saved to: {output_file}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the generated content")
    print("2. Customize config/brand_profiles.yaml for your brand")
    print("3. Add your API keys to .env file")
    print("4. Run: python run_engagement_agent.py --test-mode")
    print()


if __name__ == "__main__":
    main()
