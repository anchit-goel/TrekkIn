from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()

    existing_admin = User.query.filter_by(role='admin').first()
    if existing_admin:
        print("Admin already exists:", existing_admin.email)
    else:
        admin = User(
            name='Admin',
            email='admin@trekapp.com',
            role='admin',
            active=True
        )
        admin.set_password('admin123')  
        db.session.add(admin)
        db.session.commit()
        print("Admin created:", admin.email)
        
         