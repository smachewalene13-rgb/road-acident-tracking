# backend/app/models/accident.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AccidentPrediction(db.Model):
    __tablename__ = 'accident_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Input features
    weather = db.Column(db.String(50))
    road_condition = db.Column(db.String(50))
    speed_limit = db.Column(db.Integer)
    traffic_density = db.Column(db.String(50))
    alcohol_involved = db.Column(db.Boolean, default=False)
    speeding = db.Column(db.Boolean, default=False)
    
    # Prediction results
    predicted_severity = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'weather': self.weather,
            'road_condition': self.road_condition,
            'speed_limit': self.speed_limit,
            'predicted_severity': self.predicted_severity,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }