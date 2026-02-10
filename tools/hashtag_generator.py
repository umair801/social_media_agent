"""
Hashtag Generator - Creates relevant hashtags for social media posts
"""

from typing import List
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class HashtagGenerator:
    """
    Generates relevant and trending hashtags for posts
    """
    
    def __init__(self):
        """Initialize hashtag generator"""
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.5)
        logger.info("Hashtag Generator initialized")
    
    def generate(
        self,
        content: str,
        platform: str = 'instagram',
        count: int = 10,
        include_branded: bool = True
    ) -> List[str]:
        """
        Generate hashtags for content
        
        Args:
            content: Post content
            platform: Social media platform
            count: Number of hashtags to generate
            include_branded: Include brand/company hashtags
        
        Returns:
            List of hashtags
        """
        logger.info(f"Generating {count} hashtags for {platform}")
        
        # Platform-specific recommendations
        platform_specs = {
            'instagram': {
                'max_hashtags': 30,
                'optimal_count': 10,
                'style': 'mix of popular and niche'
            },
            'linkedin': {
                'max_hashtags': 5,
                'optimal_count': 5,
                'style': 'professional and industry-specific'
            },
            'twitter': {
                'max_hashtags': 2,
                'optimal_count': 2,
                'style': 'trending and concise'
            },
            'facebook': {
                'max_hashtags': 3,
                'optimal_count': 3,
                'style': 'broad and discoverable'
            }
        }
        
        specs = platform_specs.get(platform.lower(), platform_specs['instagram'])
        
        prompt = PromptTemplate(
            input_variables=["content", "platform", "count", "style"],
            template="""Generate relevant hashtags for this social media post.
            
            Platform: {platform}
            Content: {content}
            Number needed: {count}
            Style: {style}
            
            Requirements:
            - Mix of popular (100k+ posts) and niche (1k-50k posts) hashtags
            - Relevant to the content topic
            - Industry-appropriate
            - No spaces or special characters
            - Start with #
            
            Return ONLY a comma-separated list of hashtags (e.g., #Marketing, #SocialMedia, #Growth)
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(
                content=content,
                platform=platform,
                count=count,
                style=specs['style']
            )
            
            # Parse hashtags
            hashtags = [
                tag.strip() if tag.startswith('#') else f"#{tag.strip()}"
                for tag in result.split(',')
            ]
            
            # Remove duplicates and limit count
            hashtags = list(dict.fromkeys(hashtags))[:count]
            
            logger.success(f"Generated {len(hashtags)} hashtags")
            return hashtags
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return [f"#{platform}"]  # Fallback
    
    def analyze_hashtag_performance(
        self,
        hashtag: str,
        platform: str = 'instagram'
    ) -> dict:
        """
        Analyze hashtag performance potential
        
        Args:
            hashtag: Hashtag to analyze (with or without #)
            platform: Social media platform
        
        Returns:
            Performance analysis dictionary
        """
        # Remove # if present
        tag = hashtag.lstrip('#')
        
        prompt = PromptTemplate(
            input_variables=["hashtag", "platform"],
            template="""Analyze this hashtag for {platform}:
            
            Hashtag: #{hashtag}
            
            Provide analysis in this format:
            - Competition: low/medium/high
            - Estimated posts: number
            - Target audience: description
            - Recommendation: use/don't use
            
            Keep response concise.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        analysis = chain.run(hashtag=tag, platform=platform)
        
        return {
            'hashtag': f"#{tag}",
            'platform': platform,
            'analysis': analysis.strip()
        }
    
    def generate_campaign_hashtags(
        self,
        campaign_name: str,
        campaign_goal: str,
        brand_name: str
    ) -> List[str]:
        """
        Generate hashtags for a marketing campaign
        
        Args:
            campaign_name: Name of the campaign
            campaign_goal: Campaign objective
            brand_name: Brand name
        
        Returns:
            List of campaign hashtags
        """
        logger.info(f"Generating campaign hashtags for: {campaign_name}")
        
        prompt = PromptTemplate(
            input_variables=["campaign", "goal", "brand"],
            template="""Create branded hashtags for this marketing campaign:
            
            Campaign: {campaign}
            Goal: {goal}
            Brand: {brand}
            
            Generate 5 hashtags:
            1. Primary branded hashtag (campaign-specific)
            2. Secondary branded hashtag (brand-specific)
            3. Category hashtag (industry/niche)
            4. Trending hashtag (aligned with current trends)
            5. Call-to-action hashtag (engagement)
            
            Make them memorable, easy to spell, and not too long.
            Return as comma-separated list.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(campaign=campaign_name, goal=campaign_goal, brand=brand_name)
        
        hashtags = [
            tag.strip() if tag.startswith('#') else f"#{tag.strip()}"
            for tag in result.split(',')
        ]
        
        return hashtags[:5]


if __name__ == "__main__":
    # Test hashtag generator
    generator = HashtagGenerator()
    
    # Generate hashtags for post
    content = "5 proven strategies to boost your social media engagement in 2024"
    hashtags = generator.generate(
        content=content,
        platform='instagram',
        count=10
    )
    
    print(f"Content: {content}\n")
    print(f"Generated Hashtags:")
    for tag in hashtags:
        print(f"  {tag}")
    
    # Campaign hashtags
    print("\nCampaign Hashtags:")
    campaign_tags = generator.generate_campaign_hashtags(
        campaign_name="Summer Sale 2024",
        campaign_goal="Drive 30% increase in sales",
        brand_name="TechGear"
    )
    for tag in campaign_tags:
        print(f"  {tag}")
