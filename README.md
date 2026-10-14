# TrekkIn - Trekking Management Platform

TrekkIn is a full-stack web application designed for adventure organizations, tour operators, and outdoor communities to streamline expedition scheduling, participant registrations, and staff operations.

## About

Adventure organizations require efficient systems to manage trekking activities involving trek organizers, staff, and participants. Currently, many trekking groups rely on spreadsheets, calls, or manual coordination, which makes it difficult to manage trek approvals, participant registrations, slot availability, and booking tracking.

TrekkIn solves this by giving Admins, Trek Staff, and Trekkers dedicated, role-based dashboards to manage the entire trekking lifecycle from trek creation and staff assignment, to booking, participant tracking, and post-trek reporting.

## Roles

- **Admin** — pre-seeded, single account. Manages treks, staff, users, and views all bookings and statistics.
- **Trek Staff** — created only by Admin. Manages assigned treks, updates slots/status, and tracks participants.
- **Trekker** — self-registers. Browses open treks, books/cancels, and tracks personal booking history.

## Technical Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS
- **Frontend:** Vue 3 (Vite), Bootstrap 5
- **Database:** SQLite
- **Caching:** Redis
- **Background Jobs:** Celery + Redis (daily reminders, monthly reports, async CSV export)

## Core Features

- JWT-based authentication with role-based access control
- Admin dashboard: trek/staff/user CRUD, search, deactivation, booking overview
- Staff dashboard: assigned-trek management, slot/status updates, participant tracking
- Trekker dashboard: trek browsing/search/filter, booking, cancellation, history, profile
- Overbooking and duplicate-booking prevention; booking allowed only on Open, non-expired treks
- Daily trek reminder emails and monthly admin activity reports via Celery Beat
- User-triggered async CSV export of booking history, with email notification
- Redis-backed caching on frequently accessed endpoints, with write-path invalidation

## Setup

### Prerequisites
- Python 3.x, Node.js, Redis

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your own values
python seed.py
python run.py
```

### Background Jobs (separate terminals, backend/ with venv active)
```bash
celery -A celery_app.celery worker --loglevel=info --pool=solo
celery -A celery_app.celery beat --loglevel=info
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Author

Anchit Goel ([@anchit-goel](https://github.com/anchit-goel))

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.