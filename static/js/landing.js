const chatContent = document.getElementById('chat-wrapper');
const toggleIcon = document.getElementById('toggle-icon');
let isOpen = false;

// Toggle Chat Widget Visibility
function toggleChat() {
    isOpen = !isOpen;
    if (isOpen) {
        chatContent.classList.remove('chat-hidden');
        chatContent.classList.add('chat-visible');
        toggleIcon.classList.add('rotate-180');
        toggleIcon.classList.remove('fa-comment-dots');
        toggleIcon.classList.add('fa-xmark');
    } else {
        chatContent.classList.remove('chat-visible');
        chatContent.classList.add('chat-hidden');
        toggleIcon.classList.remove('rotate-180');
        toggleIcon.classList.remove('fa-xmark');
        toggleIcon.classList.add('fa-comment-dots');
    }
}

// Send Message Logic
async function sendLandingMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    // 1. Append User Message
    appendMessage(text, 'user');
    input.value = '';
    
    // 2. Show Typing Indicator
    showTyping();

    try {
        // 3. Send to Backend Agent
        const res = await fetch('/api/landing-chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        
        // 4. Remove Typing & Append Bot Response
        removeTyping();
        appendMessage(data.response, 'bot');
    } catch (e) {
        removeTyping();
        appendMessage("I'm having trouble connecting to the server.", 'bot');
        console.error(e);
    }
}

// Helper: Append Message to DOM
function appendMessage(text, sender) {
    const messages = document.getElementById('chat-messages');
    const div = document.createElement('div');
    
    // Styling based on sender
    const classes = sender === 'user' 
        ? 'bg-indigo-600 text-white self-end rounded-tr-none' 
        : 'bg-slate-100 text-slate-800 self-start rounded-tl-none';
    
    div.className = `p-3 rounded-lg text-sm max-w-[85%] ${classes} animate-fade-in shadow-sm`;
    div.innerText = text;
    
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// Helper: Show Typing Dots
function showTyping() {
    const messages = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.id = 'typing-indicator';
    div.className = 'bg-slate-100 p-3 rounded-lg rounded-tl-none self-start mb-2 w-14 flex gap-1 items-center justify-center animate-fade-in shadow-sm';
    div.innerHTML = `
        <div class="w-1.5 h-1.5 bg-slate-400 rounded-full typing-dot"></div>
        <div class="w-1.5 h-1.5 bg-slate-400 rounded-full typing-dot"></div>
        <div class="w-1.5 h-1.5 bg-slate-400 rounded-full typing-dot"></div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// Helper: Remove Typing Dots
function removeTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

// Listen for Enter Key
document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendLandingMessage();
});