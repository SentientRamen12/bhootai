import openai
import anthropic
import google.generativeai as genai
from typing import Dict, List, Optional, Any, Union
from config.configs import (
    LLM_PROVIDER, OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, LLM_MODELS
)

class LLMClient:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or LLM_PROVIDER
        self.model = LLM_MODELS.get(self.provider)
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                # Try to find any available provider
                if ANTHROPIC_API_KEY:
                    self.provider = "anthropic"
                    self.model = LLM_MODELS.get("anthropic")
                    self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                    print(f"OpenAI key not found, switching to Anthropic")
                    return
                elif GEMINI_API_KEY:
                    self.provider = "gemini"
                    self.model = LLM_MODELS.get("gemini")
                    genai.configure(api_key=GEMINI_API_KEY)
                    print(f"OpenAI key not found, switching to Gemini")
                    return
                else:
                    raise ValueError("No API keys found for any provider")
            openai.api_key = OPENAI_API_KEY
        elif self.provider == "anthropic":
            if not ANTHROPIC_API_KEY:
                # Try to find any available provider
                if OPENAI_API_KEY:
                    self.provider = "openai"
                    self.model = LLM_MODELS.get("openai")
                    openai.api_key = OPENAI_API_KEY
                    print(f"Anthropic key not found, switching to OpenAI")
                    return
                elif GEMINI_API_KEY:
                    self.provider = "gemini"
                    self.model = LLM_MODELS.get("gemini")
                    genai.configure(api_key=GEMINI_API_KEY)
                    print(f"Anthropic key not found, switching to Gemini")
                    return
                else:
                    raise ValueError("No API keys found for any provider")
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        elif self.provider == "gemini":
            if not GEMINI_API_KEY:
                # Try to find any available provider
                if OPENAI_API_KEY:
                    self.provider = "openai"
                    self.model = LLM_MODELS.get("openai")
                    openai.api_key = OPENAI_API_KEY
                    print(f"Gemini key not found, switching to OpenAI")
                    return
                elif ANTHROPIC_API_KEY:
                    self.provider = "anthropic"
                    self.model = LLM_MODELS.get("anthropic")
                    self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                    print(f"Gemini key not found, switching to Anthropic")
                    return
                else:
                    raise ValueError("No API keys found for any provider")
            genai.configure(api_key=GEMINI_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate(
        self, 
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: str = "",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using the configured LLM provider"""
        if self.provider == "openai":
            return self._generate_openai(system_prompt, messages, prompt, temperature, max_tokens)
        elif self.provider == "anthropic":
            return self._generate_anthropic(system_prompt, messages, prompt, temperature, max_tokens)
        elif self.provider == "gemini":
            return self._generate_gemini(system_prompt, messages, prompt, temperature, max_tokens)
    
    def _generate_openai(self, system_prompt: Optional[str], messages: Optional[List[Dict[str, str]]], prompt: str, temperature: float, max_tokens: Optional[int]) -> str:
        all_messages = []
        
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        
        if messages:
            all_messages.extend(messages)
        
        if prompt:
            all_messages.append({"role": "user", "content": prompt})
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _generate_anthropic(self, system_prompt: Optional[str], messages: Optional[List[Dict[str, str]]], prompt: str, temperature: float, max_tokens: Optional[int]) -> str:
        all_messages = []
        
        if messages:
            all_messages.extend(messages)
        
        if prompt:
            all_messages.append({"role": "user", "content": prompt})
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 1000,
            temperature=temperature,
            system=system_prompt,
            messages=all_messages
        )
        return response.content[0].text
    
    def _generate_gemini(self, system_prompt: Optional[str], messages: Optional[List[Dict[str, str]]], prompt: str, temperature: float, max_tokens: Optional[int]) -> str:
        model = genai.GenerativeModel(self.model)
        
        if messages:
            chat = model.start_chat(history=[])
            for msg in messages:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
                elif msg["role"] == "assistant":
                    # For Gemini, we need to simulate the assistant response
                    pass
            
            if prompt:
                response = chat.send_message(prompt)
            else:
                response = chat.send_message("Continue")
        else:
            # No history, use simple generation
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
        
        return response.text

# Convenience function
def llm_generate(
    system_prompt: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    prompt: str = "",
    provider: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """Convenience function for quick LLM calls"""
    client = LLMClient(provider)
    return client.generate(system_prompt, messages, prompt, temperature, max_tokens) 