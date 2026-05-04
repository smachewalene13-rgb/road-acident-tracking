from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.accident import AccidentPrediction

accident_bp = Blueprint('accident', __name__)

@accident_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    try:
        user_id = get_jwt_identity()
        predictions = AccidentPrediction.query.filter_by(user_id=user_id).all()
        
        total = len(predictions)
        high_risk = sum(1 for p in predictions if p.predicted_severity == 'High')
        medium_risk = sum(1 for p in predictions if p.predicted_severity == 'Medium')
        low_risk = sum(1 for p in predictions if p.predicted_severity == 'Low')
        
        avg_confidence = sum(p.confidence_score for p in predictions) / total if total > 0 else 0
        
        return jsonify({
            'total_predictions': total,
            'high_risk_count': high_risk,
            'medium_risk_count': medium_risk,
            'low_risk_count': low_risk,
            'average_confidence': round(avg_confidence, 2),
            'severity_distribution': {
                'Low': low_risk,
                'Medium': medium_risk,
                'High': high_risk
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500