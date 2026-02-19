// ===== LAUTECH CHATBOT - ADMIN DASHBOARD =====

class AdminDashboard {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api/admin';
        this.token = localStorage.getItem('admin_token');
        this.currentTab = 'overview';

        // DOM Elements
        this.loginSection = document.getElementById('loginSection');
        this.dashboardSection = document.getElementById('dashboardSection');
        this.loginForm = document.getElementById('loginForm');
        this.logoutBtn = document.getElementById('logoutBtn');
        this.navItems = document.querySelectorAll('.nav-item');
        this.tabContents = document.querySelectorAll('.tab-content');

        // Initialize
        this.init();
    }

    init() {
        this.setupEventListeners();

        // Check if already logged in
        if (this.token) {
            this.verifyToken();
        }
    }

    setupEventListeners() {
        // Login form
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.login();
            });
        }

        // Logout button
        if (this.logoutBtn) {
            this.logoutBtn.addEventListener('click', () => this.logout());
        }

        // Navigation
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = item.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Close modal buttons
        document.querySelectorAll('.close-modal, .cancel-btn').forEach(btn => {
            btn.addEventListener('click', () => this.closeAllModals());
        });
    }

    async login() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            utils.showToast('Please enter username and password', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.token = data.token;
                localStorage.setItem('admin_token', data.token);

                // Show dashboard
                this.loginSection.style.display = 'none';
                this.dashboardSection.style.display = 'flex';

                utils.showToast('Login successful!', 'success');

                // Load dashboard data
                this.loadDashboard();
            } else {
                utils.showToast(data.message || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            utils.showToast('Connection error. Make sure backend is running.', 'error');
        }
    }

    async verifyToken() {
        try {
            const response = await fetch(`${this.apiUrl}/verify`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Token is valid, show dashboard
                this.loginSection.style.display = 'none';
                this.dashboardSection.style.display = 'flex';
                this.loadDashboard();
            } else {
                // Token invalid, clear it
                localStorage.removeItem('admin_token');
                this.token = null;
            }
        } catch (error) {
            console.error('Token verification error:', error);
            localStorage.removeItem('admin_token');
            this.token = null;
        }
    }

    logout() {
        localStorage.removeItem('admin_token');
        this.token = null;
        this.loginSection.style.display = 'flex';
        this.dashboardSection.style.display = 'none';
        utils.showToast('Logged out successfully', 'success');
    }

    switchTab(tabId) {
        this.currentTab = tabId;

        // Update navigation
        this.navItems.forEach(item => {
            if (item.dataset.tab === tabId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Update content
        this.tabContents.forEach(content => {
            if (content.id === `${tabId}Tab`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });

        // Load tab-specific data
        this.loadTabData(tabId);
    }

    loadTabData(tabId) {
        switch(tabId) {
            case 'overview':
                this.loadDashboard();
                break;
            case 'unknown':
                this.loadUnknownQuestions();
                break;
            case 'faqs':
                this.loadFAQs();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    async loadDashboard() {
        try {
            const response = await fetch(`${this.apiUrl}/stats`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.updateStats(data.stats);
                this.updateCharts(data.stats);
                this.loadRecentUnknown();
            } else {
                utils.showToast('Failed to load dashboard data', 'error');
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            utils.showToast('Error loading dashboard data', 'error');
        }
    }

    updateStats(stats) {
        document.getElementById('totalFaqs').textContent = stats.total_faqs || 0;
        document.getElementById('unknownCount').textContent = stats.unknown_unanswered || 0;
        document.getElementById('answeredCount').textContent = (stats.unknown_total - stats.unknown_unanswered) || 0;
        document.getElementById('totalChats').textContent = stats.total_chats || 0;

        // Update badge
        document.getElementById('unknownBadge').textContent = stats.unknown_unanswered || 0;
    }

    updateCharts(stats) {
        // Category chart
        if (stats.categories && stats.categories.length > 0) {
            const ctx = document.getElementById('categoryChart')?.getContext('2d');
            if (ctx) {
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: stats.categories.map(c => c.category),
                        datasets: [{
                            data: stats.categories.map(c => c.count),
                            backgroundColor: [
                                '#00A3FF',
                                '#005F85',
                                '#4CAF50',
                                '#FFC107',
                                '#9C27B0',
                                '#FF5722'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { color: '#EAEAEA' }
                            }
                        }
                    }
                });
            }
        }
    }

    async loadRecentUnknown() {
        try {
            const response = await fetch(`${this.apiUrl}/unknown?filter=unanswered&limit=5`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.renderRecentUnknown(data.questions);
            }
        } catch (error) {
            console.error('Error loading recent unknown:', error);
        }
    }

    renderRecentUnknown(questions) {
        const tbody = document.querySelector('#recentUnknownTable tbody');
        if (!tbody) return;

        if (!questions || questions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="loading-row">No unknown questions</td></tr>';
            return;
        }

        tbody.innerHTML = questions.slice(0, 5).map(q => `
            <tr>
                <td>${utils.truncateText(q.question, 50)}</td>
                <td>${new Date(q.asked_at).toLocaleDateString()}</td>
                <td><span class="status-badge unanswered">Unanswered</span></td>
            </tr>
        `).join('');
    }

    async loadUnknownQuestions(page = 1, filter = 'unanswered') {
        try {
            const response = await fetch(`${this.apiUrl}/unknown?filter=${filter}&page=${page}&limit=20`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.renderUnknownTable(data.questions, data.pagination);
            }
        } catch (error) {
            console.error('Error loading unknown questions:', error);
        }
    }

    renderUnknownTable(questions, pagination) {
        const tbody = document.querySelector('#unknownTable tbody');
        if (!tbody) return;

        if (!questions || questions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading-row">No unknown questions</td></tr>';
            return;
        }

        tbody.innerHTML = questions.map(q => `
            <tr>
                <td>${q.id}</td>
                <td>${utils.truncateText(q.question, 60)}</td>
                <td>${new Date(q.asked_at).toLocaleString()}</td>
                <td>${q.session_id || 'anonymous'}</td>
                <td>
                    <span class="status-badge ${q.answered ? 'answered' : 'unanswered'}">
                        ${q.answered ? 'Answered' : 'Unanswered'}
                    </span>
                </td>
                <td>
                    ${!q.answered ? `
                        <button class="action-btn answer" onclick="admin.answerQuestion(${q.id})" title="Answer">
                            <i class="fas fa-reply"></i>
                        </button>
                    ` : ''}
                    <button class="action-btn delete" onclick="admin.deleteUnknown(${q.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        // Update pagination
        if (pagination) {
            this.updatePagination(pagination);
        }
    }

    answerQuestion(questionId) {
        // Show answer modal
        const modal = document.getElementById('answerModal');
        document.getElementById('unknownQuestionId').value = questionId;

        // Load question details
        this.loadQuestionDetails(questionId);

        modal.style.display = 'flex';
    }

    async loadQuestionDetails(questionId) {
        try {
            const response = await fetch(`${this.apiUrl}/unknown/${questionId}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                document.getElementById('unknownQuestionText').textContent = data.question.question;
            }
        } catch (error) {
            console.error('Error loading question details:', error);
        }
    }

    async submitAnswer() {
        const questionId = document.getElementById('unknownQuestionId').value;
        const answer = document.getElementById('answerText').value;
        const category = document.getElementById('answerCategory').value;

        if (!answer || !category) {
            utils.showToast('Please fill all fields', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/unknown/answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    question_id: parseInt(questionId),
                    answer: answer,
                    category: category
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                utils.showToast('Answer added successfully!', 'success');
                this.closeAllModals();
                this.loadUnknownQuestions(); // Reload list
                this.loadDashboard(); // Update stats
            } else {
                utils.showToast(data.error || 'Failed to add answer', 'error');
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
            utils.showToast('Error submitting answer', 'error');
        }
    }

    async loadFAQs(page = 1, search = '', category = '') {
        try {
            let url = `${this.apiUrl}/faqs?page=${page}&limit=20`;
            if (search) url += `&search=${encodeURIComponent(search)}`;
            if (category) url += `&category=${encodeURIComponent(category)}`;

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.renderFAQsTable(data.faqs, data.pagination);
                this.populateCategoryFilter(data.categories);
            }
        } catch (error) {
            console.error('Error loading FAQs:', error);
        }
    }

    renderFAQsTable(faqs, pagination) {
        const tbody = document.querySelector('#faqsTable tbody');
        if (!tbody) return;

        if (!faqs || faqs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading-row">No FAQs found</td></tr>';
            return;
        }

        tbody.innerHTML = faqs.map(f => `
            <tr>
                <td>${f.id}</td>
                <td>${utils.truncateText(f.question, 50)}</td>
                <td>${utils.truncateText(f.answer, 60)}</td>
                <td>${f.category}</td>
                <td>${new Date(f.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="action-btn" onclick="admin.editFAQ(${f.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="admin.deleteFAQ(${f.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    populateCategoryFilter(categories) {
        const select = document.getElementById('categoryFilter');
        if (!select) return;

        select.innerHTML = '<option value="">All Categories</option>' +
            categories.map(c => `<option value="${c}">${c}</option>`).join('');
    }

    showAddFAQModal() {
        document.getElementById('modalTitle').textContent = 'Add New FAQ';
        document.getElementById('faqId').value = '';
        document.getElementById('faqQuestion').value = '';
        document.getElementById('faqAnswer').value = '';
        document.getElementById('faqCategory').value = '';
        document.getElementById('faqModal').style.display = 'flex';
    }

    editFAQ(faqId) {
        // Load FAQ details and show edit modal
        this.loadFAQDetails(faqId);
    }

    async loadFAQDetails(faqId) {
        try {
            const response = await fetch(`${this.apiUrl}/faqs/${faqId}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                document.getElementById('modalTitle').textContent = 'Edit FAQ';
                document.getElementById('faqId').value = data.faq.id;
                document.getElementById('faqQuestion').value = data.faq.question;
                document.getElementById('faqAnswer').value = data.faq.answer;
                document.getElementById('faqCategory').value = data.faq.category;
                document.getElementById('faqModal').style.display = 'flex';
            }
        } catch (error) {
            console.error('Error loading FAQ details:', error);
        }
    }

    async saveFAQ() {
        const faqId = document.getElementById('faqId').value;
        const question = document.getElementById('faqQuestion').value;
        const answer = document.getElementById('faqAnswer').value;
        const category = document.getElementById('faqCategory').value;

        if (!question || !answer || !category) {
            utils.showToast('Please fill all fields', 'error');
            return;
        }

        const isEdit = !!faqId;
        const url = isEdit ? `${this.apiUrl}/faqs/${faqId}` : `${this.apiUrl}/faqs`;
        const method = isEdit ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ question, answer, category })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                utils.showToast(isEdit ? 'FAQ updated!' : 'FAQ created!', 'success');
                this.closeAllModals();
                this.loadFAQs(); // Reload list
            } else {
                utils.showToast(data.error || 'Operation failed', 'error');
            }
        } catch (error) {
            console.error('Error saving FAQ:', error);
            utils.showToast('Error saving FAQ', 'error');
        }
    }

    async deleteFAQ(faqId) {
        if (!confirm('Are you sure you want to delete this FAQ?')) return;

        try {
            const response = await fetch(`${this.apiUrl}/faqs/${faqId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                utils.showToast('FAQ deleted!', 'success');
                this.loadFAQs(); // Reload list
            } else {
                utils.showToast(data.error || 'Delete failed', 'error');
            }
        } catch (error) {
            console.error('Error deleting FAQ:', error);
            utils.showToast('Error deleting FAQ', 'error');
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    updatePagination(pagination) {
        // Implement pagination controls
        console.log('Pagination:', pagination);
    }

    loadAnalytics() {
        // Implement analytics loading
        console.log('Loading analytics...');
    }

    loadSettings() {
        // Implement settings loading
        console.log('Loading settings...');
    }
}

// Initialize admin dashboard
let admin;
document.addEventListener('DOMContentLoaded', () => {
    admin = new AdminDashboard();
    window.admin = admin; // Make globally available for onclick handlers

    // Setup form submissions
    document.getElementById('answerForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        admin.submitAnswer();
    });

    document.getElementById('faqForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        admin.saveFAQ();
    });

    document.getElementById('addFaqBtn')?.addEventListener('click', () => {
        admin.showAddFAQModal();
    });

    // Search and filter
    document.getElementById('faqSearch')?.addEventListener('input', utils.debounce((e) => {
        admin.loadFAQs(1, e.target.value, document.getElementById('categoryFilter').value);
    }, 500));

    document.getElementById('categoryFilter')?.addEventListener('change', (e) => {
        admin.loadFAQs(1, document.getElementById('faqSearch').value, e.target.value);
    });

    // Unknown questions filter
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            admin.loadUnknownQuestions(1, btn.dataset.filter);
        });
    });
});