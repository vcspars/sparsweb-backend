import os
from openai import OpenAI
from typing import List, Dict, Optional

class ChatbotService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: OPENAI_API_KEY not set. Chatbot will use fallback responses.")

    async def get_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Get response from GPT chatbot"""
        
        if not self.api_key:
            # Fallback response if API key is not set
            return self._get_fallback_response(message)
        
        try:
            if not self.client:
                return self._get_fallback_response(message)
            
            # System prompt for SPARS assistant
            system_prompt = """You are a helpful AI assistant for SPARS, an ERP solution designed specifically for the home furnishing industry. 
            SPARS helps wholesalers and distributors manage their operations efficiently. 
            You should be friendly, professional, and knowledgeable about SPARS features, modules, and capabilities.
            If you don't know something specific, direct users to contact the sales team at info@sparsus.com or call +1 (212) 685-2127.
            Keep responses concise and helpful."""
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages for context
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message: str) -> str:
        """Fallback responses when GPT is not available"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["price", "cost", "pricing", "how much"]):
            return "For pricing information, please contact our sales team at info@sparsus.com or call +1 (212) 685-2127. They'll be happy to provide you with a customized quote based on your needs."
        
        elif any(word in message_lower for word in ["demo", "demonstration", "trial"]):
            return "Great! You can request a demo by filling out the contact form on our website or by emailing info@sparsus.com. Our team will schedule a personalized demonstration for you."
        
        elif any(word in message_lower for word in ["feature", "module", "capability", "what can"]):
            return "SPARS offers comprehensive ERP solutions including inventory management, order processing, warehouse automation, EDI integration, financial management, and more. Visit our Features and Modules pages for detailed information, or contact us for a personalized overview."
        
        elif any(word in message_lower for word in ["contact", "email", "phone", "reach"]):
            return "You can reach us at:\n📧 Email: info@sparsus.com\n📞 Phone: +1 (212) 685-2127\n📍 Address: 112 West 34 Street Floor 18, New York, NY 10120\n\nOur business hours are Monday-Friday, 9:00 AM - 6:00 PM EST."
        
        elif any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm the SPARS AI Assistant. How can I help you today? I can answer questions about our ERP solution, features, modules, pricing, or help you get in touch with our sales team."
        
        else:
            return "Thank you for your message! For detailed information about SPARS, please visit our website or contact our sales team at info@sparsus.com or +1 (212) 685-2127. They'll be happy to assist you with any questions."

