import os
from groq import Groq
import logging

logger = logging.getLogger(__name__)

def lecturer_agent(topic: str, context: str):
    """
    Streaming Lecturer Agent.
    Combines User Topic + Scraped Context -> Structured Lesson.
    Yields chunks of text for real-time display.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        yield "Error: Groq API Key is missing."
        return

    client = Groq(api_key=api_key)
    
    # Detailed System Prompt for high-quality output
    system_prompt = f"""
    You are Professor X, an expert AI educator known for clarity and engagement.
    
    REQUESTED TOPIC: {topic}
    
    REAL-TIME WEB CONTEXT (Ground Truth):
    {context}
    
    INSTRUCTIONS:
    1. Synthesize the web context with your internal knowledge.
    2. Create a structured mini-lecture.
    
    STRUCTURE:
    - **Title**: Creative and Relevant.
    - **Introduction**: Brief overview to hook the student.
    - **Key Concepts**: Use bullet points for readability.
    - **Deep Dive**: Explain the most complex part simply (ELI5).
    - **Quiz**: One single multiple-choice question to test understanding.
    
    FORMATTING RULES:
    - Use Markdown (## Headers, **Bold**, *Italic*).
    - Do NOT use 'Introduction:' as a header, just write the introduction.
    - Keep it concise but informative.
    """
    
    try:
        # Call Groq with streaming enabled
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Using the larger model for better reasoning
            messages=[{"role": "user", "content": system_prompt}],
            stream=True,
            temperature=0.6,    # Slightly creative but focused
            max_tokens=2048     # Allow for a substantial lecture
        )
        
        # Yield chunks as they arrive
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        logger.error(f"Lecturer Agent Error: {e}")
        yield f"\n\n**Error generating lecture:** {str(e)}\n\nPlease try again in a moment."