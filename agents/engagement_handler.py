"""
Engagement Handler Agent - Manages comments, DMs, and audience interactions
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class EngagementAgent:
    """
    AI agent that handles social media engagement and responses
    """
    
    def __init__(self, brand_config: Dict):
        """
        Initialize engagement handler
        
        Args:
            brand_config: Brand configuration dictionary
        """
        self.brand_config = brand_config
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.6)
        
        # Engagement rules
        self.rules = {
            'positive_comment': {
                'action': 'auto_respond',
                'escalate': False
            },
            'question': {
                'action': 'check_faq',
                'escalate_if_no_match': True
            },
            'complaint': {
                'action': 'immediate_escalate',
                'auto_acknowledge': True
            },
            'spam': {
                'action': 'hide',
                'log': True
            }
        }
        
        # Response templates
        self.templates = {
            'positive': "Thank you {name}! We're thrilled to hear that. {emoji}",
            'question_ack': "Great question, {name}! {answer}",
            'complaint_ack': "We're sorry to hear that, {name}. Our team will reach out within 2 hours.",
            'after_hours': "Thanks for reaching out! We'll reply within 24 hours."
        }
        
        logger.info("Engagement Agent initialized")
    
    def classify_comment(self, comment: str) -> str:
        """
        Classify comment type using LLM
        
        Args:
            comment: Comment text
        
        Returns:
            Classification (positive, question, complaint, spam)
        """
        prompt = PromptTemplate(
            input_variables=["comment"],
            template="""Classify this social media comment into one category:
            - positive: Positive feedback, praise, appreciation
            - question: Asking for information or help
            - complaint: Negative feedback, dissatisfaction
            - spam: Promotional spam, irrelevant content
            
            Comment: {comment}
            
            Return only the category name."""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        classification = chain.run(comment=comment).strip().lower()
        
        logger.debug(f"Classified comment as: {classification}")
        return classification
    
    def generate_response(
        self,
        comment: str,
        classification: str,
        user_name: str = "there"
    ) -> Optional[str]:
        """
        Generate appropriate response to comment
        
        Args:
            comment: Original comment
            classification: Comment classification
            user_name: Commenter's name
        
        Returns:
            Response text or None if no response needed
        """
        rule = self.rules.get(classification, {})
        
        if rule.get('action') == 'hide':
            logger.info("Hiding spam comment")
            return None
        
        if rule.get('action') == 'immediate_escalate':
            if rule.get('auto_acknowledge'):
                return self.templates['complaint_ack'].format(name=user_name)
            return None
        
        # Generate personalized response
        prompt = PromptTemplate(
            input_variables=["comment", "brand_voice", "user_name"],
            template="""Generate a friendly, helpful response to this social media comment.
            
            Brand Voice: {brand_voice}
            User Name: {user_name}
            Comment: {comment}
            
            Requirements:
            - Keep it concise (1-2 sentences)
            - Match the brand voice
            - Be warm and authentic
            - Include user's name if appropriate
            - Don't over-promise
            
            Response:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            comment=comment,
            brand_voice=self.brand_config['brand_voice'],
            user_name=user_name
        )
        
        logger.info(f"Generated response for {classification} comment")
        return response.strip()
    
    def should_escalate(self, comment: str, classification: str) -> bool:
        """
        Determine if comment should be escalated to human
        
        Args:
            comment: Comment text
            classification: Comment classification
        
        Returns:
            True if should escalate
        """
        rule = self.rules.get(classification, {})
        
        # Always escalate complaints
        if classification == 'complaint':
            return True
        
        # Escalate if rule says so
        if rule.get('escalate', False):
            return True
        
        # Check for escalation keywords
        escalation_keywords = [
            'lawsuit', 'lawyer', 'refund', 'cancel',
            'urgent', 'emergency', 'serious', 'manager'
        ]
        
        comment_lower = comment.lower()
        if any(keyword in comment_lower for keyword in escalation_keywords):
            logger.warning(f"Escalation keyword detected in: {comment[:50]}")
            return True
        
        return False
    
    def process_comment(
        self,
        comment: str,
        user_name: str,
        platform: str,
        post_id: str
    ) -> Dict:
        """
        Process a single comment
        
        Args:
            comment: Comment text
            user_name: Commenter's name
            platform: Social media platform
            post_id: ID of the post
        
        Returns:
            Processing result dictionary
        """
        logger.info(f"Processing comment from {user_name} on {platform}")
        
        # Classify comment
        classification = self.classify_comment(comment)
        
        # Check if should escalate
        escalate = self.should_escalate(comment, classification)
        
        result = {
            'comment': comment,
            'user_name': user_name,
            'platform': platform,
            'post_id': post_id,
            'classification': classification,
            'escalated': escalate,
            'response': None,
            'processed_at': datetime.now().isoformat()
        }
        
        if escalate:
            logger.warning(f"Escalating {classification} comment to human")
            result['response'] = self.templates.get('complaint_ack', '').format(name=user_name)
        else:
            # Generate auto-response
            response = self.generate_response(comment, classification, user_name)
            result['response'] = response
        
        return result
    
    def monitor_comments(
        self,
        platform: str,
        check_interval: int = 300
    ):
        """
        Continuously monitor and respond to comments
        
        Args:
            platform: Platform to monitor
            check_interval: Seconds between checks
        """
        logger.info(f"Starting comment monitoring for {platform}")
        
        # This would integrate with platform API
        # For demo purposes, showing the logic
        
        while True:
            try:
                # Fetch new comments (placeholder)
                # new_comments = platform_api.get_new_comments()
                
                # Process each comment
                # for comment_data in new_comments:
                #     result = self.process_comment(
                #         comment=comment_data['text'],
                #         user_name=comment_data['user'],
                #         platform=platform,
                #         post_id=comment_data['post_id']
                #     )
                #
                #     if result['response']:
                #         # Post response
                #         platform_api.reply_to_comment(
                #             comment_id=comment_data['id'],
                #             response=result['response']
                #         )
                
                logger.debug(f"Checked {platform} for new comments")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping comment monitoring")
                break
            except Exception as e:
                logger.error(f"Error monitoring comments: {str(e)}")
                time.sleep(check_interval)
    
    def start_monitoring(self, platforms: List[str]):
        """
        Start monitoring multiple platforms
        
        Args:
            platforms: List of platforms to monitor
        """
        logger.info(f"Starting monitoring for platforms: {', '.join(platforms)}")
        
        # In production, would use multi-threading or async
        for platform in platforms:
            self.monitor_comments(platform)
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of comment or message
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment analysis result
        """
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""Analyze the sentiment of this text.
            
            Text: {text}
            
            Return JSON with:
            - sentiment: positive/neutral/negative
            - confidence: 0-1
            - emotion: primary emotion detected
            
            JSON:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(text=text)
        
        try:
            import json
            sentiment = json.loads(result)
            return sentiment
        except:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'emotion': 'unknown'
            }


if __name__ == "__main__":
    # Test engagement handler
    config = {
        'brand_voice': 'Professional yet approachable',
        'brand_name': 'Tech Innovators'
    }
    
    handler = EngagementAgent(config)
    
    # Test comment processing
    test_comments = [
        ("Love your product! Best decision ever!", "Sarah"),
        ("How do I reset my password?", "John"),
        ("This is terrible, I want a refund!", "Mike"),
    ]
    
    for comment, user in test_comments:
        result = handler.process_comment(comment, user, 'instagram', 'post_123')
        print(f"\n{user}: {comment}")
        print(f"Classification: {result['classification']}")
        print(f"Response: {result['response']}")
        print(f"Escalated: {result['escalated']}")
