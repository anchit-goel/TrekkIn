from app import db
from datetime import datetime

class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) 
    duration_days = db.Column(db.Integer, nullable=False)

    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    status = db.Column(db.String(20), nullable=False, default='Pending')

    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: lets you do trek.assigned_staff to get the User object directly
    assigned_staff = db.relationship('User', backref='assigned_treks')

    def __repr__(self):
        return f'<Trek {self.name} ({self.status})>'