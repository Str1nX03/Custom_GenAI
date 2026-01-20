from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

def scraper_agent(topic: str) -> str:
    """
    Real-time web scraper using DuckDuckGo.
    Fetches top 3 results to provide context for the lecture.
    """
    logger.info(f"Scraper Agent activated for topic: {topic}")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=3))
        
        if not results:
            logger.warning(f"No search results found for: {topic}")
            return "No specific web results found. Proceeding with internal knowledge base."

        context_parts = []
        for i, res in enumerate(results):
            title = res.get('title', 'Unknown Title')
            body = res.get('body', '')
            context_parts.append(f"Source {i+1} [{title}]: {body}")
        
        final_context = "\n\n".join(context_parts)
        logger.info(f"Scrape successful. Context length: {len(final_context)} chars")
        
        return final_context

    except Exception as e:
        logger.error(f"Scraper Agent Critical Error: {e}")
        return f"Error accessing live web data ({str(e)}). Proceeding with internal training data."