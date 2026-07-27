from app import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Booked')
    
    payment_status = db.Column(db.String(20), nullable = False, default = 'NA')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    user = db.relationship('User', backref='bookings')
    trek = db.relationship('Trek', backref='bookings')

    
    
    def __repr__ (self):
        return f'<Booking user ={self.user_id} trek = {self.trek_id} status = {self.status}>'
    
    
    
    