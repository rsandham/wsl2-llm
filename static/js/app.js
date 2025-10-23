// Global chat history
let chatHistory = [];

/**
 * Switch between tabs
 */
function switchTab(tabName, element) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    element.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

/**
 * Get request headers including API key if present
 */
function getHeaders() {
    const apiKey = document.getElementById('api-key');
    const headers = {'Content-Type': 'application/json'};
    if (apiKey && apiKey.value) {
        headers['X-API-Key'] = apiKey.value;
    }
    return headers;
}

/**
 * Generate text from prompt
 */
async function generate() {
    const output = document.getElementById('gen-output');
    const stats = document.getElementById('gen-stats');
    output.innerHTML = '<div class="loading"><div class="spinner"></div>Generating...</div>';
    stats.innerHTML = '';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                prompt: document.getElementById('gen-prompt').value,
                max_new_tokens: parseInt(document.getElementById('gen-tokens').value),
                temperature: parseFloat(document.getElementById('gen-temp').value)
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            output.textContent = data.generated_text;
            stats.innerHTML = `
                <div class="stat">⏱️ ${data.time_seconds}s</div>
                <div class="stat">📝 ${data.tokens_generated} tokens</div>
                <div class="stat">⚡ ${data.tokens_per_second} tok/s</div>
            `;
        } else {
            output.textContent = 'Error: ' + (data.detail || 'Unknown error');
        }
    } catch (error) {
        output.textContent = 'Error: ' + error.message;
    }
}

/**
 * Complete code snippet
 */
async function complete() {
    const output = document.getElementById('complete-output');
    output.innerHTML = '<div class="loading"><div class="spinner"></div>Completing...</div>';
    
    try {
        const response = await fetch('/complete', {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                code: document.getElementById('code-input').value,
                max_new_tokens: parseInt(document.getElementById('complete-tokens').value),
                temperature: parseFloat(document.getElementById('complete-temp').value)
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            output.textContent = data.full_code;
        } else {
            output.textContent = 'Error: ' + (data.detail || 'Unknown error');
        }
    } catch (error) {
        output.textContent = 'Error: ' + error.message;
    }
}

/**
 * Send chat message
 */
async function sendChat() {
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    const userMessage = input.value.trim();
    
    if (!userMessage) return;
    
    chatHistory.push({role: 'user', content: userMessage});
    updateChatUI();
    input.value = '';
    
    messages.innerHTML += '<div class="loading"><div class="spinner"></div>Thinking...</div>';
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                messages: chatHistory,
                max_new_tokens: 512,
                temperature: 0.7
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            chatHistory.push({role: 'assistant', content: data.response});
            updateChatUI();
        } else {
            messages.innerHTML += `<div class="message">Error: ${data.detail || 'Unknown error'}</div>`;
        }
    } catch (error) {
        messages.innerHTML += `<div class="message">Error: ${error.message}</div>`;
    }
}

/**
 * Update chat UI with message history
 */
function updateChatUI() {
    const messages = document.getElementById('chat-messages');
    messages.innerHTML = chatHistory.map(msg => `
        <div class="message ${msg.role}">
            <div class="message-role">${msg.role}</div>
            <div>${msg.content}</div>
        </div>
    `).join('');
    messages.scrollTop = messages.scrollHeight;
}

/**
 * Process batch of prompts
 */
async function batchProcess() {
    const output = document.getElementById('batch-output');
    const prompts = document.getElementById('batch-prompts').value
        .split('\n')
        .filter(p => p.trim());
    
    if (prompts.length === 0) {
        output.textContent = 'Please enter at least one prompt';
        return;
    }
    
    output.innerHTML = '<div class="loading"><div class="spinner"></div>Processing batch...</div>';
    
    try {
        const response = await fetch('/batch', {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                prompts: prompts,
                max_new_tokens: parseInt(document.getElementById('batch-tokens').value),
                temperature: 0.7
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            let result = `✅ Processed ${data.successful}/${data.total_prompts} prompts in ${data.time_seconds}s\n\n`;
            data.results.forEach((r, i) => {
                result += `\n━━━ Prompt ${i + 1} ━━━\n`;
                result += `${r.prompt}\n\n`;
                result += `Generated:\n${r.generated_text}\n`;
            });
            output.textContent = result;
        } else {
            output.textContent = 'Error: ' + (data.detail || 'Unknown error');
        }
    } catch (error) {
        output.textContent = 'Error: ' + error.message;
    }
}

/**
 * Initialize event listeners when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Enter key support for chat
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChat();
            }
        });
    }
});
