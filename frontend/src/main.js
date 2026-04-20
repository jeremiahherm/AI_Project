// ── State ──
const state = {
  messages: [],
  isTyping: false,
};

// ── DOM refs ──
const messagesWrapper = document.getElementById('messagesWrapper');
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const banner = document.getElementById('banner');

// ── Placeholder responses ──
const placeholderReplies = [
  "This is a placeholder response. Your model will reply here.",
  "Response from your model will appear in this space.",
  "Placeholder: connect your model to replace this text.",
  "Your model's response goes here.",
  "We fired our intern. No more replies."
];
let replyIndex = 0;

async function fetchModelReply(_messages) {
  // TODO: replace with your model API call
  // Example:
  // const res = await fetch('/api/chat', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ messages: _messages }),
  // });
  // const data = await res.json();
  // return data.reply;

  await new Promise(r => setTimeout(r, 800 + Math.random() * 600));
  return placeholderReplies[replyIndex++ % placeholderReplies.length];
}

// ── Helpers ──
function formatTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    messagesWrapper.scrollTo({ top: messagesWrapper.scrollHeight, behavior: 'smooth' });
  });
}

// ── Render a message bubble ──
function appendMessage(role, text) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  msg.innerHTML = `
    <div class="msg-avatar">${role === 'user' ? 'U' : 'A'}</div>
    <div class="msg-body">
      <div class="msg-content">${escapeHtml(text)}</div>
      <div class="msg-time">${formatTime()}</div>
    </div>
  `;
  messagesContainer.appendChild(msg);
  state.messages.push({ role, content: text });
  scrollToBottom();
}

// ── Typing indicator ──
function showTyping() {
  const el = document.createElement('div');
  el.id = 'typingIndicator';
  el.className = 'message assistant';
  el.innerHTML = `
    <div class="msg-avatar">A</div>
    <div class="msg-body">
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  messagesContainer.appendChild(el);
  scrollToBottom();
}

function hideTyping() {
  document.getElementById('typingIndicator')?.remove();
}

// ── Send flow ──
async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text || state.isTyping) return;

  messageInput.value = '';
  autoResize();
  setInputEnabled(false);

  appendMessage('user', text);

  state.isTyping = true;
  showTyping();

  try {
    const reply = await fetchModelReply(state.messages);
    hideTyping();
    appendMessage('assistant', reply);
  } catch (err) {
    hideTyping();
    appendMessage('assistant', 'Something went wrong. Please try again.');
    console.error('Model error:', err);
  } finally {
    state.isTyping = false;
    setInputEnabled(true);
    messageInput.focus();
  }
}

// ── Input helpers ──
function setInputEnabled(enabled) {
  messageInput.disabled = !enabled;
  sendBtn.disabled = !enabled || messageInput.value.trim().length === 0;
}

function autoResize() {
  messageInput.style.height = 'auto';
  messageInput.style.height = Math.min(messageInput.scrollHeight, 180) + 'px';
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}

// ── Event listeners ──
messageInput.addEventListener('input', () => {
  autoResize();
  sendBtn.disabled = messageInput.value.trim().length === 0 || state.isTyping;
});

messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

function drawBanner() {
  return `
    <div class="banner-content">
      <h1>Welcome to Your AI Chatbot</h1>
      <p>Type a message and see how your model responds!</p>
    </div>
  `
}

sendBtn.addEventListener('click', sendMessage);

// ── Init ──
messageInput.focus();
