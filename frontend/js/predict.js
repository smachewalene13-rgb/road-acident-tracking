// frontend/js/predict.js
const API_BASE_URL = 'http://localhost:5000/api';

// Check authentication
const token = localStorage.getItem('access_token');
console.log('Token exists:', !!token);

if (!token && window.location.pathname.includes('predict.html')) {
    console.log('No token found, redirecting to login');
    window.location.href = 'login.html';
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

// Get DOM elements
const predictionForm = document.getElementById('predictionForm');
const loadingSpinner = document.getElementById('loadingSpinner');
const predictionResult = document.getElementById('predictionResult');
const noResultMessage = document.getElementById('noResultMessage');

// Function to display prediction results
function displayPrediction(prediction) {
    console.log('Displaying prediction:', prediction);
    
    const severityBadge = document.getElementById('severityBadge');
    const confidenceFill = document.getElementById('confidenceFill');
    const recommendationsDiv = document.getElementById('recommendations');
    
    const severity = prediction.severity;
    const confidence = prediction.confidence;
    const riskScore = prediction.risk_score;
    const recommendations = prediction.recommendations || [];
    
    let bgColor, icon, severityText;
    
    if (severity === 'High') {
        bgColor = '#ef4444';
        icon = 'fa-skull-crosswalk';
        severityText = 'High Severity';
    } else if (severity === 'Medium') {
        bgColor = '#f59e0b';
        icon = 'fa-exclamation-triangle';
        severityText = 'Medium Severity';
    } else {
        bgColor = '#10b981';
        icon = 'fa-check-circle';
        severityText = 'Low Severity';
    }
    
    severityBadge.style.display = 'block';
    severityBadge.style.background = `linear-gradient(135deg, ${bgColor}, ${bgColor}dd)`;
    severityBadge.innerHTML = `
        <i class="fas ${icon}" style="font-size: 3rem; margin-bottom: 10px;"></i>
        <h3 style="font-size: 1.5rem; margin: 10px 0;">${severityText}</h3>
        <p style="margin: 0;">Risk Score: ${riskScore}/25</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Confidence: ${confidence}%</p>
    `;
    
    confidenceFill.style.width = `${confidence}%`;
    confidenceFill.innerHTML = `${confidence}%`;
    confidenceFill.style.background = `linear-gradient(90deg, ${bgColor}, ${bgColor}aa)`;
    
    if (recommendations.length > 0) {
        recommendationsDiv.innerHTML = `
            <h4 style="margin-bottom: 15px; color: #1f2937;">
                <i class="fas fa-lightbulb" style="color: #f59e0b;"></i> Safety Recommendations
            </h4>
            <ul style="list-style: none; padding-left: 0;">
                ${recommendations.map(rec => `
                    <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                        <span style="position: absolute; left: 0; color: ${bgColor};">→</span>
                        ${rec}
                    </li>
                `).join('')}
            </ul>
        `;
    }
    
    predictionResult.style.display = 'block';
    noResultMessage.style.display = 'none';
    predictionResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(message) {
    console.error('Error:', message);
    
    predictionResult.style.display = 'block';
    predictionResult.innerHTML = `
        <div style="background: #fee2e2; color: #dc2626; padding: 20px; border-radius: 12px; text-align: center;">
            <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
            <h4>Error</h4>
            <p>${message}</p>
        </div>
    `;
    noResultMessage.style.display = 'none';
}

// Handle form submission
if (predictionForm) {
    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('Please login first');
            window.location.href = 'login.html';
            return;
        }
        
        loadingSpinner.style.display = 'block';
        predictionResult.style.display = 'none';
        noResultMessage.style.display = 'none';
        
        const formData = {
            weather: document.getElementById('weather').value,
            road_condition: document.getElementById('roadCondition').value,
            light_condition: document.getElementById('lightCondition')?.value || 'Daylight',
            speed_limit: parseInt(document.getElementById('speedLimit').value) || 50,
            vehicle_type: document.getElementById('vehicleType')?.value || 'Car',
            driver_age: parseInt(document.getElementById('driverAge')?.value) || 35,
            time_of_day: document.getElementById('timeOfDay')?.value || 'Afternoon',
            day_of_week: document.getElementById('dayOfWeek')?.value || 'Monday',
            traffic_density: document.getElementById('trafficDensity').value || 'Medium',
            alcohol_involved: document.getElementById('alcoholInvolved')?.checked || false,
            speeding: document.getElementById('speeding')?.checked || false
        };
        
        if (!formData.weather || !formData.road_condition) {
            loadingSpinner.style.display = 'none';
            showError('Please select Weather and Road Condition');
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/predict/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            console.log('Response:', data);
            
            loadingSpinner.style.display = 'none';
            
            if (response.ok && data.success) {
                displayPrediction(data.prediction);
            } else {
                showError(data.error || 'Prediction failed');
            }
        } catch (error) {
            console.error('Error:', error);
            loadingSpinner.style.display = 'none';
            showError('Network error: ' + error.message);
        }
    });
}

console.log('predict.js loaded');