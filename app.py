import sys
import os
import logging
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from src.database import Database
from src.agents.chatbot import chat_bot
from src.agents.scraper import scraper_agent
from src.agents.lecturer import lecturer_agent

project_root = os.path.abspath(os.path.join(os.getcwd(), '..')) 
if project_root not in sys.path:
    sys.path.append(project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

db = Database()

@app.route('/')
def landing_page():
    """Renders the Marketing Landing Page"""
    return render_template('landing.html')

@app.route('/product')
def product_page():
    """Renders the Main Application (Agent Interface)"""
    return render_template('product.html')

@app.route('/api/landing-chat', methods=['POST'])
def landing_chat():
    """
    Endpoint for the Chat Bot (Landing Page).
    Fast response, sales-focused.
    """
    try:
        data = request.json
        user_msg = data.get('message', '').strip()
        
        if not user_msg:
            return jsonify({"response": "I'm listening..."})
        
        response = chat_bot(user_msg)
        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Landing API Error: {e}")
        return jsonify({"response": "I'm having a brief brain freeze. Try again?"}), 500

@app.route('/api/agent-lecture', methods=['POST'])
def agent_lecture():
    """
    Endpoint for the Professor Agent (Product Page).
    Handles the orchestration: Scrape -> Context -> Lecture Stream -> Save DB.
    """
    data = request.json
    user_msg = data.get('message', '').strip()
    session_id = data.get('session_id', 'guest')

    if not user_msg:
         return Response("Please enter a topic.", mimetype='text/plain')

    db.add_message(session_id, 'user', user_msg)

    def generate():
        try:

            yield f"**🔍 Agent 1 (Researcher):** Scanning the web for recent info on '{user_msg}'...\n\n"
            
            scraped_context = scraper_agent(user_msg)
            
            yield "**✅ Data Acquired.** Handing off to Professor Agent.\n\n---\n\n"
            
            full_response = ""
            for chunk in lecturer_agent(user_msg, scraped_context):
                full_response += chunk
                yield chunk
            
            db.add_message(session_id, 'assistant', full_response)
            
        except Exception as e:
            logger.error(f"Agent Loop Error: {e}")
            yield f"\n\n**System Error:** {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)