// frontend/js/dashboard.js
const API_BASE_URL = 'http://localhost:5000/api';

// Check authentication
const token = localStorage.getItem('access_token');
if (!token && window.location.pathname.includes('dashboard.html')) {
    window.location.href = 'login.html';
}

// Display user name
const user = JSON.parse(localStorage.getItem('user') || '{}');
const welcomeUser = document.getElementById('welcomeUser');
if (welcomeUser) {
    welcomeUser.innerHTML = `Welcome back, ${user.full_name || user.username}!`;
}

// Logout functionality
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    });
}

// Load dashboard data
async function loadDashboard() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/accidents/statistics`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const stats = await response.json();
            console.log('Stats:', stats);
            
            // Update stats cards
            document.getElementById('totalPredictions').innerText = stats.total_predictions || 0;
            document.getElementById('highRiskAlerts').innerText = stats.high_risk_count || 0;
            document.getElementById('avgConfidence').innerText = `${stats.average_confidence || 0}%`;
            
            // Update chart if exists
            if (window.severityChart && stats.severity_distribution) {
                window.severityChart.data.datasets[0].data = [
                    stats.severity_distribution.Low || 0,
                    stats.severity_distribution.Medium || 0,
                    stats.severity_distribution.High || 0
                ];
                window.severityChart.update();
            }
        }
        
        // Load recent predictions
        await loadRecentPredictions();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load recent predictions
async function loadRecentPredictions() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/history`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById('recentPredictions');
            const predictions = data.predictions || [];
            
            if (predictions.length === 0) {
                container.innerHTML = '<div class="no-data">No predictions yet. Make your first prediction!</div>';
                return;
            }
            
            container.innerHTML = predictions.slice(0, 10).map(p => {
                let severityClass = '';
                if (p.predicted_severity === 'Low') severityClass = 'severity-low';
                else if (p.predicted_severity === 'Medium') severityClass = 'severity-medium';
                else severityClass = 'severity-high';
                
                return `
                    <div class="history-item">
                        <div class="history-date">${new Date(p.created_at).toLocaleDateString()}</div>
                        <div class="history-details">
                            <div class="history-weather">Weather: ${p.weather || 'N/A'} | Speed: ${p.speed_limit || 'N/A'} km/h</div>
                        </div>
                        <div class="history-severity ${severityClass}">${p.predicted_severity}</div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

// Initialize chart
const ctx = document.getElementById('severityChart')?.getContext('2d');
if (ctx) {
    window.severityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low', 'Medium', 'High'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load dashboard
loadDashboard();