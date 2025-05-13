document.addEventListener('DOMContentLoaded', () => {
    const config = {
        apiEndpoints: {
            login: '/login',
            users: '/users',
            journals: '/journals',
            journalScore: (id) => `/journals/${id}/score`
        },
        storage: {
            tokenKey: 'jwt_token',
            userKey: 'user'
        }
    };

    const state = {
        token: null,
        user: {},
        init() {
            this.token = localStorage.getItem(config.storage.tokenKey);
            try {
                this.user = JSON.parse(localStorage.getItem(config.storage.userKey) || '{}');
            } catch (e) {
                console.error('Error parsing stored user:', e);
                this.user = {};
            }
        },
        setAuth(token, user) {
            this.token = token;
            this.user = user;
            localStorage.setItem(config.storage.tokenKey, token);
            localStorage.setItem(config.storage.userKey, JSON.stringify(user));
        },
        clearAuth() {
            this.token = null;
            this.user = {};
            localStorage.removeItem(config.storage.tokenKey);
            localStorage.removeItem(config.storage.userKey);
        },
        isAuthenticated() {
            return !!(this.token && this.user && this.user.username);
        }
    };

    const elements = {
        tabButtons: document.querySelectorAll('.tab-button'),
        tabContents: document.querySelectorAll('.tab-content'),
        registerForm: document.getElementById('register-form'),
        loginForm: document.getElementById('login-form'),
        journalForm: document.getElementById('journal-form'),
        getJournalsButton: document.getElementById('get-journals-btn'),
        logoutButton: document.getElementById('logout-btn'),
        loginInfo: document.getElementById('login-info'),
        journalsList: document.getElementById('journals-list'),
        authTabs: document.querySelectorAll('.auth-tab'),
        loggedInTabs: document.querySelectorAll('.logged-in-tab')
    };

    const api = {
        async request(url, method = 'GET', data = null, requiresAuth = false) {
            try {
                const headers = {
                    'Content-Type': 'application/json'
                };
                
                if (requiresAuth) {
                    if (!state.token) {
                        return { error: 'Authentication required', status: 401 };
                    }
                    headers['Authorization'] = `Bearer ${state.token}`;
                }
                
                const options = {
                    method,
                    headers
                };
                
                if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
                    options.body = JSON.stringify(data);
                }
                
                const response = await fetch(url, options);
                
                let responseData;
                try {
                    responseData = await response.json();
                } catch (e) {
                    responseData = { message: 'Could not parse response as JSON' };
                }
                
                if (response.status === 401 && requiresAuth) {
                    if (responseData.error === 'token_expired' || responseData.error === 'invalid_token') {
                        ui.showNotification('Session expired. Please log in again.', 'error');
                        state.clearAuth();
                        ui.updateLoginStatus();
                    }
                }
                
                return {
                    ok: response.ok,
                    status: response.status,
                    data: responseData
                };
            } catch (error) {
                console.error(`API request error (${url}):`, error);
                return {
                    ok: false,
                    status: 0,
                    error: error.message,
                    data: { message: 'Network or server error occurred' }
                };
            }
        },
        
        async register(userData) {
            return await this.request(config.apiEndpoints.users, 'POST', userData);
        },
        
        async login(credentials) {
            return await this.request(config.apiEndpoints.login, 'POST', credentials);
        },
        
        async createJournal(journalData) {
            return await this.request(config.apiEndpoints.journals, 'POST', journalData, true);
        },
        
        async getJournals() {
            return await this.request(config.apiEndpoints.journals, 'GET', null, true);
        },
        
        async getJournalScore(journalId) {
            return await this.request(config.apiEndpoints.journalScore(journalId), 'GET', null, true);
        }
    };

    const ui = {
        initializeTabs() {
            elements.tabContents.forEach(content => {
                content.classList.remove('active');
                content.style.display = 'none';
            });
            
            const activeTab = document.querySelector('.tab-content.active') || elements.tabContents[0];
            if (activeTab) {
                activeTab.style.display = 'block';
            }
        },
        
        switchTab(targetTab) {
            elements.tabButtons.forEach(btn => btn.classList.remove('active'));
            const button = document.querySelector(`[data-tab="${targetTab}"]`);
            if (button) {
                button.classList.add('active');
            }
            
            elements.tabContents.forEach(content => {
                content.classList.remove('active');
                content.style.display = 'none';
            });
            
            const selectedTab = document.getElementById(targetTab);
            if (selectedTab) {
                selectedTab.classList.add('active');
                selectedTab.style.display = 'block';
            }
            
            if (targetTab === 'journals-list-tab' && state.isAuthenticated()) {
                this.loadJournals();
            }
        },
        
        updateLoginStatus() {
            if (state.token) {
                this.validateToken();
            }
            
            if (state.isAuthenticated()) {
                if (elements.loginInfo) {
                    elements.loginInfo.textContent = `Logged in as: ${state.user.username}`;
                    elements.loginInfo.className = 'login-info logged-in';
                }
                
                elements.authTabs.forEach(tab => {
                    tab.style.display = 'none';
                    if (!tab.classList.contains('tab-button')) {
                        tab.classList.remove('active');
                    }
                });
                
                elements.loggedInTabs.forEach(tab => {
                    tab.style.display = 'block';
                });
                
                const activeLoggedInTab = document.querySelector('.logged-in-tab.tab-button.active');
                if (!activeLoggedInTab) {
                    const firstLoggedInTabButton = document.querySelector('.logged-in-tab.tab-button');
                    if (firstLoggedInTabButton) {
                        firstLoggedInTabButton.click();
                    }
                }
            } else {
                if (elements.loginInfo) {
                    elements.loginInfo.textContent = 'Not logged in';
                    elements.loginInfo.className = 'login-info';
                }
                
                elements.authTabs.forEach(tab => {
                    tab.style.display = 'block';
                });
                
                elements.loggedInTabs.forEach(tab => {
                    tab.style.display = 'none';
                    if (tab.classList.contains('tab-content')) {
                        tab.classList.remove('active');
                    }
                });
                
                const activeAuthTab = document.querySelector('.auth-tab.tab-button.active');
                if (!activeAuthTab) {
                    const firstAuthTabButton = document.querySelector('.auth-tab.tab-button');
                    if (firstAuthTabButton) {
                        firstAuthTabButton.click();
                    }
                }
            }
            
            this.initializeTabs();
        },
        
        validateToken() {
            if (typeof state.token !== 'string' || state.token.trim() === '') {
                console.error('Invalid token format in storage');
                state.clearAuth();
                return false;
            }
            
            try {
                const parts = state.token.split('.');
                if (parts.length !== 3) {
                    console.error('Invalid JWT format (should have 3 parts)');
                    state.clearAuth();
                    return false;
                }
                
                try {
                    const payload = JSON.parse(atob(parts[1]));
                    
                    if (payload.exp && Date.now() >= payload.exp * 1000) {
                        console.warn('Token has expired');
                        this.showNotification('Your session has expired. Please log in again.', 'error');
                        state.clearAuth();
                        return false;
                    }
                    
                    return true;
                } catch (e) {
                    console.error('Error decoding token payload:', e);
                    state.clearAuth();
                    return false;
                }
            } catch (e) {
                console.error('Error checking token format:', e);
                state.clearAuth();
                return false;
            }
        },
        
        showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    notification.remove();
                }, 500);
            }, 3000);
        },
        
        async loadJournals() {
            if (!state.isAuthenticated()) {
                this.showNotification('Please log in to view journals', 'error');
                return;
            }
            
            if (elements.journalsList) {
                elements.journalsList.innerHTML = '<p class="loading">Loading journals...</p>';
            }
            
            const result = await api.getJournals();
            
            if (!result.ok) {
                if (elements.journalsList) {
                    elements.journalsList.innerHTML = '<p class="error">Failed to load journals. Please try again later.</p>';
                }
                this.showNotification(result.data.message || 'Error loading journals', 'error');
                return;
            }
            
            const journals = result.data;
            
            if (elements.journalsList) {
                if (journals.length > 0) {
                    let journalsHTML = '<div class="journals-container">';
                    
                    journals.forEach(journal => {
                        journalsHTML += `
                            <div class="journal-card">
                                <h4>Journal #${journal.id}</h4>
                                <p><strong>Created:</strong> ${new Date(journal.created_at).toLocaleString()}</p>
                                <p><strong>Content:</strong> ${this.sanitizeHTML(journal.text)}</p>
                        `;
                        
                        if (journal.score) {
                            journalsHTML += this.renderScoreDetails(journal.score);
                        } else {
                            journalsHTML += `
                                <button class="view-score-btn" data-journal-id="${journal.id}">View Score Details</button>
                            `;
                        }
                        
                        journalsHTML += `</div>`;
                    });
                    
                    journalsHTML += '</div>';
                    elements.journalsList.innerHTML = journalsHTML;
                    
                    setTimeout(() => {
                        const scoreButtons = document.querySelectorAll('.view-score-btn');
                        if (scoreButtons.length > 0) {
                            scoreButtons.forEach(button => {
                                button.addEventListener('click', (e) => {
                                    const journalId = e.target.getAttribute('data-journal-id');
                                    this.loadJournalScore(journalId);
                                });
                            });
                        }
                    }, 0);
                } else {
                    elements.journalsList.innerHTML = '<p>You have not created any journal entries yet.</p>';
                }
            }
        },
        
        async loadJournalScore(journalId) {
            if (!state.isAuthenticated()) {
                this.showNotification('Please log in to view journal scores', 'error');
                return;
            }
            
            const scoreButton = document.querySelector(`.view-score-btn[data-journal-id="${journalId}"]`);
            if (scoreButton) {
                scoreButton.disabled = true;
                scoreButton.textContent = 'Loading...';
            }
            
            const result = await api.getJournalScore(journalId);
            
            if (!result.ok) {
                if (scoreButton) {
                    scoreButton.disabled = false;
                    scoreButton.textContent = 'View Score Details';
                    
                    const errorMsg = document.createElement('p');
                    errorMsg.className = 'error';
                    errorMsg.textContent = result.data.message || 'Error fetching score';
                    scoreButton.insertAdjacentElement('afterend', errorMsg);
                }
                
                this.showNotification('Failed to load journal score', 'error');
                return;
            }
            
            const data = result.data;
            
            if (scoreButton && data.score) {
                const scoreDetails = document.createElement('div');
                scoreDetails.className = 'score-details';
                scoreDetails.innerHTML = this.renderScoreDetails(data.score);
                
                scoreButton.parentNode.replaceChild(scoreDetails, scoreButton);
            }
        },
        
        renderScoreDetails(score) {
            return `
                <div class="score-details">
                    <h5>Journal Score</h5>
                    <ul>
                        <li>Positive Emotion: ${score.positive_emotion}</li>
                        <li>Negative Emotion: ${score.negative_emotion}</li>
                        <li>Social: ${score.social}</li>
                        <li>Cognitive: ${score.cognitive}</li>
                        <li>Total Score: ${score.total}</li>
                    </ul>
                </div>
            `;
        },
        
        sanitizeHTML(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    const handlers = {
        initializeTabButtons() {
            elements.tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const targetTab = button.getAttribute('data-tab');
                    ui.switchTab(targetTab);
                });
            });
        },
        
        async handleRegister(e) {
            e.preventDefault();
            const username = document.getElementById('register-username').value;
            const password = document.getElementById('register-password').value;
            const email = document.getElementById('register-email').value;
            
            if (!username || !password || !email) {
                ui.showNotification('All fields are required', 'error');
                return;
            }
            
            const result = await api.register({ username, password, email });
            
            if (result.ok) {
                ui.showNotification('Registration successful! You can now log in.', 'success');
                elements.registerForm.reset();
                
                const loginTabButton = document.querySelector('[data-tab="login-tab"]');
                if (loginTabButton) {
                    loginTabButton.click();
                }
            } else {
                ui.showNotification(result.data.message || 'Registration failed', 'error');
            }
        },
        
        async handleLogin(e) {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            
            if (!username || !password) {
                ui.showNotification('Username and password are required', 'error');
                return;
            }
            
            const result = await api.login({ username, password });
            
            if (result.ok && result.data.access_token) {
                state.setAuth(
                    result.data.access_token, 
                    { 
                        username: result.data.username || username,
                        id: result.data.user_id ? String(result.data.user_id) : null
                    }
                );
                
                elements.loginForm.reset();
                ui.updateLoginStatus();
                ui.showNotification('Login successful', 'success');
                
                const journalsTabButton = document.querySelector('[data-tab="journals-list-tab"]');
                if (journalsTabButton) {
                    journalsTabButton.click();
                }
            } else {
                ui.showNotification(result.data.message || 'Login failed', 'error');
            }
        },
        
        async handleJournalSubmit(e) {
            e.preventDefault();
            const content = document.getElementById('journal-content').value;
            
            if (!content.trim()) {
                ui.showNotification('Journal content cannot be empty', 'error');
                return;
            }
            
            if (!state.isAuthenticated()) {
                ui.showNotification('Please log in to submit a journal entry', 'error');
                return;
            }
            
            const result = await api.createJournal({ text: content });
            
            if (result.ok) {
                ui.showNotification('Journal entry created successfully', 'success');
                elements.journalForm.reset();
                
                const journalsTabButton = document.querySelector('[data-tab="journals-list-tab"]');
                if (journalsTabButton) {
                    journalsTabButton.click();
                }
            } else {
                ui.showNotification(result.data.message || 'Failed to create journal entry', 'error');
            }
        },
        
        handleLogout() {
            state.clearAuth();
            ui.updateLoginStatus();
            ui.showNotification('Logged out successfully', 'info');
        },
        
        async verifyToken() {
            if (!state.token) return;
            
            const result = await api.getJournals();
            
            if (!result.ok && (result.status === 401 || result.status === 403)) {
                ui.showNotification('Your session has expired. Please log in again.', 'error');
                state.clearAuth();
                ui.updateLoginStatus();
            }
        }
    };

    const addStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                border-radius: 4px;
                color: white;
                z-index: 1000;
                animation: slide-in 0.3s ease-out;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            }
            .notification.success { background-color: #4CAF50; }
            .notification.error { background-color: #F44336; }
            .notification.info { background-color: #2196F3; }
            .notification.fade-out {
                opacity: 0;
                transition: opacity 0.5s;
            }
            @keyframes slide-in {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            .error {
                color: #F44336;
                font-weight: bold;
            }
        `;
        document.head.appendChild(style);
    };

    const init = () => {
        addStyles();
        state.init();
        ui.initializeTabs();
        handlers.initializeTabButtons();
        
        if (state.token) {
            handlers.verifyToken();
        }
        
        ui.updateLoginStatus();
        
        if (elements.registerForm) {
            elements.registerForm.addEventListener('submit', handlers.handleRegister);
        }
        
        if (elements.loginForm) {
            elements.loginForm.addEventListener('submit', handlers.handleLogin);
        }
        
        if (elements.journalForm) {
            elements.journalForm.addEventListener('submit', handlers.handleJournalSubmit);
        }
        
        if (elements.getJournalsButton) {
            elements.getJournalsButton.addEventListener('click', () => ui.loadJournals());
        }
        
        if (elements.logoutButton) {
            elements.logoutButton.addEventListener('click', handlers.handleLogout);
        }
    };
    
    init();
});