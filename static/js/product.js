const container = document.getElementById('lecture-container');
const topicInput = document.getElementById('topic-input');
const sendBtn = document.getElementById('send-btn');

// Generate a random session ID for this tab session
const sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);

async function startLesson() {
    const topic = topicInput.value.trim();
    if (!topic) return;

    // 1. UI State: Lock Input & Show Loading
    topicInput.disabled = true;
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
    sendBtn.classList.add('opacity-75', 'cursor-not-allowed');

    // Clear previous content with a clean fade
    container.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full space-y-6 animate-fade-in">
            <div class="relative">
                <div class="w-16 h-16 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
                <i class="fa-solid fa-magnifying-glass absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-indigo-600"></i>
            </div>
            <div class="text-center">
                <div class="text-slate-800 font-bold text-lg">Agent 1: Researching</div>
                <div class="text-slate-500 text-sm mt-1">Scanning DuckDuckGo for '${topic}'...</div>
            </div>
        </div>
    `;

    try {
        // 2. Initiate Stream Request
        const response = await fetch('/api/agent-lecture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: topic,
                session_id: sessionId
            })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        // 3. Prepare for Stream Reading
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';
        
        // Replace loading spinner with the content container
        container.innerHTML = '<div class="prose max-w-none pb-24 animate-fade-in pl-2 pr-2"></div>';
        const contentDiv = container.querySelector('.prose');

        // 4. Read the Stream Loop
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            
            // Render Markdown
            // Note: In production, you might want to sanitize this, but marked handles basic XSS well enough for this demo
            contentDiv.innerHTML = marked.parse(fullText);
            
            // Smart Auto-Scroll: Only scroll if user hasn't scrolled up significantly
            const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 200;
            if (isNearBottom) {
                container.scrollTo({
                    top: container.scrollHeight,
                    behavior: 'smooth'
                });
            }
        }

    } catch (error) {
        console.error(error);
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-red-500 animate-fade-in">
                <i class="fa-solid fa-triangle-exclamation text-4xl mb-4 text-red-100 bg-red-500 rounded-full p-4"></i>
                <h3 class="text-lg font-bold text-slate-800">Connection Error</h3>
                <p class="text-slate-500 mt-2">Could not reach the Agent Engine.</p>
                <button onclick="window.location.reload()" class="mt-4 text-indigo-600 font-bold hover:underline">Try Refreshing</button>
            </div>
        `;
    } finally {
        // 5. Reset Input State (Optional: Keep it disabled to force new session or allow new topic)
        topicInput.value = '';
        topicInput.disabled = false;
        topicInput.focus();
        
        sendBtn.disabled = false;
        sendBtn.innerHTML = 'Teach Me <i class="fa-solid fa-paper-plane text-xs"></i>';
        sendBtn.classList.remove('opacity-75', 'cursor-not-allowed');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    topicInput.focus();
});

topicInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') startLesson();
});