// ===== LAUTECH CHATBOT - MAIN CHAT FUNCTIONALITY =====

class LautechChatbot {
    constructor() {
        this.messages = [];
        this.sessionId = utils.getSessionId();
        this.isTyping = false;
        this.apiUrl = 'http://localhost:5000/api';
        this.isUserScrolled = false; // Track if user manually scrolled

        // DOM Elements
        this.chatMessages = document.getElementById('chatMessages');
        this.welcomeSection = document.getElementById('welcomeSection');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearChatBtn = document.getElementById('clearChat');
        this.themeToggle = document.getElementById('themeToggle');
        this.suggestedQuestions = document.getElementById('suggestedQuestions');

        // Initialize
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadChatHistory();
        this.adjustTextareaHeight();
        this.loadSuggestions();

        // Focus input on desktop
        if (!utils.isMobileDevice()) {
            this.userInput.focus();
        }

        // Check if backend is reachable
        this.checkBackendHealth();

        // Set up scroll detection
        this.setupScrollDetection();
    }

    setupScrollDetection() {
        this.chatMessages.addEventListener('scroll', () => {
            const { scrollTop, scrollHeight, clientHeight } = this.chatMessages;
            const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
            this.isUserScrolled = !isAtBottom;
        });
    }

    async checkBackendHealth() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            if (response.ok) {
                console.log('✅ Backend connection successful');
                utils.showToast('Connected to server', 'success');
            } else {
                console.warn('⚠️ Backend returned error');
                utils.showToast('Server connection issue', 'error');
            }
        } catch (error) {
            console.error('❌ Cannot connect to backend:', error);
            utils.showToast('Cannot connect to server. Make sure backend is running on port 5000', 'error');
        }
    }

    setupEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Send message on Enter (but Shift+Enter for new line)
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Adjust textarea height as user types
        this.userInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
            this.toggleSendButton();
        });

        // Clear chat button
        if (this.clearChatBtn) {
            this.clearChatBtn.addEventListener('click', () => this.clearChat());
        }

        // Theme toggle
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    adjustTextareaHeight() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = Math.min(this.userInput.scrollHeight, 120) + 'px';
    }

    toggleSendButton() {
        const hasText = this.userInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText;
    }

    async sendMessage() {
        const messageText = this.userInput.value.trim();
        if (!messageText) return;

        // Clear input and reset height
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        this.toggleSendButton();

        // Hide welcome section if visible
        if (this.welcomeSection && !this.welcomeSection.classList.contains('hidden')) {
            this.welcomeSection.classList.add('hidden');
        }

        // Add user message to UI
        this.addMessage(messageText, 'user');

        // Force scroll to bottom for user message
        this.forceScrollToBottom();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend and get response
            const response = await this.getBotResponse(messageText);

            // Hide typing indicator
            this.hideTypingIndicator();

            // Add bot response to UI
            this.addMessage(
                response.answer,
                'ai',
                response.confidence,
                response.match_type,
                response.suggestions
            );

            // Save to storage
            this.saveMessages();

        } catch (error) {
            console.error('Error getting response:', error);
            this.hideTypingIndicator();

            // Show error message
            this.addMessage(
                "I'm having trouble connecting right now. Please check if the backend server is running.",
                'ai',
                null,
                null,
                null,
                true
            );

            utils.showToast('Connection error. Make sure backend is running on port 5000', 'error');
        }
    }

    async getBotResponse(question) {
        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    async loadSuggestions() {
        try {
            console.log('Loading suggestions from API...');
            const response = await fetch(`${this.apiUrl}/chat/suggestions`);

            if (response.ok) {
                const data = await response.json();
                console.log('Suggestions received:', data);
                this.updateSuggestedQuestions(data.suggestions);
            } else {
                console.warn('Failed to load suggestions, using fallback');
                this.useFallbackSuggestions();
            }
        } catch (error) {
            console.log('Could not load suggestions, using fallback:', error);
            this.useFallbackSuggestions();
        }
    }

    useFallbackSuggestions() {
        const fallbackSuggestions = [
            "What is the cut-off mark for Medicine?",
            "How much are school fees?",
            "Where is the best area to live?",
            "Does LAUTECH accept second choice?",
            "How do I check admission status?",
            "What documents are needed for verification?"
        ];
        this.updateSuggestedQuestions(fallbackSuggestions);
    }

    updateSuggestedQuestions(suggestions) {
        const chipsContainer = document.getElementById('questionChips') ||
                              document.querySelector('.question-chips');

        if (!chipsContainer) {
            console.error('Could not find chips container!');
            return;
        }

        chipsContainer.innerHTML = '';

        suggestions.forEach(question => {
            const chip = document.createElement('button');
            chip.className = 'chip';
            chip.innerHTML = `<i class="fas fa-question-circle"></i> ${question}`;
            chip.addEventListener('click', () => {
                this.userInput.value = question;
                this.sendMessage();

                if (this.welcomeSection && !this.welcomeSection.classList.contains('hidden')) {
                    this.welcomeSection.classList.add('hidden');
                }
            });
            chipsContainer.appendChild(chip);
        });

        console.log(`Added ${suggestions.length} suggestion chips`);
    }

    addMessage(text, sender, confidence = null, matchType = null, suggestions = null, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}${isError ? ' error' : ''}`;

        const timestamp = utils.formatTimestamp();
        const formattedText = utils.linkify(utils.escapeHtml(text)).replace(/\n/g, '<br>');

        let messageHTML = `
            <div class="message-content">
                <div class="message-text">
                    ${formattedText}
                </div>
        `;

        if (suggestions && suggestions.length > 0) {
            messageHTML += `
                <div class="suggestions-container">
                    <p class="suggestions-title">Did you mean:</p>
                    <div class="suggestion-chips">
            `;
            suggestions.forEach(sugg => {
                messageHTML += `
                    <button class="suggestion-chip" data-question="${utils.escapeHtml(sugg.question)}">
                        ${utils.escapeHtml(sugg.question)}
                    </button>
                `;
            });
            messageHTML += `</div></div>`;
        }

        messageHTML += `
                <div class="message-meta">
                    <span class="timestamp">${timestamp}</span>
                    <div class="message-actions">
                        ${sender === 'ai' ? `
                            <button class="copy-btn" title="Copy to clipboard">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button class="speak-btn" title="Listen to answer">
                                <i class="fas fa-volume-up"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
                ${confidence ? `<div class="confidence-badge">${Math.round(confidence * 100)}% match</div>` : ''}
            </div>
        `;

        messageDiv.innerHTML = messageHTML;
        this.chatMessages.appendChild(messageDiv);

        if (sender === 'ai') {
            const copyBtn = messageDiv.querySelector('.copy-btn');
            const speakBtn = messageDiv.querySelector('.speak-btn');

            if (copyBtn) {
                copyBtn.addEventListener('click', (e) => {
                    utils.copyToClipboard(text, e.currentTarget);
                });
            }

            if (speakBtn) {
                speakBtn.addEventListener('click', (e) => {
                    utils.tts.toggle(text, e.currentTarget);
                });
            }
        }

        messageDiv.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const question = chip.dataset.question;
                this.userInput.value = question;
                this.sendMessage();
            });
        });

        // Scroll to show new message
        this.smartScrollToBottom();

        // Store message
        this.messages.push({
            text,
            sender,
            timestamp,
            confidence,
            matchType
        });
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.classList.add('active');
        this.smartScrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.classList.remove('active');
    }

    // ===== SCROLLING METHODS =====

    smartScrollToBottom() {
        // Only auto-scroll if user hasn't manually scrolled up
        if (!this.isUserScrolled) {
            this.forceScrollToBottom();
        }
    }

    forceScrollToBottom() {
        requestAnimationFrame(() => {
            // Immediate scroll
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;

            // Smooth scroll after a tiny delay (for better UX)
            setTimeout(() => {
                this.chatMessages.scrollTo({
                    top: this.chatMessages.scrollHeight,
                    behavior: 'smooth'
                });
            }, 50);

            // Final check after any images/content load
            setTimeout(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }, 200);
        });
    }

    // ===== STORAGE METHODS =====

    saveMessages() {
        utils.saveChatToStorage(this.messages);
    }

    loadChatHistory() {
        const savedMessages = utils.loadChatFromStorage();

        if (savedMessages && savedMessages.length > 0) {
            if (this.welcomeSection) {
                this.welcomeSection.classList.add('hidden');
            }

            savedMessages.forEach(msg => {
                this.addMessage(msg.text, msg.sender, msg.confidence, msg.matchType);
            });

            this.messages = savedMessages;

            // Scroll to bottom after loading history
            setTimeout(() => this.forceScrollToBottom(), 100);
        }
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.chatMessages.innerHTML = '';
            utils.clearChatStorage();
            this.messages = [];
            if (this.welcomeSection) {
                this.welcomeSection.classList.remove('hidden');
            }
            utils.showToast('Chat history cleared', 'success');
        }
    }

    toggleTheme() {
        document.body.classList.toggle('light-theme');
        const icon = this.themeToggle.querySelector('i');
        icon.classList.toggle('fa-moon');
        icon.classList.toggle('fa-sun');
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new LautechChatbot();
});