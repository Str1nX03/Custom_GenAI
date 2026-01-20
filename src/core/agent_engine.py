import os
import logging
import time
from typing import List, Dict, Optional
from groq import Groq

# Configure logging to track performance and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    """
    A production-ready, lightweight wrapper around the Groq API.
    Designed to replace heavy frameworks like LangChain for specific tasks.
    
    Attributes:
        client (Groq): The authenticated Groq client.
        model_name (str): The specific LLM to use (e.g., llama3-70b-8192).
        system_prompt (str): The persona and instructions for the agent.
        memory (List[Dict]): Ephemeral memory for the current session context.
    """
    def __init__(self, 
                 system_prompt: str, 
                 model_name: str = "llama3-70b-8192", 
                 temperature: float = 0.5):
        
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.critical("❌ GROQ_API_KEY is missing from environment variables. Agent cannot function.")
            # We don't raise an error here to allow app startup, but run() will fail gracefully.

        self.client = Groq(api_key=self.api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt
        
        # Local memory buffer. 
        # Note: Long-term persistence is handled by the Database class in app.py.
        # This memory is for the immediate instantiation context.
        self.memory: List[Dict[str, str]] = []

    def run(self, user_input: str, retries: int = 2) -> str:
        """
        Executes a single turn of conversation with the LLM.
        
        Args:
            user_input (str): The user's message.
            retries (int): Number of times to retry if the API call fails.
            
        Returns:
            str: The LLM's response content.
        """
        if not self.api_key:
            return "System Error: API Key missing. Please check server logs."

        # Construct the message payload
        # 1. System Prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 2. Add History (if any exists in this session instance)
        messages.extend(self.memory)
        
        # 3. Current User Input
        messages.append({"role": "user", "content": user_input})
        
        # Execute with Retry Logic
        for attempt in range(retries + 1):
            try:
                start_time = time.time()
                
                # Call Groq API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=1024, # Safety limit to prevent runaway generation
                    top_p=1,
                    stream=False
                )
                
                elapsed = time.time() - start_time
                logger.info(f"Groq Inference: {elapsed:.2f}s | Model: {self.model_name}")

                content = response.choices[0].message.content
                
                # Update local short-term memory
                self.memory.append({"role": "user", "content": user_input})
                self.memory.append({"role": "assistant", "content": content})
                
                return content

            except Exception as e:
                logger.warning(f"Groq Attempt {attempt + 1}/{retries + 1} failed: {e}")
                
                if attempt < retries:
                    # Exponential-ish backoff (1s, 2s...)
                    time.sleep(1 * (attempt + 1)) 
                else:
                    logger.error("All retries exhausted.")
                    return "I'm currently experiencing high traffic or connection issues. Please try again later."