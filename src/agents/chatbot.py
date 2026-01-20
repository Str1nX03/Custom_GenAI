from src.core.agent_engine import Agent
import logging

logger = logging.getLogger(__name__)

def chat_bot(user_message: str) -> str:
    """
    Fast, sales-oriented chatbot for the landing page.
    Uses llama-3.1-8b-instant for low latency.
    """
    try:
        system_prompt = """
        IDENTITY:
        You are 'Aura', the virtual concierge for GenAI Edu.
        
        GOAL:
        Your goal is to briefly explain that we use Multi-Agent Systems to generate custom lectures.
        Encourage the user to click "Launch Agent" to try the full product.
        
        RULES:
        1. Keep answers under 30 words.
        2. Be professional, enthusiastic, and inviting.
        3. Do not try to teach the user here; refer them to the Product Page.
        """
        
        # Initialize the Agent with the fast model
        agent = Agent(
            system_prompt=system_prompt,
            model_name="llama-3.1-8b-instant", 
            temperature=0.7
        )
        
        return agent.run(user_message)
        
    except Exception as e:
        logger.error(f"Concierge Bot Error: {e}")
        return "I'm currently offline, but our main agents are working perfectly. Please click 'Launch Agent' above!"