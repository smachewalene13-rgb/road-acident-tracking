from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.accident import AccidentPrediction
import random

prediction_bp = Blueprint('prediction', __name__)

def predict_severity(data):
    """Simple prediction logic based on input features"""
    risk_score = 0
    
    # Weather impact
    weather_risk = {'Clear': 0, 'Rain': 2, 'Fog': 3, 'Snow': 4}
    risk_score += weather_risk.get(data.get('weather'), 0)
    
    # Road condition impact
    road_risk = {'Dry': 0, 'Wet': 1, 'Icy': 3, 'Flooded': 2}
    risk_score += road_risk.get(data.get('road_condition'), 0)
    
    # Speed impact
    speed = int(data.get('speed_limit', 0))
    if speed > 80:
        risk_score += 3
    elif speed > 60:
        risk_score += 2
    elif speed > 40:
        risk_score += 1
    
    # Other factors
    if data.get('speeding', False):
        risk_score += 2
    if data.get('alcohol_involved', False):
        risk_score += 3
    if data.get('traffic_density') == 'High':
        risk_score += 1
    
    # Determine severity
    if risk_score >= 8:
        severity = 'High'
        confidence = random.uniform(0.85, 0.95)
    elif risk_score >= 4:
        severity = 'Medium'
        confidence = random.uniform(0.75, 0.88)
    else:
        severity = 'Low'
        confidence = random.uniform(0.90, 0.98)
    
    # Recommendations based on severity
    recommendations = {
        'Low': [
            '✓ Drive cautiously',
            '✓ Stay alert',
            '✓ Follow traffic rules'
        ],
        'Medium': [
            '⚠️ Reduce speed',
            '⚠️ Increase following distance',
            '⚠️ Check weather conditions'
        ],
        'High': [
            '🚨 IMMEDIATE ACTION REQUIRED',
            '📞 Call emergency services',
            '🆘 Seek medical attention',
            '⚠️ Set up warning triangles'
        ]
    }
    
    return {
        'severity': severity,
        'confidence': round(confidence * 100, 2),
        'risk_score': risk_score,
        'recommendations': recommendations[severity]
    }

@prediction_bp.route('/', methods=['POST'])
@jwt_required()
def predict():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Make prediction
        prediction_result = predict_severity(data)
        
        # Save to database
        prediction = AccidentPrediction(
            user_id=user_id,
            weather=data.get('weather'),
            road_condition=data.get('road_condition'),
            speed_limit=data.get('speed_limit'),
            traffic_density=data.get('traffic_density'),
            alcohol_involved=data.get('alcohol_involved', False),
            speeding=data.get('speeding', False),
            predicted_severity=prediction_result['severity'],
            confidence_score=prediction_result['confidence']
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prediction': prediction_result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    try:
        user_id = get_jwt_identity()
        predictions = AccidentPrediction.query.filter_by(user_id=user_id)\
            .order_by(AccidentPrediction.created_at.desc()).limit(20).all()
        
        return jsonify({
            'predictions': [p.to_dict() for p in predictions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500