from app import db

class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))

    def __repr__(self):
        return f'<StaffProfile user={self.user_id}>'
    
    
    
    