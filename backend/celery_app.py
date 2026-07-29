from celery import Celery
from celery.schedules import crontab
from config import Config

celery = Celery(
    'trekking_tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=[
        'app.tasks.reminders',
        'app.tasks.reports',
        'app.tasks.csv_export',
    ]
)

celery.conf.timezone = 'Asia/Kolkata'

celery.conf.beat_schedule = {
    'daily-trek-reminders': {
        'task': 'app.tasks.reminders.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-activity-report': {
        'task': 'app.tasks.reports.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),
    },
}