// Global variables
let currentUser = null;
let searchTimeout = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    console.log('🚀 Q&A Platform initialized');
    
    // Check if user is logged in
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateLoginState();
    }
    
    // Set active navigation
    updateActiveNavigation();
}

function setupEventListeners() {
    // Search functionality
    const searchBar = document.getElementById('searchBar');
    const searchBtn = document.getElementById('searchBtn');
    
    if (searchBar) {
        searchBar.addEventListener('input', handleSearchInput);
        searchBar.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
    
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    
    // Ask form submission
    const askForm = document.getElementById('askForm');
    if (askForm) {
        askForm.addEventListener('submit', handleAskSubmission);
    }
    
    // Modal close events
    window.addEventListener('click', function(e) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.classList.remove('show');
                modal.style.display = 'none';
            }
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape to close modals
        if (e.key === 'Escape') {
            closeAllModals();
        }
        
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchBar?.focus();
        }
    });
}

// Navigation functions
function updateActiveNavigation() {
    const path = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === path || 
            (path === '/' && item.getAttribute('href') === '/')) {
            item.classList.add('active');
        }
    });
}

// Modal functions
function openAskModal() {
    const modal = document.getElementById('askModal');
    const aiResponse = document.getElementById('aiResponse');
    
    // Reset form and hide previous response
    document.getElementById('askForm').reset();
    aiResponse.style.display = 'none';
    
    modal.style.display = 'flex';
    modal.classList.add('show');
    
    // Focus on the question input
    setTimeout(() => {
        document.getElementById('questionTitle')?.focus();
    }, 100);
}

function closeAskModal() {
    const modal = document.getElementById('askModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

function closeSearchModal() {
    const modal = document.getElementById('searchModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    });
}

// Search functionality
function handleSearchInput(e) {
    const query = e.target.value.trim();
    
    // Clear previous timeout
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // Debounce search
    if (query.length >= 2) {
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 500);
    }
}

async function performSearch(query = null) {
    const searchBar = document.getElementById('searchBar');
    const searchQuery = query || searchBar.value.trim();
    
    if (!searchQuery) {
        showMessage('Please enter a search term', 'error');
        return;
    }
    
    try {
        // Show loading state
        const searchBtn = document.getElementById('searchBtn');
        const originalText = searchBtn.innerHTML;
        searchBtn.innerHTML = '<div class="loading"></div>';
        
        const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}`);
        const results = await response.json();
        
        // Restore button
        searchBtn.innerHTML = originalText;
        
        displaySearchResults(results, searchQuery);
        
    } catch (error) {
        console.error('Search error:', error);
        showMessage('Search failed. Please try again.', 'error');
    }
}

function displaySearchResults(results, query) {
    const modal = document.getElementById('searchModal');
    const resultsContainer = document.getElementById('searchResults');
    
    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--secondary-text);">
                <h3>No results found for "${query}"</h3>
                <p>Try different keywords or ask a new question.</p>
                <button onclick="openAskModal(); closeSearchModal();" class="submit-btn" style="margin-top: 20px;">
                    Ask Your Question
                </button>
            </div>
        `;
    } else {
        resultsContainer.innerHTML = `
            <div style="margin-bottom: 20px; padding: 0 24px;">
                <p><strong>${results.length}</strong> result${results.length !== 1 ? 's' : ''} for "<strong>${query}</strong>"</p>
            </div>
            ${results.map(result => `
                <div class="question-item" onclick="viewQuestion(${result.id}); closeSearchModal();">
                    <div class="question-title">${highlightSearchTerm(result.title, query)}</div>
                    <div class="question-meta">
                        <span>${result.category}</span>
                        <span>${result.answers} answers</span>
                        <span>${result.timestamp}</span>
                    </div>
                </div>
            `).join('')}
        `;
    }
    
    modal.style.display = 'flex';
    modal.classList.add('show');
}

function highlightSearchTerm(text, term) {
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark style="background: #fef08a; padding: 2px 4px; border-radius: 3px;">$1</mark>');
}

// Ask question functionality
async function handleAskSubmission(e) {
    e.preventDefault();
    
    const question = document.getElementById('questionTitle').value.trim();
    const category = document.getElementById('questionCategory').value;
    
    if (!question) {
        showMessage('Please enter your question', 'error');
        return;
    }
    
    try {
        // Show loading state
        const submitBtn = e.target.querySelector('.submit-btn');
        const submitText = document.getElementById('submitText');
        const loadingText = document.getElementById('loadingText');
        
        submitBtn.disabled = true;
        submitText.style.display = 'none';
        loadingText.style.display = 'inline';
        
        // Send question to backend
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                category: category
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Display AI response
            const aiResponse = document.getElementById('aiResponse');
            const aiAnswerText = document.getElementById('aiAnswerText');
            
            aiAnswerText.innerHTML = formatAIResponse(result.answer);
            aiResponse.style.display = 'block';
            
            // Scroll to response
            aiResponse.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            showMessage('Your question has been answered!', 'success');
        } else {
            throw new Error(result.error || 'Failed to get answer');
        }
        
    } catch (error) {
        console.error('Error submitting question:', error);
        showMessage('Failed to get answer. Please try again.', 'error');
    } finally {
        // Restore button state
        const submitBtn = document.querySelector('.submit-btn');
        const submitText = document.getElementById('submitText');
        const loadingText = document.getElementById('loadingText');
        
        submitBtn.disabled = false;
        submitText.style.display = 'inline';
        loadingText.style.display = 'none';
    }
}

function formatAIResponse(response) {
    // Format the AI response with better styling
    return response
        .split('\n\n')
        .map(paragraph => `<p style="margin-bottom: 12px;">${paragraph}</p>`)
        .join('');
}

// Login functionality
function showLogin() {
    // Simple login simulation
    const email = prompt('Enter your email:');
    if (email) {
        currentUser = {
            email: email,
            name: email.split('@')[0],
            loginTime: new Date().toISOString()
        };
        
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        updateLoginState();
        showMessage(`Welcome back, ${currentUser.name}!`, 'success');
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    updateLoginState();
    showMessage('Logged out successfully', 'success');
}

function updateLoginState() {
    const loginBtn = document.querySelector('.login-btn');
    if (currentUser) {
        loginBtn.textContent = `👤 ${currentUser.name}`;
        loginBtn.onclick = logout;
    } else {
        loginBtn.textContent = 'Login';
        loginBtn.onclick = showLogin;
    }
}

// Utility functions
function showMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    messageEl.textContent = message;
    messageEl.style.position = 'fixed';
    messageEl.style.top = '20px';
    messageEl.style.right = '20px';
    messageEl.style.zIndex = '9999';
    messageEl.style.minWidth = '300px';
    messageEl.style.animation = 'slideInRight 0.3s ease';
    
    document.body.appendChild(messageEl);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        messageEl.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 300);
    }, 3000);
}

function viewQuestion(questionId) {
    // Navigate to question detail (in a real app)
    window.location.href = `/questions#question-${questionId}`;
}

// Add CSS animations for messages
const messageStyles = document.createElement('style');
messageStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(messageStyles);

// Expose functions globally for onclick handlers
window.openAskModal = openAskModal;
window.closeAskModal = closeAskModal;
window.closeSearchModal = closeSearchModal;
window.showLogin = showLogin;
window.viewQuestion = viewQuestion;