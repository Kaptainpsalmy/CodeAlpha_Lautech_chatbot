// ===== ADVANCED UTILITY FUNCTIONS =====

// Generate a unique session ID for this chat session
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Get or create session ID from localStorage
function getSessionId() {
    let sessionId = localStorage.getItem('lautech_session_id');
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('lautech_session_id', sessionId);
    }
    return sessionId;
}

// Format timestamp to readable time
function formatTimestamp(date = new Date()) {
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const formattedHours = hours % 12 || 12;
    const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;
    return `${formattedHours}:${formattedMinutes} ${ampm}`;
}

// Format date for message grouping
function formatMessageDate(date) {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
        });
    }
}

// ===== ADVANCED COPY TO CLIPBOARD =====
async function copyToClipboard(text, buttonElement = null) {
    try {
        await navigator.clipboard.writeText(text);

        // Visual feedback on button
        if (buttonElement) {
            const originalHTML = buttonElement.innerHTML;
            buttonElement.innerHTML = '<i class="fas fa-check"></i>';
            buttonElement.classList.add('copy-success');

            setTimeout(() => {
                buttonElement.innerHTML = originalHTML;
                buttonElement.classList.remove('copy-success');
            }, 1500);
        }

        showToast('✓ Copied to clipboard!', 'success', 1500);
        return true;

    } catch (err) {
        console.error('Failed to copy:', err);

        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();

        try {
            document.execCommand('copy');
            showToast('✓ Copied to clipboard!', 'success', 1500);
            return true;
        } catch (e) {
            showToast('❌ Failed to copy text', 'error');
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    }
}

// ===== ADVANCED TEXT TO SPEECH =====
class TextToSpeech {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
        this.isPlaying = false;
        this.currentButton = null;
        this.voices = [];
        this.selectedVoice = null;

        // Load available voices
        this.loadVoices();

        // Chrome loads voices asynchronously
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = () => this.loadVoices();
        }
    }

    loadVoices() {
        this.voices = this.synth.getVoices();

        // Try to find a nice Nigerian English voice or default to any English voice
        this.selectedVoice = this.voices.find(voice =>
            voice.lang.includes('en-NG') ||
            voice.name.includes('Nigeria') ||
            voice.name.includes('Google UK') ||
            voice.name.includes('Microsoft David')
        ) || this.voices.find(voice => voice.lang.includes('en'));
    }

    speak(text, buttonElement = null) {
        // Cancel any ongoing speech
        this.stop();

        // Create new utterance
        this.utterance = new SpeechSynthesisUtterance(text);

        // Configure voice
        if (this.selectedVoice) {
            this.utterance.voice = this.selectedVoice;
        }

        // Configure settings
        this.utterance.lang = 'en-US';
        this.utterance.rate = 1.0;
        this.utterance.pitch = 1.0;
        this.utterance.volume = 1;

        // Event handlers
        this.utterance.onstart = () => {
            this.isPlaying = true;
            this.currentButton = buttonElement;
            if (buttonElement) {
                buttonElement.innerHTML = '<i class="fas fa-stop"></i>';
                buttonElement.classList.add('speaking');
                buttonElement.title = 'Stop';
            }
        };

        this.utterance.onend = () => {
            this.isPlaying = false;
            if (buttonElement) {
                buttonElement.innerHTML = '<i class="fas fa-volume-up"></i>';
                buttonElement.classList.remove('speaking');
                buttonElement.title = 'Listen to answer';
            }
            this.currentButton = null;
        };

        this.utterance.onerror = (event) => {
            console.error('Speech error:', event);
            this.isPlaying = false;
            if (buttonElement) {
                buttonElement.innerHTML = '<i class="fas fa-volume-up"></i>';
                buttonElement.classList.remove('speaking');
            }
            showToast('Error playing speech', 'error');
        };

        // Start speaking
        this.synth.speak(this.utterance);
    }

    stop() {
        if (this.synth.speaking) {
            this.synth.cancel();
            this.isPlaying = false;

            if (this.currentButton) {
                this.currentButton.innerHTML = '<i class="fas fa-volume-up"></i>';
                this.currentButton.classList.remove('speaking');
                this.currentButton.title = 'Listen to answer';
            }
        }
    }

    toggle(text, buttonElement) {
        if (this.isPlaying) {
            this.stop();
        } else {
            this.speak(text, buttonElement);
        }
    }

    getVoices() {
        return this.voices;
    }

    setVoice(voiceName) {
        const voice = this.voices.find(v => v.name === voiceName);
        if (voice) {
            this.selectedVoice = voice;
            localStorage.setItem('preferred_voice', voiceName);
        }
    }
}

// Create global TTS instance
const tts = new TextToSpeech();

// ===== ENHANCED TOAST NOTIFICATIONS =====
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        // Create toast container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    // Choose icon based on type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';

    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Remove toast after duration
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

// ===== CHAT HISTORY MANAGEMENT =====
const MAX_HISTORY_ITEMS = 100;

function saveChatToStorage(messages) {
    try {
        // Only save last MAX_HISTORY_ITEMS messages
        const messagesToSave = messages.slice(-MAX_HISTORY_ITEMS);

        // Add timestamp to each message
        const messagesWithTime = messagesToSave.map(msg => ({
            ...msg,
            savedAt: new Date().toISOString()
        }));

        localStorage.setItem('lautech_chat_history', JSON.stringify(messagesWithTime));
        localStorage.setItem('lautech_last_save', new Date().toISOString());

    } catch (e) {
        console.error('Failed to save chat history:', e);

        // If storage is full, clear old messages
        if (e.name === 'QuotaExceededError') {
            localStorage.removeItem('lautech_chat_history');
            showToast('Chat history cleared due to storage limit', 'warning');
        }
    }
}

function loadChatFromStorage() {
    try {
        const saved = localStorage.getItem('lautech_chat_history');
        return saved ? JSON.parse(saved) : [];
    } catch (e) {
        console.error('Failed to load chat history:', e);
        return [];
    }
}

function clearChatStorage() {
    localStorage.removeItem('lautech_chat_history');
    localStorage.removeItem('lautech_last_save');
    showToast('Chat history cleared', 'success');
}

function getChatStats() {
    const messages = loadChatFromStorage();
    const lastSave = localStorage.getItem('lautech_last_save');

    return {
        totalMessages: messages.length,
        userMessages: messages.filter(m => m.sender === 'user').length,
        aiMessages: messages.filter(m => m.sender === 'ai').length,
        lastSave: lastSave ? new Date(lastSave) : null
    };
}

// ===== SESSION MANAGEMENT =====
function getSessionStats() {
    const sessionId = getSessionId();
    const startTime = localStorage.getItem('lautech_session_start');

    if (!startTime) {
        localStorage.setItem('lautech_session_start', new Date().toISOString());
    }

    return {
        sessionId,
        startedAt: startTime ? new Date(startTime) : new Date(),
        messagesCount: loadChatFromStorage().length
    };
}

// ===== TYPING INDICATOR ANIMATIONS =====
class TypingIndicator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.dots = [];
        this.interval = null;
    }

    show() {
        if (!this.container) return;

        this.container.classList.add('active');
        this.container.innerHTML = '';

        // Create animated dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            dot.style.animationDelay = `${i * 0.2}s`;
            this.container.appendChild(dot);
        }

        // Add "thinking" text
        const text = document.createElement('span');
        text.textContent = 'AI is thinking...';
        this.container.appendChild(text);
    }

    hide() {
        if (!this.container) return;
        this.container.classList.remove('active');
        this.container.innerHTML = '';
    }
}

// ===== SUGGESTED QUESTIONS MANAGER =====
class SuggestedQuestions {
    constructor(containerId, onClickCallback) {
        this.container = document.getElementById(containerId);
        this.onClick = onClickCallback;
        this.questions = [];
    }

    async loadFromAPI(apiUrl) {
        try {
            const response = await fetch(apiUrl);
            if (response.ok) {
                const data = await response.json();
                this.questions = data.suggestions || [];
                this.render();
            }
        } catch (error) {
            console.log('Could not load suggestions:', error);
            // Fallback suggestions
            this.questions = [
                "What is the cut-off mark for Medicine?",
                "How much are school fees?",
                "Where is the best area to live?",
                "Does LAUTECH accept second choice?",
                "How do I check admission status?",
                "What documents are needed for verification?"
            ];
            this.render();
        }
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = '';

        this.questions.forEach(question => {
            const chip = document.createElement('button');
            chip.className = 'chip';
            chip.innerHTML = `<i class="fas fa-question-circle"></i> ${question}`;
            chip.addEventListener('click', () => this.onClick(question));
            this.container.appendChild(chip);
        });
    }

    updateBasedOnContext(context) {
        // Filter suggestions based on conversation context
        // This could be enhanced with ML later
        if (context.includes('fee') || context.includes('pay')) {
            // Show fee-related suggestions
            this.questions = [
                "How much are school fees?",
                "Can I pay in installments?",
                "How do I pay my school fees?"
            ];
        } else if (context.includes('hostel') || context.includes('live')) {
            this.questions = [
                "Does school provide hostel?",
                "Which area is cheapest?",
                "Which area is safest?"
            ];
        }
        this.render();
    }
}

// ===== DETECT MOBILE DEVICE =====
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// ===== DEBOUNCE FUNCTION =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== TRUNCATE TEXT =====
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// ===== ESCAPE HTML (prevent XSS) =====
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ===== DETECT LINKS IN TEXT =====
function linkify(text) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function(url) {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="message-link">${url}</a>`;
    });
}

// ===== EXPORT FUNCTIONS =====
window.utils = {
    generateSessionId,
    getSessionId,
    formatTimestamp,
    formatMessageDate,
    copyToClipboard,
    tts,
    showToast,
    saveChatToStorage,
    loadChatFromStorage,
    clearChatStorage,
    getChatStats,
    getSessionStats,
    TypingIndicator,
    SuggestedQuestions,
    isMobileDevice,
    debounce,
    truncateText,
    escapeHtml,
    linkify
};