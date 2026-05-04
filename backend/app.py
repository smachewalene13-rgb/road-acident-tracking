from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pathlib import Path
import random
import os
import re
import sqlite3

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

# Create Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Setup paths
backend_dir = Path(__file__).parent.resolve()
database_dir = backend_dir / 'database'
database_dir.mkdir(exist_ok=True)
db_path = database_dir / 'accident_prediction.db'

# Configuration
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production-12345'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production-67890'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

# Initialize extensions with app
db.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5000'])

# ==================== JWT CONFIGURATION ====================

@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    try:
        return User.query.get(int(identity))
    except:
        return None

@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({'error': 'Missing or invalid token', 'message': 'Please login to access this resource'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token', 'message': str(error)}), 401

# ==================== MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20), default='')
    role = db.Column(db.String(50), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name or '',
            'phone': self.phone or '',
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class AccidentPrediction(db.Model):
    __tablename__ = 'accident_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Input features
    weather = db.Column(db.String(50))
    road_condition = db.Column(db.String(50))
    light_condition = db.Column(db.String(50))
    speed_limit = db.Column(db.Integer)
    vehicle_type = db.Column(db.String(50))
    driver_age = db.Column(db.Integer)
    time_of_day = db.Column(db.String(50))
    day_of_week = db.Column(db.String(20))
    traffic_density = db.Column(db.String(50))
    alcohol_involved = db.Column(db.Boolean, default=False)
    speeding = db.Column(db.Boolean, default=False)
    
    # Prediction results
    predicted_severity = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)
    severity_score = db.Column(db.Float, default=0)
    
    # Feedback
    actual_severity = db.Column(db.String(50))
    feedback_provided = db.Column(db.Boolean, default=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'weather': self.weather,
            'road_condition': self.road_condition,
            'light_condition': self.light_condition,
            'speed_limit': self.speed_limit,
            'vehicle_type': self.vehicle_type,
            'driver_age': self.driver_age,
            'time_of_day': self.time_of_day,
            'day_of_week': self.day_of_week,
            'traffic_density': self.traffic_density,
            'alcohol_involved': self.alcohol_involved,
            'speeding': self.speeding,
            'predicted_severity': self.predicted_severity,
            'confidence_score': self.confidence_score,
            'severity_score': self.severity_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==================== HELPER FUNCTIONS ====================

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def predict_severity(data):
    risk_score = 0
    
    weather_risk = {'Clear': 0, 'Rain': 2, 'Fog': 3, 'Snow': 4}
    risk_score += weather_risk.get(data.get('weather', 'Clear'), 0)
    
    road_risk = {'Dry': 0, 'Wet': 2, 'Icy': 4, 'Flooded': 3}
    risk_score += road_risk.get(data.get('road_condition', 'Dry'), 0)
    
    speed = int(data.get('speed_limit', 50))
    if speed > 80:
        risk_score += 3
    elif speed > 60:
        risk_score += 2
    elif speed > 40:
        risk_score += 1
    
    if data.get('speeding', False):
        risk_score += 2
    if data.get('alcohol_involved', False):
        risk_score += 3
    if data.get('traffic_density') == 'High':
        risk_score += 1
    
    if risk_score >= 10:
        severity = 'High'
        confidence = random.uniform(0.85, 0.95)
    elif risk_score >= 5:
        severity = 'Medium'
        confidence = random.uniform(0.75, 0.88)
    else:
        severity = 'Low'
        confidence = random.uniform(0.90, 0.98)
    
    recommendations = {
        'Low': ['✓ Drive cautiously', '✓ Stay alert', '✓ Follow traffic rules'],
        'Medium': ['⚠️ Reduce speed', '⚠️ Increase following distance', '⚠️ Check weather conditions'],
        'High': ['🚨 IMMEDIATE ACTION REQUIRED', '📞 Call emergency services', '🆘 Seek medical attention']
    }
    
    return {
        'severity': severity,
        'confidence': round(confidence * 100, 2),
        'risk_score': risk_score,
        'severity_score': (risk_score / 25) * 100,
        'recommendations': recommendations[severity]
    }

# ==================== CREATE TABLES ====================

with app.app_context():
    db.create_all()
    print(f"✅ Database ready at: {db_path}")

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    if os.path.exists(os.path.join('../frontend', path)):
        return send_from_directory('../frontend', path)
    return send_from_directory('../frontend', 'index.html')

# ==================== API ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Road Accident Prediction System is running',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email exists'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', ''),
            phone=data.get('phone', '')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User registered', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user.update_last_login()
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/', methods=['POST'])
@jwt_required()
def predict():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data.get('weather') or not data.get('road_condition'):
            return jsonify({'error': 'Weather and road condition are required'}), 400
        
        prediction_result = predict_severity(data)
        
        prediction = AccidentPrediction(
            user_id=user_id,
            weather=data.get('weather'),
            road_condition=data.get('road_condition'),
            light_condition=data.get('light_condition', 'Daylight'),
            speed_limit=data.get('speed_limit', 50),
            vehicle_type=data.get('vehicle_type', 'Car'),
            driver_age=data.get('driver_age', 35),
            time_of_day=data.get('time_of_day', 'Afternoon'),
            day_of_week=data.get('day_of_week', 'Monday'),
            traffic_density=data.get('traffic_density', 'Medium'),
            alcohol_involved=data.get('alcohol_involved', False),
            speeding=data.get('speeding', False),
            predicted_severity=prediction_result['severity'],
            confidence_score=prediction_result['confidence'],
            severity_score=prediction_result['severity_score']
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prediction': {
                'severity': prediction_result['severity'],
                'confidence': prediction_result['confidence'],
                'risk_score': prediction_result['risk_score'],
                'recommendations': prediction_result['recommendations']
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/history', methods=['GET'])
@jwt_required()
def get_history():
    try:
        user_id = int(get_jwt_identity())
        predictions = AccidentPrediction.query.filter_by(user_id=user_id)\
            .order_by(AccidentPrediction.created_at.desc()).limit(20).all()
        return jsonify({'predictions': [p.to_dict() for p in predictions]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accidents/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    try:
        user_id = int(get_jwt_identity())
        predictions = AccidentPrediction.query.filter_by(user_id=user_id).all()
        
        total = len(predictions)
        high = sum(1 for p in predictions if p.predicted_severity == 'High')
        medium = sum(1 for p in predictions if p.predicted_severity == 'Medium')
        low = sum(1 for p in predictions if p.predicted_severity == 'Low')
        avg_conf = sum(p.confidence_score for p in predictions) / total if total > 0 else 0
        
        return jsonify({
            'total_predictions': total,
            'high_risk_count': high,
            'medium_risk_count': medium,
            'low_risk_count': low,
            'average_confidence': round(avg_conf, 2),
            'severity_distribution': {'Low': low, 'Medium': medium, 'High': high}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚗 Road Accident Prediction System")
    print("="*60)
    print(f"📍 Backend Server: http://localhost:5000")
    print(f"📡 API Health: http://localhost:5000/api/health")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)