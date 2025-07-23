/**
 * VoiceBot Enterprise - Frontend JavaScript Application
 * ====================================================
 * 
 * Advanced AI-powered frontend for two-wheeler sales management system.
 * Provides real-time analytics, voice commands, multilingual support,
 * and comprehensive business intelligence features.
 * 
 * Key Features:
 * - Voice recognition and speech synthesis
 * - Real-time data visualization with Chart.js
 * - Multilingual chat interface
 * - Business analytics dashboard
 * - Customer management system
 * - Inventory tracking
 * - PDF report generation
 * 
 * Author: Mohamed Ibrahim
 * Repository: https://github.com/rMohamedIbrahim/AI-Sales-Assistant-Chatbot
 * License: MIT
 * Version: 1.0.0
 */

/**
 * Main VoiceBot Application Class
 * 
 * This class manages the entire frontend application including:
 * - Voice recognition and synthesis
 * - Chat functionality with AI backend
 * - Real-time data updates and visualization
 * - Multi-section navigation and state management
 * - Integration with external APIs for enhanced features
 */
class VoiceBotApp {
    /**
     * Initialize the VoiceBot application
     * Sets up all required properties, API endpoints, and configurations
     */
    constructor() {
        // Voice and audio management
        this.isListening = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        
        // Application configuration
        this.apiBase = 'http://localhost:8000';
        this.currentSection = 'dashboard';
        this.charts = {}; // Store Chart.js instances
        
        // Real-time business metrics (simulated for demo)
        this.realTimeData = {
            conversations: 1247,  // Total chat conversations
            leads: 89,           // Generated leads
            revenue: 52400,      // Revenue in currency
            satisfaction: 96     // Customer satisfaction percentage
        };
        
        // External API endpoints for enhanced functionality
        // Note: Replace 'demo' API keys with actual keys in production
        this.apis = {
            crypto: 'https://api.coindesk.com/v1/bpi/currentprice.json',
            weather: 'https://api.openweathermap.org/data/2.5/weather?q=Mumbai&units=metric&appid=demo',
            jsonPlaceholder: 'https://jsonplaceholder.typicode.com',
            randomUser: 'https://randomuser.me/api',
            quotes: 'https://api.quotable.io/random',
            news: 'https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=demo',
            translate: 'https://api.mymemory.translated.net/get'
        };
        
        // Voice command mapping for hands-free navigation
        this.voiceCommands = {
            'show dashboard': () => this.switchSection('dashboard'),
            'open analytics': () => this.switchSection('analytics'),
            'show customers': () => this.switchSection('customers'),
            'check inventory': () => this.switchSection('inventory'),
            'generate report': () => this.generateBusinessReport(),
            'refresh data': () => this.refreshAllData(),
            'dark mode': () => this.toggleTheme(),
            'light mode': () => this.toggleTheme(),
            'export data': () => this.exportData(),
            'help me': () => this.showVoiceHelp()
        };
        
        // Multi-language support for international users
        this.languages = {
            'en': 'English',
            'hi': 'हिंदी',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'bn': 'বাংলা',
            'mr': 'मराठी'
        };
        
        this.currentLanguage = 'en';
        this.notifications = [];
        this.isDarkMode = false;
        
        this.init();
    }

    async init() {
        // Show loading screen
        await this.showLoadingScreen();
        
        // Initialize speech recognition
        this.initSpeechRecognition();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize dashboard
        this.initDashboard();
        
        // Start real-time updates
        this.startRealTimeUpdates();
        
        // Setup advanced features
        this.setupAdvancedFeatures();
        
        // Hide loading screen
        this.hideLoadingScreen();
        
        // Check system status
        this.checkSystemStatus();
    }

    showLoadingScreen() {
        return new Promise(resolve => {
            const loadingScreen = document.querySelector('.loading-screen');
            setTimeout(() => {
                resolve();
            }, 2000); // Simulate loading time
        });
    }

    hideLoadingScreen() {
        const loadingScreen = document.querySelector('.loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
            
            // Remove from DOM after animation
            setTimeout(() => {
                loadingScreen.remove();
            }, 500);
        }
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateVoiceButton();
                this.addSystemMessage('🎤 Listening...', 'info');
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleVoiceInput(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.addSystemMessage('❌ Voice recognition error. Please try again.', 'error');
                this.isListening = false;
                this.updateVoiceButton();
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                this.updateVoiceButton();
            };
        } else {
            console.warn('Speech recognition not supported');
            this.addSystemMessage('⚠️ Speech recognition not supported in this browser.', 'warning');
        }
    }

    async checkSystemStatus() {
        try {
            console.log('🔍 Checking system status...');
            const response = await fetch('/api/health');
            const status = await response.json();
            console.log('✅ System Status:', status);
            this.addSystemMessage('✅ System online and ready!', 'success');
            return status;
        } catch (error) {
            console.warn('⚠️ System status check failed:', error);
            this.addSystemMessage('⚠️ System running in offline mode', 'warning');
            return { status: 'offline' };
        }
    }

    setupEventListeners() {
        // Navigation items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('data-section') || item.getAttribute('href').substring(1);
                if (section) {
                    this.switchSection(section);
                }
            });
        });

        // Quick action cards
        document.querySelectorAll('.action-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                const action = card.getAttribute('data-action');
                if (action) {
                    this.handleQuickAction(action);
                }
            });
        });

        // Voice button
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoiceRecognition());
        }

        // Send button and text input
        const sendBtn = document.getElementById('sendBtn');
        const textInput = document.getElementById('textInput');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendTextMessage());
        }
        
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendTextMessage();
                }
            });
        }

        // Quick suggestions
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const suggestion = chip.textContent;
                this.handleSuggestion(suggestion);
            });
        });

        // Chart time filters
        document.querySelectorAll('.time-filter').forEach(filter => {
            filter.addEventListener('click', () => {
                document.querySelectorAll('.time-filter').forEach(f => f.classList.remove('active'));
                filter.classList.add('active');
                this.updateCharts(filter.getAttribute('data-period'));
            });
        });

        // Settings controls
        this.setupSettingsControls();
    }

    switchSection(sectionName) {
        console.log('🔄 Switching to section:', sectionName);
        
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const navItem = document.querySelector(`[data-section="${sectionName}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }

        // Update content - first hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Try to find the exact section ID first
        let targetSection = document.getElementById(sectionName);
        
        // If not found, try with 'Section' suffix
        if (!targetSection) {
            targetSection = document.getElementById(`${sectionName}Section`);
        }
        
        // If still not found, show a default section or create a placeholder
        if (targetSection) {
            targetSection.classList.add('active');
        } else {
            console.warn(`Section element not found: ${sectionName}`);
            // Show assistant section as default if target not found
            const defaultSection = document.getElementById('assistant');
            if (defaultSection) {
                defaultSection.classList.add('active');
                this.addSystemMessage(`📋 ${sectionName} section is under development. Showing AI Assistant instead.`, 'info');
            }
        }

        this.currentSection = sectionName;

        // Section-specific initialization with real-time data
        if (sectionName === 'analytics') {
            this.loadAnalyticsSection();
        } else if (sectionName === 'customers') {
            this.loadCustomersSection();
        } else if (sectionName === 'inventory') {
            this.loadInventorySection();
        }
        
        // Show system message
        this.addSystemMessage(`📄 Switched to ${sectionName} section`, 'info');
    }

    handleQuickAction(action) {
        console.log('Handling quick action:', action);
        
        switch (action) {
            case 'start-conversation':
                this.switchSection('assistant');
                this.addSystemMessage('🎤 Ready to start a new conversation! Click the microphone or type your message.', 'success');
                break;
            case 'view-analytics':
                this.switchSection('analytics');
                this.addSystemMessage('📊 Loading analytics dashboard...', 'info');
                break;
            case 'manage-customers':
                this.switchSection('customers');
                this.addSystemMessage('👥 Customer management loaded successfully.', 'info');
                break;
            case 'inventory-check':
                this.switchSection('inventory');
                this.addSystemMessage('🏍️ Inventory dashboard loaded.', 'info');
                break;
            case 'generate-report':
                this.switchSection('reports');
                this.addSystemMessage('📋 Reports section opened.', 'info');
                break;
            case 'system-settings':
                this.switchSection('settings');
                this.addSystemMessage('⚙️ System settings loaded.', 'info');
                break;
            case 'export-data':
                this.exportData();
                break;
            default:
                console.log('Unknown action:', action);
                this.addSystemMessage(`Action "${action}" is not yet implemented.`, 'warning');
        }
    }

    initDashboard() {
        this.updateStatsCards();
        this.updateSystemMetrics();
    }

    updateStatsCards() {
        const stats = [
            { id: 'conversations', value: this.realTimeData.conversations, trend: '+12.5%' },
            { id: 'leads', value: this.realTimeData.leads, trend: '+8.2%' },
            { id: 'revenue', value: `$${this.realTimeData.revenue.toLocaleString()}`, trend: '+15.3%' },
            { id: 'satisfaction', value: `${this.realTimeData.satisfaction}%`, trend: '+2.1%' }
        ];

        stats.forEach(stat => {
            const card = document.querySelector(`[data-stat="${stat.id}"]`);
            if (card) {
                const h3 = card.querySelector('h3');
                const trend = card.querySelector('.stat-trend');
                if (h3) h3.textContent = stat.value;
                if (trend) trend.textContent = stat.trend;
            }
        });
    }

    updateSystemMetrics() {
        const metrics = {
            'cpu-usage': Math.floor(Math.random() * 30 + 10) + '%',
            'memory': Math.floor(Math.random() * 40 + 30) + '%',
            'response-time': Math.floor(Math.random() * 100 + 50) + 'ms',
            'uptime': '99.9%'
        };

        Object.entries(metrics).forEach(([key, value]) => {
            const metricElement = document.querySelector(`[data-metric="${key}"]`);
            if (metricElement) {
                metricElement.textContent = value;
            }
        });
    }

    toggleVoiceRecognition() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (this.recognition) {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Error starting recognition:', error);
                this.addSystemMessage('Could not start voice recognition.', 'error');
            }
        }
    }

    stopListening() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    updateVoiceButton() {
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            if (this.isListening) {
                voiceBtn.classList.add('recording');
                voiceBtn.innerHTML = `
                    <div class="voice-waves">
                        <span class="wave"></span>
                        <span class="wave"></span>
                        <span class="wave"></span>
                    </div>
                `;
            } else {
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="fas fa-microphone voice-icon"></i>';
            }
        }
    }

    async handleVoiceInput(transcript) {
        this.addUserMessage(transcript, 'voice');
        await this.processMessage(transcript);
    }

    async sendTextMessage() {
        const textInput = document.getElementById('textInput');
        const message = textInput.value.trim();
        
        if (message) {
            textInput.value = '';
            this.addUserMessage(message, 'text');
            await this.processMessage(message);
        }
    }

    async processMessage(message) {
        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Generate a user ID for session tracking
            if (!this.userId) {
                this.userId = 'user_' + Math.random().toString(36).substr(2, 9);
            }

            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    language: 'en-IN',
                    user_id: this.userId,
                    context: {
                        timestamp: new Date().toISOString(),
                        page: window.location.pathname
                    }
                })
            });

            const data = await response.json();
            this.hideTypingIndicator();
            
            if (data.response) {
                // Add AI message with enhanced information
                this.addAIMessage(data.response, {
                    intent: data.intent,
                    confidence: data.confidence,
                    suggestions: data.suggestions
                });
                
                // Add suggested quick replies if available
                if (data.suggestions && data.suggestions.length > 0) {
                    this.addQuickReplies(data.suggestions);
                }
                
                this.speakResponse(data.response);
                
                // Show intent and confidence for debugging (optional)
                if (data.intent && data.confidence) {
                    console.log(`Intent: ${data.intent} (Confidence: ${(data.confidence * 100).toFixed(1)}%)`);
                }
            }
        } catch (error) {
            console.error('Error processing message:', error);
            this.hideTypingIndicator();
            
            // Provide demo response
            const demoResponse = this.getDemoResponse(message);
            this.addAIMessage(demoResponse);
            this.speakResponse(demoResponse);
        }
    }

    getDemoResponse(message) {
        const msg = message.toLowerCase();
        
        if (msg.includes('bike') || msg.includes('under') || msg.includes('lakh')) {
            return "We have several excellent bikes under 1 lakh! Our popular models include: Honda CB Shine (₹72,000), Bajaj Pulsar 125 (₹94,000), and TVS Raider 125 (₹85,000). All come with great mileage and warranty. Would you like to know more about any specific model?";
        } else if (msg.includes('test ride') || msg.includes('book')) {
            return "I'd be happy to help you book a test ride! Please provide your name, contact number, and preferred date. We have slots available from Monday to Saturday, 10 AM to 6 PM. Which bike would you like to test ride?";
        } else if (msg.includes('emi') || msg.includes('finance')) {
            return "We offer flexible EMI options starting from ₹2,500 per month! We work with all major banks and NBFCs. For a ₹1 lakh bike, you can get EMIs starting from ₹3,000 for 36 months. Lower interest rates available for salaried professionals. Shall I calculate EMI for a specific model?";
        } else if (msg.includes('service') || msg.includes('maintenance')) {
            return "We offer comprehensive service packages: Basic Service (₹800), Complete Service (₹1,500), and Premium Care (₹2,500). Includes engine oil change, brake check, tire inspection, and 20-point check. First service is free! Which package interests you?";
        } else {
            return "Thank you for your interest! I can help you with bike information, pricing, test rides, EMI options, and service bookings. What would you like to know more about?";
        }
    }

    addUserMessage(message, type = 'text') {
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            const messageElement = this.createMessageElement('user', message, type);
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    addAIMessage(message, metadata = {}) {
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            const messageElement = this.createMessageElement('ai', message, 'text', metadata);
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    addQuickReplies(suggestions) {
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages && suggestions && suggestions.length > 0) {
            const quickRepliesElement = document.createElement('div');
            quickRepliesElement.className = 'quick-replies';
            quickRepliesElement.innerHTML = `
                <div class="quick-replies-label">💡 Quick suggestions:</div>
                <div class="quick-replies-buttons">
                    ${suggestions.map(suggestion => 
                        `<button class="quick-reply-btn" onclick="voiceBotApp.sendQuickReply('${suggestion}')">${suggestion}</button>`
                    ).join('')}
                </div>
            `;
            chatMessages.appendChild(quickRepliesElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    sendQuickReply(suggestion) {
        // Remove existing quick replies
        const existingQuickReplies = document.querySelectorAll('.quick-replies');
        existingQuickReplies.forEach(element => element.remove());
        
        // Send the suggestion as user message
        this.addUserMessage(suggestion);
        this.processMessage(suggestion);
    }

    addSystemMessage(message, type = 'info') {
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            const messageElement = this.createSystemMessageElement(message, type);
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    createMessageElement(sender, message, inputType = 'text', metadata = {}) {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group';
        
        const isAI = sender === 'ai';
        const displayName = isAI ? 'VoiceBot AI' : 'You';
        const icon = isAI ? 'fas fa-robot' : (inputType === 'voice' ? 'fas fa-microphone' : 'fas fa-user');
        
        // Create metadata display for AI messages
        let metadataDisplay = '';
        if (isAI && metadata.intent && metadata.confidence) {
            const confidencePercent = (metadata.confidence * 100).toFixed(1);
            const confidenceColor = metadata.confidence > 0.7 ? '#10b981' : metadata.confidence > 0.4 ? '#f59e0b' : '#ef4444';
            metadataDisplay = `
                <div class="message-metadata">
                    <span class="intent-badge" style="background: ${confidenceColor}20; color: ${confidenceColor};">
                        🎯 ${metadata.intent.replace('_', ' ')} (${confidencePercent}%)
                    </span>
                </div>
            `;
        }
        
        messageGroup.innerHTML = `
            <div class="message-header">
                <div class="message-avatar ${isAI ? 'ai-avatar' : 'user-avatar'}">
                    <i class="${icon}"></i>
                </div>
                <span class="message-sender">${displayName}</span>
                <span class="message-time">${timeString}</span>
            </div>
            ${metadataDisplay}
            <div class="message-bubble ${isAI ? 'ai-bubble' : 'user-bubble'}">
                <p>${message}</p>
            </div>
        `;
        
        return messageGroup;
    }

    createSystemMessageElement(message, type) {
        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group system-message';
        
        const icons = {
            info: 'fas fa-info-circle',
            success: 'fas fa-check-circle',
            warning: 'fas fa-exclamation-triangle',
            error: 'fas fa-times-circle'
        };
        
        messageGroup.innerHTML = `
            <div class="message-header">
                <div class="message-avatar system-avatar">
                    <i class="${icons[type] || icons.info}"></i>
                </div>
                <span class="message-sender">System</span>
                <span class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            <div class="message-bubble system-bubble ${type}">
                <p>${message}</p>
            </div>
        `;
        
        return messageGroup;
    }

    showTypingIndicator() {
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            const typingElement = document.createElement('div');
            typingElement.className = 'typing-indicator';
            typingElement.id = 'typingIndicator';
            typingElement.innerHTML = `
                <div class="message-group">
                    <div class="message-header">
                        <div class="message-avatar ai-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <span class="message-sender">VoiceBot AI</span>
                    </div>
                    <div class="message-bubble ai-bubble">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            `;
            chatMessages.appendChild(typingElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    speakResponse(text) {
        if (this.synthesis) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 0.8;
            this.synthesis.speak(utterance);
        }
    }

    handleSuggestion(suggestion) {
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.value = suggestion;
            this.sendTextMessage();
        }
    }

    initAnalytics() {
        this.updateLanguageStats();
        this.simulateChartData();
    }

    updateLanguageStats() {
        const languages = [
            { name: 'English', percent: 78 },
            { name: 'Spanish', percent: 45 },
            { name: 'French', percent: 32 },
            { name: 'German', percent: 28 },
            { name: 'Italian', percent: 15 }
        ];

        const container = document.querySelector('.language-stats');
        if (container) {
            container.innerHTML = languages.map(lang => `
                <div class="lang-stat">
                    <span class="lang-name">${lang.name}</span>
                    <div class="lang-bar">
                        <div class="lang-fill" style="width: ${lang.percent}%"></div>
                    </div>
                    <span class="lang-percent">${lang.percent}%</span>
                </div>
            `).join('');
        }
    }

    simulateChartData() {
        // Simulate chart data for demo purposes
        const chartPlaceholders = document.querySelectorAll('.chart-placeholder');
        chartPlaceholders.forEach(placeholder => {
            placeholder.innerHTML = `
                <i class="fas fa-chart-line"></i>
                <h4>Analytics Chart</h4>
                <p>Real-time data visualization would appear here in a production environment.</p>
            `;
        });
    }

    updateCharts(period) {
        console.log('Updating charts for period:', period);
        // In a real app, this would fetch new data and update the charts
        this.simulateChartData();
    }

    setupSettingsControls() {
        // API Settings
        const apiEndpointInput = document.querySelector('input[name="apiEndpoint"]');
        if (apiEndpointInput) {
            apiEndpointInput.value = this.apiBase;
            apiEndpointInput.addEventListener('change', (e) => {
                this.apiBase = e.target.value;
                this.addSystemMessage(`API endpoint updated to: ${this.apiBase}`, 'success');
            });
        }

        // Voice Settings
        const voiceSelect = document.getElementById('voiceSelect');
        if (voiceSelect && this.synthesis) {
            const voices = this.synthesis.getVoices();
            voiceSelect.innerHTML = voices.map(voice => 
                `<option value="${voice.name}">${voice.name} (${voice.lang})</option>`
            ).join('');
        }

        // Language Settings
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect && this.recognition) {
            languageSelect.addEventListener('change', (e) => {
                this.recognition.lang = e.target.value;
                this.addSystemMessage(`Language changed to: ${e.target.value}`, 'success');
            });
        }
    }

    startRealTimeUpdates() {
        // Simulate real-time data updates
        setInterval(() => {
            this.realTimeData.conversations += Math.floor(Math.random() * 3);
            this.realTimeData.leads += Math.floor(Math.random() * 2);
            this.realTimeData.revenue += Math.floor(Math.random() * 1000);
            
            if (this.currentSection === 'dashboard') {
                this.updateStatsCards();
                this.updateSystemMetrics();
            }
        }, 30000); // Update every 30 seconds
    }

    exportData() {
        const data = {
            timestamp: new Date().toISOString(),
            stats: this.realTimeData,
            conversations: 'Export data would be generated here'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voicebot-data-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addSystemMessage('Data exported successfully!', 'success');
    }

    // Additional methods for HTML compatibility
    toggleProfileMenu() {
        console.log('🔄 Toggling profile menu');
        const menu = document.querySelector('.profile-dropdown');
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
    }

    // Advanced features implementation
    async setupAdvancedFeatures() {
        this.setupNotificationSystem();
        this.setupVoiceCommands();
        this.setupThemeToggle();
        this.setupLanguageSupport();
        this.setupBusinessIntelligence();
        this.startRealTimeMonitoring();
    }

    setupNotificationSystem() {
        this.addNotification('🎉 Advanced AI features activated!', 'success');
        this.addNotification('📊 Real-time monitoring started', 'info');
    }

    addNotification(message, type = 'info') {
        if (!this.notifications) this.notifications = [];
        
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date().toLocaleString(),
            read: false
        };
        
        this.notifications.unshift(notification);
        console.log(`🔔 ${type.toUpperCase()}: ${message}`);
        
        // Show system message
        this.addSystemMessage(message, type);
    }

    setupVoiceCommands() {
        if (this.recognition) {
            const originalOnResult = this.recognition.onresult;
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                console.log('🎤 Voice command:', transcript);
                
                // Check for voice commands
                const command = Object.keys(this.voiceCommands).find(cmd => 
                    transcript.includes(cmd)
                );
                
                if (command) {
                    this.voiceCommands[command]();
                    this.addNotification(`✅ Executed: "${command}"`, 'success');
                } else {
                    this.handleVoiceInput(transcript);
                }
            };
        }
    }

    setupThemeToggle() {
        const themeToggle = document.createElement('button');
        themeToggle.innerHTML = '🌙';
        themeToggle.className = 'theme-toggle';
        themeToggle.style.cssText = `
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: all 0.3s ease;
        `;
        themeToggle.onclick = () => this.toggleTheme();
        themeToggle.title = 'Toggle Dark Mode';
        
        const header = document.querySelector('.header-actions') || document.querySelector('.header');
        if (header) {
            header.appendChild(themeToggle);
        }
    }

    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        document.body.classList.toggle('dark-mode', this.isDarkMode);
        
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = this.isDarkMode ? '☀️' : '🌙';
        }
        
        this.addNotification(
            `🎨 Switched to ${this.isDarkMode ? 'dark' : 'light'} mode`, 
            'info'
        );
    }

    setupLanguageSupport() {
        const languageSelector = document.createElement('select');
        languageSelector.className = 'language-selector';
        languageSelector.style.cssText = `
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 0.5rem;
            margin-left: 1rem;
        `;
        languageSelector.innerHTML = Object.entries(this.languages).map(([code, name]) => 
            `<option value="${code}" ${code === this.currentLanguage ? 'selected' : ''}>${name}</option>`
        ).join('');
        
        languageSelector.onchange = (e) => this.changeLanguage(e.target.value);
        
        const header = document.querySelector('.header-actions') || document.querySelector('.header');
        if (header) {
            header.appendChild(languageSelector);
        }
    }

    async changeLanguage(langCode) {
        this.currentLanguage = langCode;
        this.addNotification(`🌍 Language changed to ${this.languages[langCode]}`, 'success');
        
        // Update speech recognition language
        if (this.recognition) {
            this.recognition.lang = langCode === 'en' ? 'en-US' : 
                                  langCode === 'hi' ? 'hi-IN' : 
                                  `${langCode}-IN`;
        }
    }

    setupBusinessIntelligence() {
        this.businessInsights = {
            recommendations: [
                '📈 Sales are projected to increase by 15% next quarter',
                '🎯 Customer satisfaction is at an all-time high of 96%',
                '💡 Recommend focusing on premium models for higher margins',
                '🚀 Voice assistant adoption increased customer engagement by 40%',
                '📊 Peak sales hours: 10 AM - 2 PM and 5 PM - 8 PM',
                '🏆 Top performing region: Maharashtra with 35% market share'
            ]
        };
        
        this.addNotification('🧠 Business insights generated', 'info');
    }

    startRealTimeMonitoring() {
        // Monitor system performance
        setInterval(() => {
            this.updateRealTimeMetrics();
        }, 30000); // Every 30 seconds
        
        // Monitor low stock alerts
        setInterval(() => {
            this.checkInventoryAlerts();
        }, 60000); // Every minute
    }

    async checkInventoryAlerts() {
        try {
            const inventory = await this.fetchInventoryData();
            const lowStockItems = inventory.filter(item => item.stock < 15);
            
            if (lowStockItems.length > 0) {
                this.addNotification(
                    `🚨 ${lowStockItems.length} items are running low on stock!`, 
                    'warning'
                );
            }
        } catch (error) {
            console.warn('Inventory check failed:', error);
        }
    }

    generateBusinessReport() {
        this.addNotification('📋 Generating comprehensive business report...', 'info');
        
        setTimeout(() => {
            const report = {
                timestamp: new Date().toISOString(),
                sections: ['Sales', 'Customer Analytics', 'Inventory', 'Predictions'],
                insights: this.businessInsights.recommendations,
                metrics: this.realTimeData
            };
            
            const blob = new Blob([JSON.stringify(report, null, 2)], 
                { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `business-report-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.addNotification('✅ Business report generated and downloaded!', 'success');
        }, 2000);
    }

    refreshAllData() {
        this.addNotification('🔄 Refreshing all data sources...', 'info');
        
        // Refresh based on current section
        switch(this.currentSection) {
            case 'analytics':
                this.loadAnalyticsSection();
                break;
            case 'customers':
                this.loadCustomersSection();
                break;
            case 'inventory':
                this.loadInventorySection();
                break;
            default:
                this.updateRealTimeMetrics();
        }
    }

    updateRealTimeMetrics() {
        // Simulate real-time updates
        this.realTimeData.conversations += Math.floor(Math.random() * 5);
        this.realTimeData.leads += Math.floor(Math.random() * 2);
        this.realTimeData.revenue += Math.floor(Math.random() * 2000);
        
        // Update dashboard if visible
        if (this.currentSection === 'dashboard') {
            this.updateDashboardMetrics();
        }
    }

    updateDashboardMetrics() {
        const statsCards = document.querySelectorAll('.stat-number');
        if (statsCards.length >= 4) {
            statsCards[0].textContent = this.realTimeData.conversations.toLocaleString();
            statsCards[1].textContent = this.realTimeData.leads;
            statsCards[2].textContent = `₹${this.realTimeData.revenue.toLocaleString()}`;
            statsCards[3].textContent = `${this.realTimeData.satisfaction}%`;
        }
    }

    showVoiceHelp() {
        const helpCommands = Object.keys(this.voiceCommands).join(', ');
        this.addNotification(
            `🎤 Available voice commands: ${helpCommands}`, 
            'info'
        );
    }

    executeVoiceCommand(command) {
        if (this.voiceCommands[command]) {
            this.voiceCommands[command]();
            this.addNotification(`✅ Executed: "${command}"`, 'success');
        }
    }

    refreshInsights() {
        const insightsList = document.getElementById('insightsList');
        if (insightsList) {
            insightsList.innerHTML = '<div class="insight-item">🔄 Refreshing insights...</div>';
            
            setTimeout(() => {
                insightsList.innerHTML = this.businessInsights.recommendations.map(insight => 
                    `<div class="insight-item">${insight}</div>`
                ).join('');
                
                this.addNotification('🧠 Business insights refreshed!', 'success');
            }, 1500);
        }
    }

    // Charts initialization
    initializeCharts(data) {
        this.createSalesChart(data);
        this.createModelsChart(data);
        this.createQuarterlyChart(data);
        this.createRevenueChart(data);
    }

    createSalesChart(data) {
        const ctx = document.getElementById('salesChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Sales (₹ Lakhs)',
                    data: data.marketTrends.monthly,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createModelsChart(data) {
        const ctx = document.getElementById('modelsChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.topModels.map(m => m.name),
                datasets: [{
                    label: 'Units Sold',
                    data: data.topModels.map(m => m.sales),
                    backgroundColor: ['#2563eb', '#7c3aed', '#10b981'],
                    borderColor: ['#1d4ed8', '#6d28d9', '#059669'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createQuarterlyChart(data) {
        const ctx = document.getElementById('quarterlyChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                datasets: [{
                    data: data.marketTrends.quarterly,
                    backgroundColor: ['#2563eb', '#7c3aed', '#10b981', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createRevenueChart(data) {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        const revenueData = [
            this.realTimeData.revenue * 0.4, // Direct Sales
            this.realTimeData.revenue * 0.3, // Online Sales
            this.realTimeData.revenue * 0.2, // Partnerships
            this.realTimeData.revenue * 0.1  // Other
        ];

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Direct Sales', 'Online Sales', 'Partnerships', 'Other'],
                datasets: [{
                    data: revenueData,
                    backgroundColor: ['#2563eb', '#7c3aed', '#10b981', '#f59e0b'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Advanced PDF Report Generation
    async generateAdvancedPDFReport() {
        this.showReportProgress();
        
        try {
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('p', 'mm', 'a4');
            
            // Get current data
            const analyticsData = await this.fetchAnalyticsData();
            const customersData = await this.fetchCustomersData();
            const inventoryData = await this.fetchInventoryData();
            
            this.updateReportProgress(20);
            
            // Page 1: Cover & Executive Summary
            await this.addCoverPage(pdf);
            
            this.updateReportProgress(30);
            
            // Page 2: Analytics with Charts
            pdf.addPage();
            await this.addAnalyticsPage(pdf, analyticsData);
            
            this.updateReportProgress(50);
            
            // Page 3: Customer Analysis
            pdf.addPage();
            await this.addCustomersPage(pdf, customersData);
            
            this.updateReportProgress(70);
            
            // Page 4: Inventory Report
            pdf.addPage();
            await this.addInventoryPage(pdf, inventoryData);
            
            this.updateReportProgress(85);
            
            // Page 5: Business Insights & Recommendations
            pdf.addPage();
            await this.addInsightsPage(pdf);
            
            this.updateReportProgress(95);
            
            // Generate and download
            const fileName = `VoiceBot-Enterprise-Report-${new Date().toISOString().split('T')[0]}.pdf`;
            pdf.save(fileName);
            
            this.updateReportProgress(100);
            
            setTimeout(() => {
                this.hideReportProgress();
                this.addNotification('📊 Advanced PDF report with charts generated successfully!', 'success');
            }, 1000);
            
        } catch (error) {
            console.error('PDF generation failed:', error);
            this.hideReportProgress();
            this.addNotification('❌ PDF generation failed. Please try again.', 'error');
        }
    }

    showReportProgress() {
        const progressHTML = `
            <div class="report-generating" id="reportProgress">
                <h3>📊 Generating Advanced PDF Report</h3>
                <p>Please wait while we create your comprehensive business report with visualized charts...</p>
                <div class="report-progress">
                    <div class="report-progress-bar" id="progressBar" style="width: 0%"></div>
                </div>
                <div id="progressText">Initializing...</div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', progressHTML);
    }

    updateReportProgress(percent) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) progressBar.style.width = `${percent}%`;
        
        if (progressText) {
            const messages = {
                20: 'Fetching real-time data...',
                30: 'Creating cover page...',
                50: 'Generating analytics charts...',
                70: 'Processing customer data...',
                85: 'Compiling inventory report...',
                95: 'Adding business insights...',
                100: 'Finalizing PDF...'
            };
            progressText.textContent = messages[percent] || 'Processing...';
        }
    }

    hideReportProgress() {
        const progress = document.getElementById('reportProgress');
        if (progress) progress.remove();
    }

    async addCoverPage(pdf) {
        // Cover page styling
        pdf.setFillColor(37, 99, 235);
        pdf.rect(0, 0, 210, 297, 'F');
        
        // Title
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(24);
        pdf.setFont('helvetica', 'bold');
        pdf.text('VoiceBot Enterprise', 105, 80, { align: 'center' });
        
        pdf.setFontSize(18);
        pdf.text('Business Analytics Report', 105, 100, { align: 'center' });
        
        // Date
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'normal');
        const currentDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        pdf.text(`Generated on: ${currentDate}`, 105, 120, { align: 'center' });
        
        // Executive Summary Box
        pdf.setFillColor(255, 255, 255);
        pdf.rect(20, 150, 170, 80, 'F');
        
        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(14);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Executive Summary', 30, 165);
        
        pdf.setFontSize(10);
        pdf.setFont('helvetica', 'normal');
        const summary = [
            `• Total Conversations: ${this.realTimeData.conversations.toLocaleString()}`,
            `• Active Leads: ${this.realTimeData.leads}`,
            `• Revenue Generated: ₹${this.realTimeData.revenue.toLocaleString()}`,
            `• Customer Satisfaction: ${this.realTimeData.satisfaction}%`,
            `• Report includes real-time analytics, customer insights,`,
            `  inventory status, and AI-powered recommendations`
        ];
        
        summary.forEach((line, index) => {
            pdf.text(line, 30, 180 + (index * 8));
        });
    }

    async addAnalyticsPage(pdf, data) {
        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.text('📊 Analytics Dashboard', 20, 20);
        
        // Capture charts as images and add to PDF
        const charts = ['salesChart', 'modelsChart', 'quarterlyChart', 'revenueChart'];
        let yPosition = 40;
        
        for (let i = 0; i < charts.length; i += 2) {
            for (let j = 0; j < 2 && (i + j) < charts.length; j++) {
                const chartElement = document.getElementById(charts[i + j]);
                if (chartElement) {
                    try {
                        const canvas = await html2canvas(chartElement.parentElement, {
                            backgroundColor: '#ffffff',
                            scale: 2
                        });
                        
                        const imgData = canvas.toDataURL('image/png');
                        const xPos = j === 0 ? 20 : 110;
                        pdf.addImage(imgData, 'PNG', xPos, yPosition, 80, 60);
                    } catch (error) {
                        console.warn('Chart capture failed:', error);
                    }
                }
            }
            yPosition += 70;
        }
        
        // Add key metrics
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Key Performance Indicators:', 20, yPosition + 20);
        
        pdf.setFont('helvetica', 'normal');
        const metrics = [
            `Sales Growth: ${data.salesGrowth}% (Quarter over Quarter)`,
            `Customer Acquisition: ${data.customerAcquisition} new customers`,
            `Revenue Increase: ${data.revenueIncrease}% (Year over Year)`,
            `Top Performing Model: ${data.topModels[0].name} (${data.topModels[0].sales} units)`
        ];
        
        metrics.forEach((metric, index) => {
            pdf.text(`• ${metric}`, 25, yPosition + 35 + (index * 8));
        });
    }

    async addCustomersPage(pdf, customers) {
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.text('👥 Customer Analytics', 20, 20);
        
        // Customer statistics
        const vipCustomers = customers.filter(c => c.status === 'VIP').length;
        const totalValue = customers.reduce((sum, c) => sum + c.value, 0);
        
        pdf.setFontSize(12);
        pdf.text('Customer Overview:', 20, 40);
        
        pdf.setFont('helvetica', 'normal');
        const customerStats = [
            `Total Customers: ${customers.length}`,
            `VIP Customers: ${vipCustomers}`,
            `Average Customer Value: ₹${Math.round(totalValue / customers.length).toLocaleString()}`,
            `Total Customer Value: ₹${totalValue.toLocaleString()}`
        ];
        
        customerStats.forEach((stat, index) => {
            pdf.text(`• ${stat}`, 25, 55 + (index * 8));
        });
        
        // Top customers table
        pdf.setFont('helvetica', 'bold');
        pdf.text('Top 10 Customers by Value:', 20, 100);
        
        const topCustomers = customers.sort((a, b) => b.value - a.value).slice(0, 10);
        
        // Table headers
        pdf.setFontSize(9);
        pdf.text('Name', 25, 115);
        pdf.text('Status', 80, 115);
        pdf.text('Location', 110, 115);
        pdf.text('Value (₹)', 160, 115);
        
        pdf.setFont('helvetica', 'normal');
        topCustomers.forEach((customer, index) => {
            const y = 125 + (index * 8);
            pdf.text(customer.name.substring(0, 20), 25, y);
            pdf.text(customer.status, 80, y);
            pdf.text(customer.location.substring(0, 15), 110, y);
            pdf.text(customer.value.toLocaleString(), 160, y);
        });
    }

    async addInventoryPage(pdf, inventory) {
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.text('📦 Inventory Report', 20, 20);
        
        const totalStock = inventory.reduce((sum, item) => sum + item.stock, 0);
        const lowStockItems = inventory.filter(item => item.status === 'Low Stock').length;
        const totalValue = inventory.reduce((sum, item) => sum + (item.stock * item.price), 0);
        
        pdf.setFontSize(12);
        pdf.text('Inventory Summary:', 20, 40);
        
        pdf.setFont('helvetica', 'normal');
        const inventoryStats = [
            `Total Items: ${inventory.length}`,
            `Total Stock Units: ${totalStock}`,
            `Low Stock Alerts: ${lowStockItems}`,
            `Total Inventory Value: ₹${totalValue.toLocaleString()}`
        ];
        
        inventoryStats.forEach((stat, index) => {
            pdf.text(`• ${stat}`, 25, 55 + (index * 8));
        });
        
        // Inventory table
        pdf.setFont('helvetica', 'bold');
        pdf.text('Current Inventory Status:', 20, 100);
        
        pdf.setFontSize(9);
        pdf.text('Model', 25, 115);
        pdf.text('Brand', 70, 115);
        pdf.text('Stock', 100, 115);
        pdf.text('Price (₹)', 130, 115);
        pdf.text('Status', 170, 115);
        
        pdf.setFont('helvetica', 'normal');
        inventory.slice(0, 15).forEach((item, index) => {
            const y = 125 + (index * 8);
            pdf.text(item.model.substring(0, 15), 25, y);
            pdf.text(item.brand, 70, y);
            pdf.text(item.stock.toString(), 100, y);
            pdf.text(item.price.toLocaleString(), 130, y);
            
            if (item.status === 'Low Stock') {
                pdf.setTextColor(220, 38, 38);
            } else {
                pdf.setTextColor(16, 185, 129);
            }
            pdf.text(item.status, 170, y);
            pdf.setTextColor(0, 0, 0);
        });
    }

    async addInsightsPage(pdf) {
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.text('🧠 AI Business Insights & Recommendations', 20, 20);
        
        pdf.setFontSize(12);
        pdf.text('AI-Powered Recommendations:', 20, 40);
        
        pdf.setFont('helvetica', 'normal');
        this.businessInsights.recommendations.forEach((insight, index) => {
            // Remove emoji for PDF
            const cleanInsight = insight.replace(/[\u{1F300}-\u{1F6FF}]/gu, '');
            pdf.text(`• ${cleanInsight}`, 25, 55 + (index * 12));
        });
        
        // Future predictions
        pdf.setFont('helvetica', 'bold');
        pdf.text('Future Projections:', 20, 180);
        
        pdf.setFont('helvetica', 'normal');
        const projections = [
            'Sales expected to grow 15-20% next quarter based on current trends',
            'Customer acquisition rate showing positive momentum',
            'Inventory optimization recommended for top-selling models',
            'Voice AI adoption increasing customer engagement by 40%'
        ];
        
        projections.forEach((projection, index) => {
            pdf.text(`• ${projection}`, 25, 195 + (index * 10));
        });
        
        // Footer
        pdf.setFontSize(8);
        pdf.setTextColor(100, 100, 100);
        pdf.text('Generated by VoiceBot Enterprise AI Analytics System', 105, 280, { align: 'center' });
    }

    // Real-time data fetching methods
    async fetchAnalyticsData() {
        try {
            console.log('📊 Fetching analytics data...');
            
            // Simulate business analytics with real crypto data for demo
            const cryptoResponse = await fetch(this.apis.crypto);
            const cryptoData = await cryptoResponse.json();
            
            // Generate analytics metrics using crypto price as base
            const btcPrice = parseFloat(cryptoData.bpi.USD.rate.replace(/,/g, ''));
            
            return {
                salesGrowth: (btcPrice % 100).toFixed(1),
                customerAcquisition: Math.floor(btcPrice % 50) + 20,
                revenueIncrease: (btcPrice % 30).toFixed(1),
                marketTrends: {
                    quarterly: Array.from({length: 4}, (_, i) => Math.floor(btcPrice % (100 + i * 10))),
                    monthly: Array.from({length: 12}, (_, i) => Math.floor(btcPrice % (80 + i * 5)))
                },
                topModels: [
                    { name: 'Honda Activa', sales: Math.floor(btcPrice % 200) + 100 },
                    { name: 'TVS Jupiter', sales: Math.floor(btcPrice % 150) + 80 },
                    { name: 'Bajaj Pulsar', sales: Math.floor(btcPrice % 120) + 60 }
                ]
            };
        } catch (error) {
            console.error('Analytics data fetch failed:', error);
            return this.generateMockAnalytics();
        }
    }

    async fetchInventoryData() {
        try {
            console.log('📦 Fetching inventory data...');
            
            // Use JSONPlaceholder for mock inventory data
            const response = await fetch(`${this.apis.jsonPlaceholder}/posts?_limit=20`);
            const posts = await response.json();
            
            // Transform posts into inventory items
            const inventory = posts.map((post, index) => ({
                id: post.id,
                model: `Model ${String.fromCharCode(65 + (index % 26))}${post.id}`,
                brand: ['Honda', 'TVS', 'Bajaj', 'Yamaha', 'Hero'][index % 5],
                stock: Math.floor(Math.random() * 50) + 10,
                price: Math.floor(Math.random() * 100000) + 50000,
                status: Math.random() > 0.8 ? 'Low Stock' : 'In Stock',
                lastUpdated: new Date().toISOString()
            }));
            
            return inventory;
        } catch (error) {
            console.error('Inventory data fetch failed:', error);
            return this.generateMockInventory();
        }
    }

    async fetchCustomersData() {
        try {
            console.log('👥 Fetching customers data...');
            
            // Use Random User API for realistic customer data
            const response = await fetch(`${this.apis.randomUser}?results=15&nat=in`);
            const userData = await response.json();
            
            // Transform to customer format
            const customers = userData.results.map((user, index) => ({
                id: index + 1,
                name: `${user.name.first} ${user.name.last}`,
                email: user.email,
                phone: user.phone,
                location: `${user.location.city}, ${user.location.state}`,
                avatar: user.picture.medium,
                status: ['Prospect', 'Lead', 'Customer', 'VIP'][Math.floor(Math.random() * 4)],
                lastContact: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
                purchaseHistory: Math.floor(Math.random() * 3),
                value: Math.floor(Math.random() * 500000) + 50000
            }));
            
            return customers;
        } catch (error) {
            console.error('Customer data fetch failed:', error);
            return this.generateMockCustomers();
        }
    }

    generateMockAnalytics() {
        return {
            salesGrowth: (Math.random() * 20 + 5).toFixed(1),
            customerAcquisition: Math.floor(Math.random() * 30) + 20,
            revenueIncrease: (Math.random() * 25 + 10).toFixed(1),
            marketTrends: {
                quarterly: Array.from({length: 4}, () => Math.floor(Math.random() * 100)),
                monthly: Array.from({length: 12}, () => Math.floor(Math.random() * 80))
            },
            topModels: [
                { name: 'Honda Activa', sales: Math.floor(Math.random() * 200) + 100 },
                { name: 'TVS Jupiter', sales: Math.floor(Math.random() * 150) + 80 },
                { name: 'Bajaj Pulsar', sales: Math.floor(Math.random() * 120) + 60 }
            ]
        };
    }

    generateMockInventory() {
        const brands = ['Honda', 'TVS', 'Bajaj', 'Yamaha', 'Hero'];
        return Array.from({length: 20}, (_, i) => ({
            id: i + 1,
            model: `Model ${String.fromCharCode(65 + (i % 26))}${i + 1}`,
            brand: brands[i % brands.length],
            stock: Math.floor(Math.random() * 50) + 10,
            price: Math.floor(Math.random() * 100000) + 50000,
            status: Math.random() > 0.8 ? 'Low Stock' : 'In Stock',
            lastUpdated: new Date().toISOString()
        }));
    }

    generateMockCustomers() {
        const names = ['Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sneha Singh', 'Vikram Rao'];
        return Array.from({length: 15}, (_, i) => ({
            id: i + 1,
            name: names[i % names.length] + ` ${i + 1}`,
            email: `customer${i + 1}@example.com`,
            phone: `+91 ${Math.floor(Math.random() * 9000000000) + 1000000000}`,
            location: ['Mumbai, Maharashtra', 'Delhi, Delhi', 'Bangalore, Karnataka'][i % 3],
            avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${i}`,
            status: ['Prospect', 'Lead', 'Customer', 'VIP'][Math.floor(Math.random() * 4)],
            lastContact: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
            purchaseHistory: Math.floor(Math.random() * 3),
            value: Math.floor(Math.random() * 500000) + 50000
        }));
    }

    async loadAnalyticsSection() {
        this.addSystemMessage('📊 Loading real-time analytics data...', 'info');
        
        try {
            const analyticsData = await this.fetchAnalyticsData();
            this.renderAnalyticsData(analyticsData);
            this.addSystemMessage('✅ Analytics data loaded successfully!', 'success');
        } catch (error) {
            this.addSystemMessage('⚠️ Using cached analytics data', 'warning');
        }
    }

    async loadCustomersSection() {
        this.addSystemMessage('👥 Loading real-time customer data...', 'info');
        
        try {
            const customersData = await this.fetchCustomersData();
            this.renderCustomersData(customersData);
            this.addSystemMessage('✅ Customer data loaded successfully!', 'success');
        } catch (error) {
            this.addSystemMessage('⚠️ Using cached customer data', 'warning');
        }
    }

    async loadInventorySection() {
        this.addSystemMessage('📦 Loading real-time inventory data...', 'info');
        
        try {
            const inventoryData = await this.fetchInventoryData();
            this.renderInventoryData(inventoryData);
            this.addSystemMessage('✅ Inventory data loaded successfully!', 'success');
        } catch (error) {
            this.addSystemMessage('⚠️ Using cached inventory data', 'warning');
        }
    }

    renderAnalyticsData(data) {
        const analyticsSection = document.getElementById('analytics');
        if (!analyticsSection) return;

        analyticsSection.innerHTML = `
            <div class="section-header">
                <h1>📊 Real-Time Analytics</h1>
                <p>Live business intelligence and performance metrics</p>
            </div>
            
            <div class="analytics-grid">
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Sales Growth</h3>
                        <span class="metric-trend positive">↗ ${data.salesGrowth}%</span>
                    </div>
                    <div class="metric-value">${data.salesGrowth}%</div>
                    <div class="metric-subtitle">This quarter</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>New Customers</h3>
                        <span class="metric-trend positive">↗ ${data.customerAcquisition}</span>
                    </div>
                    <div class="metric-value">${data.customerAcquisition}</div>
                    <div class="metric-subtitle">This month</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Revenue Growth</h3>
                        <span class="metric-trend positive">↗ ${data.revenueIncrease}%</span>
                    </div>
                    <div class="metric-value">${data.revenueIncrease}%</div>
                    <div class="metric-subtitle">Year over year</div>
                </div>
            </div>
            
            <!-- Charts Container -->
            <div class="charts-container">
                <div class="chart-card">
                    <h3>📈 Sales Trend (Monthly)</h3>
                    <canvas id="salesChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-card">
                    <h3>🎯 Top Models Performance</h3>
                    <canvas id="modelsChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-card">
                    <h3>📊 Quarterly Growth</h3>
                    <canvas id="quarterlyChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-card">
                    <h3>💰 Revenue Distribution</h3>
                    <canvas id="revenueChart" width="400" height="200"></canvas>
                </div>
            </div>
            
            <div class="top-models">
                <h3>🏆 Top Selling Models</h3>
                <div class="models-list">
                    ${data.topModels.map(model => `
                        <div class="model-item">
                            <span class="model-name">${model.name}</span>
                            <span class="model-sales">${model.sales} units</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="report-actions">
                <button onclick="app.generateAdvancedPDFReport()" class="pdf-report-btn">
                    📄 Generate PDF Report with Charts
                </button>
            </div>
        `;
        
        // Initialize charts after DOM is updated
        setTimeout(() => {
            this.initializeCharts(data);
        }, 100);
    }

    renderCustomersData(customers) {
        const customersSection = document.getElementById('customers');
        if (!customersSection) return;

        customersSection.innerHTML = `
            <div class="section-header">
                <h1>👥 Customer Management</h1>
                <p>Real-time customer data and CRM insights</p>
            </div>
            
            <div class="customers-stats">
                <div class="stat-item">
                    <span class="stat-label">Total Customers</span>
                    <span class="stat-value">${customers.length}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">VIP Customers</span>
                    <span class="stat-value">${customers.filter(c => c.status === 'VIP').length}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Active Leads</span>
                    <span class="stat-value">${customers.filter(c => c.status === 'Lead').length}</span>
                </div>
            </div>
            
            <div class="customers-table">
                <div class="table-header">
                    <span>Customer</span>
                    <span>Contact</span>
                    <span>Status</span>
                    <span>Value</span>
                    <span>Last Contact</span>
                </div>
                ${customers.map(customer => `
                    <div class="table-row">
                        <div class="customer-info">
                            <img src="${customer.avatar}" alt="${customer.name}" class="customer-avatar">
                            <div>
                                <div class="customer-name">${customer.name}</div>
                                <div class="customer-location">${customer.location}</div>
                            </div>
                        </div>
                        <div class="customer-contact">
                            <div>${customer.email}</div>
                            <div>${customer.phone}</div>
                        </div>
                        <span class="status-badge status-${customer.status.toLowerCase()}">${customer.status}</span>
                        <span class="customer-value">₹${customer.value.toLocaleString()}</span>
                        <span class="last-contact">${customer.lastContact}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderInventoryData(inventory) {
        const inventorySection = document.getElementById('inventory');
        if (!inventorySection) return;

        const totalStock = inventory.reduce((sum, item) => sum + item.stock, 0);
        const lowStockItems = inventory.filter(item => item.status === 'Low Stock').length;

        inventorySection.innerHTML = `
            <div class="section-header">
                <h1>📦 Inventory Management</h1>
                <p>Real-time stock levels and inventory tracking</p>
            </div>
            
            <div class="inventory-stats">
                <div class="stat-item">
                    <span class="stat-label">Total Items</span>
                    <span class="stat-value">${inventory.length}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Stock</span>
                    <span class="stat-value">${totalStock}</span>
                </div>
                <div class="stat-item warning">
                    <span class="stat-label">Low Stock Alerts</span>
                    <span class="stat-value">${lowStockItems}</span>
                </div>
            </div>
            
            <div class="inventory-grid">
                ${inventory.map(item => `
                    <div class="inventory-card ${item.status === 'Low Stock' ? 'low-stock' : ''}">
                        <div class="inventory-header">
                            <h3>${item.model}</h3>
                            <span class="brand-badge">${item.brand}</span>
                        </div>
                        <div class="inventory-details">
                            <div class="detail-row">
                                <span>Stock:</span>
                                <span class="stock-count">${item.stock} units</span>
                            </div>
                            <div class="detail-row">
                                <span>Price:</span>
                                <span class="price">₹${item.price.toLocaleString()}</span>
                            </div>
                            <div class="detail-row">
                                <span>Status:</span>
                                <span class="status ${item.status === 'Low Stock' ? 'warning' : 'success'}">${item.status}</span>
                            </div>
                        </div>
                        <div class="last-updated">
                            Updated: ${new Date(item.lastUpdated).toLocaleString()}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 VoiceBot Enterprise Loading...');
    window.app = new VoiceBotApp();
    console.log('✅ VoiceBot Enterprise Loaded Successfully!');
    
    // Register PWA Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('🔧 PWA: Service Worker registered successfully');
                window.app.addNotification('📱 App can be installed for offline use!', 'info');
            })
            .catch(error => {
                console.log('❌ PWA: Service Worker registration failed');
            });
    }
    
    // PWA Install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Show install button/notification
        window.app.addNotification('📲 Install VoiceBot as an app for better experience!', 'info');
        
        // Add install button to header
        const installBtn = document.createElement('button');
        installBtn.innerHTML = '📲 Install App';
        installBtn.className = 'install-btn';
        installBtn.onclick = () => {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    window.app.addNotification('🎉 App installed successfully!', 'success');
                }
                deferredPrompt = null;
                installBtn.remove();
            });
        };
        
        const header = document.querySelector('.header-actions') || document.querySelector('.header');
        if (header) {
            header.appendChild(installBtn);
        }
    });
});

// Global functions for HTML compatibility
function askSampleQuestion(question) {
    console.log('🤖 Sample question:', question);
    if (window.app) {
        window.app.addMessage(question, 'user');
        setTimeout(() => {
            window.app.addMessage('This is a sample response to: ' + question, 'bot');
        }, 1000);
    }
}

function sendMessage() {
    console.log('📤 Sending message...');
    const input = document.getElementById('messageInput');
    if (input && input.value.trim()) {
        if (window.app) {
            window.app.addMessage(input.value, 'user');
            input.value = '';
            setTimeout(() => {
                window.app.addMessage('Thank you for your message. How can I help you today?', 'bot');
            }, 1000);
        }
    }
}

function toggleVoiceRecording() {
    console.log('🎤 Toggling voice recording...');
    if (window.app) {
        if (window.app.isListening) {
            window.app.stopListening();
        } else {
            window.app.startListening();
        }
    }
}

// Add typing animation CSS
const typingCSS = `
.typing-dots {
    display: flex;
    gap: 4px;
    padding: 8px 0;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--primary-500);
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: 0ms; }
.typing-dots span:nth-child(2) { animation-delay: 160ms; }
.typing-dots span:nth-child(3) { animation-delay: 320ms; }

@keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

.system-avatar {
    background: var(--neutral-400);
    color: white;
}

.user-avatar {
    background: var(--secondary-500);
    color: white;
}

.system-bubble {
    background: var(--neutral-100);
    border-color: var(--neutral-300);
}

.system-bubble.info { border-left: 4px solid var(--primary-500); }
.system-bubble.success { border-left: 4px solid var(--success-500); }
.system-bubble.warning { border-left: 4px solid var(--warning-500); }
.system-bubble.error { border-left: 4px solid var(--error-500); }

.user-bubble {
    background: var(--secondary-50);
    border-color: var(--secondary-200);
}
`;

// Inject typing animation CSS
const style = document.createElement('style');
style.textContent = typingCSS;
document.head.appendChild(style);
