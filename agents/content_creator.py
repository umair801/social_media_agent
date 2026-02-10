"""
Content Creator Agent - Generates platform-optimized social media content
Uses CrewAI framework for intelligent content generation
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

from tools.hashtag_generator import HashtagGenerator
from tools.image_generator import ImagePromptGenerator


class ContentCreatorAgent:
    """
    AI agent that creates engaging, platform-optimized social media content
    """
    
    def __init__(self, brand_config: Dict):
        """
        Initialize content creator with brand configuration
        
        Args:
            brand_config: Brand configuration dictionary
        """
        self.brand_config = brand_config
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        
        # Initialize tools
        self.hashtag_generator = HashtagGenerator()
        self.image_prompt_generator = ImagePromptGenerator()
        
        # Create CrewAI agents
        self._setup_agents()
        
        logger.info("Content Creator Agent initialized")
    
    def _setup_agents(self):
        """Setup CrewAI agents for content creation"""
        
        # Content Strategist Agent
        self.strategist = Agent(
            role="Social Media Strategist",
            goal=f"Create engaging content ideas aligned with {self.brand_config['brand_voice']}",
            backstory="""You are an expert social media strategist with 10 years of experience
            in creating viral content. You understand platform algorithms, audience psychology,
            and content trends across all major social platforms.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        
        # Copywriter Agent
        self.copywriter = Agent(
            role="Social Media Copywriter",
            goal="Write compelling, platform-optimized copy that drives engagement",
            backstory="""You are an award-winning copywriter who specializes in social media.
            You know how to craft hooks that stop scrolling, create emotional connections,
            and drive action. You adapt your writing style perfectly to each platform.""",
            tools=[
                Tool(
                    name="Generate Hashtags",
                    func=self.hashtag_generator.generate,
                    description="Generate relevant hashtags for social posts"
                )
            ],
            llm=self.llm,
            verbose=True
        )
        
        # Visual Content Specialist
        self.visual_specialist = Agent(
            role="Visual Content Specialist",
            goal="Create image and video concepts that complement the copy",
            backstory="""You are a creative director with expertise in social media visuals.
            You understand color psychology, composition, and platform-specific visual requirements.
            You create detailed image prompts that designers can execute perfectly.""",
            tools=[
                Tool(
                    name="Generate Image Prompt",
                    func=self.image_prompt_generator.create_prompt,
                    description="Generate detailed image prompts for visual content"
                )
            ],
            llm=self.llm,
            verbose=True
        )
    
    def create_posts(
        self,
        platform: str,
        count: int = 1,
        content_type: Optional[str] = None,
        target_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Generate social media posts for specified platform
        
        Args:
            platform: Platform name (instagram, linkedin, twitter, facebook)
            count: Number of posts to generate
            content_type: Specific content type (carousel, video, article, etc.)
            target_date: Target posting date
        
        Returns:
            List of generated post dictionaries
        """
        logger.info(f"Generating {count} {platform} posts")
        
        # Get platform-specific requirements
        platform_specs = self._get_platform_specs(platform)
        
        # Get content pillar distribution
        pillars = self._get_content_pillars(count)
        
        posts = []
        
        for i, pillar in enumerate(pillars):
            # Create task for content generation
            task = Task(
                description=f"""Create a {platform} post for {self.brand_config['brand_name']}.
                
                Content Pillar: {pillar}
                Brand Voice: {self.brand_config['brand_voice']}
                Target Audience: {self.brand_config['target_audience']}
                
                Platform Requirements:
                - Max Length: {platform_specs['max_length']} characters
                - Hashtags: {platform_specs['hashtag_count']}
                - Format: {content_type or platform_specs['default_format']}
                
                Create engaging content that:
                1. Hooks attention in the first sentence
                2. Provides value to the audience
                3. Includes a clear call-to-action
                4. Matches the brand voice perfectly
                5. Is optimized for {platform} algorithm
                
                Return in JSON format with keys: caption, hashtags, image_prompt, cta
                """,
                agent=self.copywriter,
                expected_output="JSON object with post content"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.strategist, self.copywriter, self.visual_specialist],
                tasks=[task],
                verbose=False
            )
            
            try:
                result = crew.kickoff()
                
                # Parse result
                post_data = self._parse_crew_output(result, platform)
                
                # Add metadata
                post_data['platform'] = platform
                post_data['content_pillar'] = pillar
                post_data['scheduled_date'] = target_date or datetime.now()
                post_data['status'] = 'draft'
                
                posts.append(post_data)
                logger.success(f"Generated post {i+1}/{count} for {platform}")
                
            except Exception as e:
                logger.error(f"Error generating post: {str(e)}")
                continue
        
        return posts
    
    def _get_platform_specs(self, platform: str) -> Dict:
        """Get platform-specific content specifications"""
        
        specs = {
            'instagram': {
                'max_length': 2200,
                'hashtag_count': 10,
                'default_format': 'carousel',
                'optimal_length': '125-150 words'
            },
            'linkedin': {
                'max_length': 3000,
                'hashtag_count': 5,
                'default_format': 'article',
                'optimal_length': '1300-2000 characters'
            },
            'twitter': {
                'max_length': 280,
                'hashtag_count': 2,
                'default_format': 'text',
                'optimal_length': '100-120 characters'
            },
            'facebook': {
                'max_length': 63206,
                'hashtag_count': 3,
                'default_format': 'video',
                'optimal_length': '40-80 characters'
            }
        }
        
        return specs.get(platform.lower(), specs['instagram'])
    
    def _get_content_pillars(self, count: int) -> List[str]:
        """
        Distribute posts across content pillars based on strategy
        
        Args:
            count: Number of posts to generate
        
        Returns:
            List of content pillar assignments
        """
        pillars_config = self.brand_config.get('content_pillars', {
            'educational': 40,
            'inspirational': 20,
            'promotional': 20,
            'engagement': 20
        })
        
        # Convert percentages to counts
        pillar_list = []
        for pillar, percentage in pillars_config.items():
            pillar_count = int(count * (percentage / 100))
            pillar_list.extend([pillar] * pillar_count)
        
        # Fill remaining slots
        while len(pillar_list) < count:
            pillar_list.append('educational')
        
        return pillar_list[:count]
    
    def _parse_crew_output(self, output: str, platform: str) -> Dict:
        """
        Parse CrewAI output into structured post data
        
        Args:
            output: Raw output from CrewAI
            platform: Target platform
        
        Returns:
            Structured post dictionary
        """
        try:
            # Try to parse as JSON
            if isinstance(output, str):
                # Extract JSON from markdown code blocks if present
                if '```json' in output:
                    json_str = output.split('```json')[1].split('```')[0].strip()
                    data = json.loads(json_str)
                elif '```' in output:
                    json_str = output.split('```')[1].split('```')[0].strip()
                    data = json.loads(json_str)
                else:
                    data = json.loads(output)
            else:
                data = output
            
            # Ensure required fields
            post = {
                'content': data.get('caption', ''),
                'hashtags': data.get('hashtags', []),
                'image_prompt': data.get('image_prompt', ''),
                'cta': data.get('cta', ''),
                'media': None  # Will be generated later
            }
            
            return post
            
        except Exception as e:
            logger.warning(f"Failed to parse crew output as JSON: {str(e)}")
            
            # Fallback: return output as-is
            return {
                'content': str(output),
                'hashtags': [],
                'image_prompt': '',
                'cta': '',
                'media': None
            }
    
    def create_content_series(
        self,
        platform: str,
        topic: str,
        count: int = 5
    ) -> List[Dict]:
        """
        Create a series of related posts on a specific topic
        
        Args:
            platform: Target platform
            topic: Series topic
            count: Number of posts in series
        
        Returns:
            List of related posts
        """
        logger.info(f"Creating {count}-post series on '{topic}' for {platform}")
        
        task = Task(
            description=f"""Create a {count}-post content series about '{topic}' for {platform}.
            
            Each post should:
            1. Build on the previous post
            2. Provide unique value
            3. Include "Part X of {count}" in the content
            4. End with a teaser for the next post (except the last one)
            
            Brand: {self.brand_config['brand_name']}
            Voice: {self.brand_config['brand_voice']}
            
            Return as JSON array of posts.
            """,
            agent=self.strategist,
            expected_output=f"JSON array of {count} posts"
        )
        
        crew = Crew(
            agents=[self.strategist, self.copywriter],
            tasks=[task],
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Parse series
        try:
            if isinstance(result, str):
                series_data = json.loads(result)
            else:
                series_data = result
            
            posts = []
            for i, post_data in enumerate(series_data):
                post = self._parse_crew_output(json.dumps(post_data), platform)
                post['platform'] = platform
                post['series'] = topic
                post['series_number'] = i + 1
                posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"Error creating content series: {str(e)}")
            return []


if __name__ == "__main__":
    # Test content creator
    brand_config = {
        'brand_name': 'Tech Innovators',
        'brand_voice': 'Professional yet approachable',
        'target_audience': 'B2B decision-makers',
        'content_pillars': {
            'educational': 40,
            'inspirational': 20,
            'promotional': 20,
            'engagement': 20
        }
    }
    
    creator = ContentCreatorAgent(brand_config)
    
    # Generate Instagram posts
    posts = creator.create_posts(platform='instagram', count=3)
    
    for i, post in enumerate(posts, 1):
        print(f"\n--- Post {i} ---")
        print(f"Content: {post['content'][:100]}...")
        print(f"Hashtags: {', '.join(post['hashtags'][:5])}")
