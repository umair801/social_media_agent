"""
Image Prompt Generator - Creates detailed prompts for visual content
"""

from typing import Dict
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class ImagePromptGenerator:
    """
    Generates detailed image prompts for designers or AI image generators
    """
    
    def __init__(self):
        """Initialize image prompt generator"""
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        logger.info("Image Prompt Generator initialized")
    
    def create_prompt(
        self,
        content: str,
        platform: str = 'instagram',
        style: str = 'professional',
        brand_colors: str = None
    ) -> str:
        """
        Generate detailed image prompt
        
        Args:
            content: Post content/caption
            platform: Social media platform
            style: Visual style (professional, minimal, vibrant, etc.)
            brand_colors: Brand color palette
        
        Returns:
            Detailed image prompt
        """
        logger.info(f"Creating image prompt for {platform}")
        
        # Platform specifications
        platform_specs = {
            'instagram': {
                'aspect_ratio': '1:1 or 4:5',
                'optimal_size': '1080x1080 or 1080x1350',
                'style': 'eye-catching, mobile-optimized'
            },
            'linkedin': {
                'aspect_ratio': '1.91:1',
                'optimal_size': '1200x627',
                'style': 'professional, clean'
            },
            'twitter': {
                'aspect_ratio': '16:9',
                'optimal_size': '1200x675',
                'style': 'simple, clear message'
            },
            'facebook': {
                'aspect_ratio': '1.91:1',
                'optimal_size': '1200x630',
                'style': 'engaging, shareable'
            }
        }
        
        specs = platform_specs.get(platform.lower(), platform_specs['instagram'])
        
        prompt_template = PromptTemplate(
            input_variables=["content", "platform", "aspect_ratio", "style", "colors"],
            template="""Create a detailed image prompt for a social media post.
            
            Post Content: {content}
            Platform: {platform}
            Aspect Ratio: {aspect_ratio}
            Visual Style: {style}
            Brand Colors: {colors}
            
            Generate a detailed prompt that describes:
            1. Main subject/focus
            2. Composition and layout
            3. Color scheme
            4. Typography (if text overlay needed)
            5. Mood and atmosphere
            6. Background elements
            7. Any specific visual elements that support the message
            
            Make the prompt specific enough for a designer or AI image generator to execute.
            Keep it concise but comprehensive.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        try:
            image_prompt = chain.run(
                content=content,
                platform=platform,
                aspect_ratio=specs['aspect_ratio'],
                style=f"{style}, {specs['style']}",
                colors=brand_colors or "modern, professional palette"
            )
            
            logger.success("Image prompt created successfully")
            return image_prompt.strip()
            
        except Exception as e:
            logger.error(f"Error creating image prompt: {str(e)}")
            return f"Create a {style} image for {platform} about: {content}"
    
    def create_carousel_prompts(
        self,
        content_slides: list,
        platform: str = 'instagram',
        theme: str = 'cohesive'
    ) -> list:
        """
        Generate prompts for carousel posts
        
        Args:
            content_slides: List of slide contents
            platform: Social media platform
            theme: Visual theme to maintain across slides
        
        Returns:
            List of image prompts for each slide
        """
        logger.info(f"Creating carousel prompts for {len(content_slides)} slides")
        
        prompt_template = PromptTemplate(
            input_variables=["slides", "platform", "theme", "slide_count"],
            template="""Create image prompts for a {slide_count}-slide carousel post.
            
            Platform: {platform}
            Theme: {theme}
            
            Slide Contents:
            {slides}
            
            For each slide, create a prompt that:
            - Maintains visual consistency across all slides
            - Uses the same color scheme and style
            - Has clear visual hierarchy
            - Makes the sequence flow naturally
            
            Return as numbered list of prompts.
            """
        )
        
        slides_text = "\n".join([f"{i+1}. {slide}" for i, slide in enumerate(content_slides)])
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(
            slides=slides_text,
            platform=platform,
            theme=theme,
            slide_count=len(content_slides)
        )
        
        # Parse numbered list
        prompts = []
        for line in result.split('\n'):
            if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 20)):
                prompt = line.split('.', 1)[1].strip()
                prompts.append(prompt)
        
        return prompts[:len(content_slides)]
    
    def suggest_visual_elements(self, content: str, industry: str = None) -> Dict:
        """
        Suggest visual elements based on content
        
        Args:
            content: Post content
            industry: Industry/niche for context
        
        Returns:
            Dictionary of visual element suggestions
        """
        prompt_template = PromptTemplate(
            input_variables=["content", "industry"],
            template="""Based on this content, suggest visual elements:
            
            Content: {content}
            Industry: {industry}
            
            Suggest:
            1. Icons/Graphics: 3-5 relevant icons
            2. Background: background style
            3. Typography: font style recommendations
            4. Color Mood: suggested color palette
            5. Stock Photo Keywords: 5 keywords for finding relevant images
            
            Format as JSON.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(
            content=content,
            industry=industry or "general"
        )
        
        try:
            import json
            suggestions = json.loads(result)
            return suggestions
        except:
            return {
                'icons': [],
                'background': 'clean, minimal',
                'typography': 'modern sans-serif',
                'color_mood': 'professional',
                'stock_keywords': []
            }


if __name__ == "__main__":
    # Test image prompt generator
    generator = ImagePromptGenerator()
    
    # Single image prompt
    content = "5 productivity hacks that will change your workflow forever"
    prompt = generator.create_prompt(
        content=content,
        platform='instagram',
        style='modern and vibrant',
        brand_colors='blue and orange'
    )
    
    print(f"Content: {content}\n")
    print(f"Image Prompt:\n{prompt}\n")
    
    # Carousel prompts
    slides = [
        "Hack #1: Time blocking",
        "Hack #2: Pomodoro technique",
        "Hack #3: Automation tools"
    ]
    
    carousel_prompts = generator.create_carousel_prompts(slides)
    print("\nCarousel Prompts:")
    for i, p in enumerate(carousel_prompts, 1):
        print(f"\nSlide {i}:\n{p}")
