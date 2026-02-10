"""
Brand Voice Validator - Ensures content matches brand identity
"""

from typing import Dict
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class BrandVoiceValidator:
    """
    Validates content against brand voice guidelines
    """
    
    def __init__(self, brand_config: Dict):
        """
        Initialize validator with brand configuration
        
        Args:
            brand_config: Brand configuration dictionary
        """
        self.brand_config = brand_config
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        
        # Extract brand voice attributes
        self.brand_voice = brand_config.get('brand_voice', 'Professional')
        self.tone = brand_config.get('tone', [])
        self.values = brand_config.get('values', [])
        
        logger.info("Brand Voice Validator initialized")
    
    def validate(self, content: str, threshold: float = 0.7) -> bool:
        """
        Validate if content matches brand voice
        
        Args:
            content: Content to validate
            threshold: Minimum score to pass (0-1)
        
        Returns:
            True if content passes validation
        """
        logger.debug(f"Validating content: {content[:50]}...")
        
        score = self.score_content(content)
        
        passed = score >= threshold
        
        if passed:
            logger.success(f"Content passed validation (score: {score:.2f})")
        else:
            logger.warning(f"Content failed validation (score: {score:.2f})")
        
        return passed
    
    def score_content(self, content: str) -> float:
        """
        Score content against brand voice (0-1)
        
        Args:
            content: Content to score
        
        Returns:
            Score between 0 and 1
        """
        prompt = PromptTemplate(
            input_variables=["content", "brand_voice", "tone", "values"],
            template="""Analyze if this content matches the brand voice.
            
            Brand Voice: {brand_voice}
            Tone: {tone}
            Values: {values}
            
            Content: {content}
            
            Rate how well the content matches the brand voice on a scale of 0-1:
            - 1.0: Perfect match
            - 0.7-0.9: Good match with minor adjustments needed
            - 0.5-0.7: Moderate match, needs revision
            - Below 0.5: Poor match, major revision needed
            
            Consider:
            - Tone and style consistency
            - Alignment with brand values
            - Language and vocabulary choice
            - Professionalism level
            - Authenticity
            
            Return only the numeric score (e.g., 0.85)
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(
                content=content,
                brand_voice=self.brand_voice,
                tone=', '.join(self.tone) if self.tone else 'neutral',
                values=', '.join(self.values) if self.values else 'none specified'
            )
            
            # Extract numeric score
            score = float(result.strip())
            return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error(f"Error scoring content: {str(e)}")
            return 0.5  # Default to moderate score on error
    
    def suggest_improvements(self, content: str) -> str:
        """
        Suggest improvements to better match brand voice
        
        Args:
            content: Original content
        
        Returns:
            Suggested improvements
        """
        prompt = PromptTemplate(
            input_variables=["content", "brand_voice"],
            template="""Suggest improvements to make this content better match the brand voice.
            
            Brand Voice: {brand_voice}
            Original Content: {content}
            
            Provide specific, actionable suggestions to improve:
            1. Tone and style
            2. Word choice
            3. Structure
            4. Authenticity
            
            Keep suggestions concise and practical.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        suggestions = chain.run(content=content, brand_voice=self.brand_voice)
        
        return suggestions.strip()
    
    def rewrite_content(self, content: str) -> str:
        """
        Rewrite content to match brand voice
        
        Args:
            content: Original content
        
        Returns:
            Rewritten content
        """
        logger.info("Rewriting content to match brand voice")
        
        prompt = PromptTemplate(
            input_variables=["content", "brand_voice", "tone"],
            template="""Rewrite this content to perfectly match the brand voice.
            
            Brand Voice: {brand_voice}
            Tone: {tone}
            Original: {content}
            
            Requirements:
            - Keep the core message and information
            - Match the brand voice exactly
            - Maintain similar length
            - Keep it natural and authentic
            
            Rewritten content:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        rewritten = chain.run(
            content=content,
            brand_voice=self.brand_voice,
            tone=', '.join(self.tone) if self.tone else 'neutral'
        )
        
        return rewritten.strip()


if __name__ == "__main__":
    # Test validator
    config = {
        'brand_voice': 'Professional yet approachable',
        'tone': ['educational', 'inspirational'],
        'values': ['innovation', 'customer success', 'integrity']
    }
    
    validator = BrandVoiceValidator(config)
    
    # Test content
    test_content = "Hey guys! 🎉 Check out our AMAZING new product! It's literally the best thing ever!!!"
    
    print(f"Content: {test_content}\n")
    
    # Score
    score = validator.score_content(test_content)
    print(f"Score: {score:.2f}\n")
    
    # Validate
    passed = validator.validate(test_content)
    print(f"Passed: {passed}\n")
    
    if not passed:
        # Get suggestions
        suggestions = validator.suggest_improvements(test_content)
        print(f"Suggestions:\n{suggestions}\n")
        
        # Rewrite
        rewritten = validator.rewrite_content(test_content)
        print(f"Rewritten:\n{rewritten}")
