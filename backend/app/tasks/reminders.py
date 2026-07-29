from datetime import date, timedelta
from celery_app import celery
from app import create_app
from app.models import Trek, Booking
from app.tasks.email_utils import send_email


@celery.task(name='app.tasks.reminders.send_daily_reminders')
def send_daily_reminders():
    app = create_app()
    with app.app_context():
        tomorrow = date.today() + timedelta(days=1)
        treks = Trek.query.filter(Trek.start_date == tomorrow).all()

        count = 0
        for trek in treks:
            bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
            for b in bookings:
                subject = f"Reminder: {trek.name} starts tomorrow!"
                body = f"""
                <h3>Hi {b.user.name},</h3>
                <p>Your trek <strong>{trek.name}</strong> in {trek.location} starts tomorrow
                ({trek.start_date}).</p>
                <p>Duration: {trek.duration_days} days &middot; Difficulty: {trek.difficulty}</p>
                <p>Please be ready and reach the starting point on time.</p>
                """
                send_email(b.user.email, subject, body)
                count += 1
        return f"Sent {count} reminder emails"