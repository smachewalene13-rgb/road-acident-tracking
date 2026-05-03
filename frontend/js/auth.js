const API_BASE_URL = 'http://localhost:5000/api';

// Register
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }
        
        const userData = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: password,
            full_name: document.getElementById('fullName').value
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showSuccess('Registration successful! Please login.');
                setTimeout(() => window.location.href = 'login.html', 2000);
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError('Network error. Please try again.');
        }
    });
}

// Login
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const loginData = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(loginData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                showSuccess('Login successful! Redirecting...');
                setTimeout(() => window.location.href = 'dashboard.html', 1500);
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError('Network error. Please try again.');
        }
    });
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    const form = document.querySelector('.auth-form');
    if (form) form.prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    const form = document.querySelector('.auth-form');
    if (form) form.prepend(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}