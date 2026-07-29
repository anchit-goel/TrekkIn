import csv
import os
from datetime import datetime
from celery_app import celery
from app import create_app
from app.models import Booking, User
from app.tasks.email_utils import send_email
from flask import current_app


@celery.task(name='app.tasks.csv_export.export_booking_history')
def export_booking_history(user_id):
    app = create_app()
    with app.app_context():
        os.makedirs(current_app.config['EXPORT_DIR'], exist_ok=True)

        user = User.query.get(user_id)
        bookings = Booking.query.filter_by(user_id=user_id).all()

        filename = f"booking_history_{user_id}_{int(datetime.utcnow().timestamp())}.csv"
        filepath = os.path.join(current_app.config['EXPORT_DIR'], filename)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['User ID', 'Trek Name', 'Location', 'Booking Status', 'Booking Date'])
            for b in bookings:
                writer.writerow([user_id, b.trek.name, b.trek.location, b.status, b.booking_date.isoformat()])

        send_email(
            user.email,
            "Your Trekking History Export is Ready",
            f"<p>Hi {user.name},</p><p>Your booking history CSV export has been generated.</p>"
        )

        return filename