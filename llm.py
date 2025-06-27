import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class LLM:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM class with Gemini API.
        
        Args:
            api_key (str, optional): Google API key. If not provided, 
                will look for GOOGLE_API_KEY, GOOGLE_API, or GEMINI_API_KEY environment variables.
        """
        # Try multiple possible environment variable names
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = (
                os.getenv("GOOGLE_API_KEY") or 
                os.getenv("GOOGLE_API") or 
                os.getenv("GEMINI_API_KEY")
            )
        
        if not self.api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY, GOOGLE_API, or GEMINI_API_KEY "
                "environment variable or pass api_key parameter."
            )
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.chat = None
    
    def llm_call(self, messages: List[Dict[str, str]]) -> str:
        """
        Make a call to the Gemini 2.5 Pro model.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries 
                with 'role' and 'content' keys.
                Example: [{"role": "user", "content": "Hello"}, 
                         {"role": "assistant", "content": "Hi there!"}]
        
        Returns:
            str: The model's response content
        """
        try:
            # Convert messages to Gemini format if needed
            gemini_messages = self._convert_messages_to_gemini_format(
                messages
            )
            
            # Generate response
            response = self.model.generate_content(gemini_messages)
            
            # Return the response text
            return response.text
            
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {str(e)}")
    
    def start_chat(self):
        """Start a new chat session."""
        self.chat = self.model.start_chat(history=[])
    
    def chat_call(self, message: str) -> str:
        """
        Make a call in an ongoing chat session.
        
        Args:
            message (str): The user's message
        
        Returns:
            str: The model's response
        """
        if not self.chat:
            self.start_chat()
        
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            raise Exception(f"Error in chat call: {str(e)}")
    
    def _convert_messages_to_gemini_format(
        self, messages: List[Dict[str, str]]
    ) -> str:
        """
        Convert OpenAI-style messages to Gemini format.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries
        
        Returns:
            str: Combined text for Gemini
        """
        formatted_text = ""
        
        for message in messages:
            role = message.get("role", "").lower()
            content = message.get("content", "")
            
            if role == "user":
                formatted_text += f"User: {content}\n"
            elif role == "assistant":
                formatted_text += f"Assistant: {content}\n"
            elif role == "system":
                formatted_text += f"System: {content}\n"
        
        return formatted_text.strip()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model_name": "gemini-2.5-pro",
            "provider": "Google",
            "api_key_configured": bool(self.api_key)
        }