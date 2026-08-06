from datetime import datetime
from sqlalchemy import func
from celery_app import celery
from app import create_app, db
from app.models import Trek, Booking
from app.tasks.email_utils import send_email
from flask import current_app


@celery.task(name='app.tasks.reports.send_monthly_report')
def send_monthly_report():
    app = create_app()
    with app.app_context():
        total_treks = Trek.query.count()
        total_participants = db.session.query(func.count(func.distinct(Booking.user_id))).filter(Booking.status == 'Completed').scalar()

        popular = (
            db.session.query(Trek.name, func.count(Booking.id).label('cnt'))
            .join(Booking, Booking.trek_id == Trek.id)
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
            .all()
        )
        popular_html = "".join(f"<li>{name}: {cnt} bookings</li>" for name, cnt in popular) or "<li>No bookings yet</li>"

        body = f"""
        <h2>Monthly Trekking Activity Report - {datetime.now().strftime('%B %Y')}</h2>
        <p>Total treks in system: {total_treks}</p>
        <p>Total completed participations: {total_participants}</p>
        <h3>Top Treks</h3>
        <ul>{popular_html}</ul>
        """

        send_email(current_app.config['ADMIN_NOTIFY_EMAIL'], "Monthly Trekking Activity Report", body)
        return "Monthly report sent"