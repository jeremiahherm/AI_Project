import { parseUserMessage, fetchTourResult } from './endpoint.js';
import { formatTourCard, escapeHtml } from './tourcard.js';

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
// Pass html=true to render formatted HTML instead of escaped text
function appendMessage(role, content, html = false) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  msg.innerHTML = `
    <div class="msg-avatar">${role === 'user' ? 'U' : 'A'}</div>
    <div class="msg-body">
      <div class="msg-content">${html ? content : escapeHtml(content)}</div>
      <div class="msg-time">${formatTime()}</div>
    </div>
  `;
  messagesContainer.appendChild(msg);
  state.messages.push({ role, content: html ? '[tour card]' : content });
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

  const tourRequest = parseUserMessage(text);
  if (!tourRequest) {
    appendMessage(
      'assistant',
      'Please use the format: City, YYYY-MM-DD to YYYY-MM-DD\nExample: Paris, 2026-10-01 to 2026-10-15'
    );
    setInputEnabled(true);
    messageInput.focus();
    return;
  }

  state.isTyping = true;
  showTyping();

  try {
    const tour = await fetchTourResult(tourRequest);
    hideTyping();
    appendMessage('assistant', formatTourCard(tour), true);
  } catch (err) {
    hideTyping();
    appendMessage('assistant', `Something went wrong: ${err.message}`);
    console.error('API error:', err);
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
  `;
}

sendBtn.addEventListener('click', sendMessage);

// ── Init ──
messageInput.focus();