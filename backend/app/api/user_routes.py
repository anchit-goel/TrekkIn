from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.auth import role_required
from app.models import Trek, Booking, User
from app.cache.redis_client import cache_get, cache_set, cache_delete
from datetime import date

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


def get_current_user_id():
    return int(get_jwt_identity())


@user_bp.route('/treks', methods=['GET'])
@role_required('trekker')
def browse_treks():
    cached = cache_get('open_treks')
    if cached is not None:
        return jsonify(cached), 200

    treks = Trek.query.filter_by(status='Open').all()
    today = date.today()
    result = [{
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'difficulty': t.difficulty,
        'duration_days': t.duration_days,
        'available_slots': t.available_slots
    } for t in treks if not (t.end_date and t.end_date < today)]

    cache_set('open_treks', result, ttl_seconds=30)
    return jsonify(result), 200


@user_bp.route('/bookings', methods=['POST'])
@role_required('trekker')
def book_trek():
    user_id = get_current_user_id()
    data = request.get_json()
    trek_id = data.get('trek_id')

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.end_date and trek.end_date < date.today():
        return jsonify({'error': 'This trek has ended and can no longer be booked'}), 400

    if trek.status != 'Open':
        return jsonify({'error': 'Trek is not open for booking'}), 400

    if trek.available_slots <= 0:
        return jsonify({'error': 'No slots available'}), 400

    existing = Booking.query.filter_by(user_id=user_id, trek_id=trek_id, status='Booked').first()
    if existing:
        return jsonify({'error': 'You already have an active booking for this trek'}), 409

    booking = Booking(user_id=user_id, trek_id=trek_id, status='Booked')
    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()
    cache_delete('open_treks', 'admin_all_treks')
    return jsonify({'message': 'Trek booked successfully', 'booking_id': booking.id}), 201


@user_bp.route('/bookings', methods=['GET'])
@role_required('trekker')
def my_bookings():
    user_id = get_current_user_id()
    bookings = Booking.query.filter_by(user_id=user_id).all()

    return jsonify([{
        'id': b.id,
        'trek_id': b.trek.id,
        'trek_name': b.trek.name,
        'location': b.trek.location,
        'status': b.status,
        'booking_date': b.booking_date.isoformat(),
        'payment_status': b.payment_status
    } for b in bookings]), 200


@user_bp.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
@role_required('trekker')
def cancel_booking(booking_id):
    user_id = get_current_user_id()
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403

    if booking.status != 'Booked':
        return jsonify({'error': 'Only active bookings can be cancelled'}), 400

    booking.status = 'Cancelled'
    booking.trek.available_slots = min(booking.trek.total_slots, booking.trek.available_slots + 1)

    db.session.commit()
    cache_delete('open_treks', 'admin_all_treks')
    return jsonify({'message': 'Booking cancelled'}), 200


@user_bp.route('/history', methods=['GET'])
@role_required('trekker')
def trekking_history():
    user_id = get_current_user_id()
    bookings = Booking.query.filter_by(user_id=user_id, status='Completed').all()

    return jsonify([{
        'trek_name': b.trek.name,
        'location': b.trek.location,
        'date': b.booking_date.isoformat(),
        'status': b.status
    } for b in bookings]), 200


@user_bp.route('/profile', methods=['GET'])
@role_required('trekker')
def get_profile():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    return jsonify({'name': user.name, 'email': user.email}), 200


@user_bp.route('/profile', methods=['PUT'])
@role_required('trekker')
def update_profile():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    data = request.get_json()

    if 'name' in data and data['name'].strip():
        user.name = data['name'].strip()

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'name': user.name}), 200

@user_bp.route('/export', methods=['POST'])
@role_required('trekker')
def trigger_export():
    from app.tasks.csv_export import export_booking_history
    user_id = get_current_user_id()
    task = export_booking_history.delay(user_id)
    return jsonify({'task_id': task.id, 'message': 'Export started, you will be emailed when ready'}), 202


@user_bp.route('/export/<task_id>', methods=['GET'])
@role_required('trekker')
def export_status(task_id):
    from celery_app import celery
    result = celery.AsyncResult(task_id)
    if result.state == 'SUCCESS':
        return jsonify({'status': 'done', 'filename': result.result}), 200
    elif result.state == 'FAILURE':
        return jsonify({'status': 'failed', 'error': str(result.result)}), 200
    return jsonify({'status': result.state.lower()}), 200


@user_bp.route('/export/<task_id>/download', methods=['GET'])
@role_required('trekker')
def download_export(task_id):
    from celery_app import celery
    from flask import send_from_directory, current_app
    result = celery.AsyncResult(task_id)
    if result.state != 'SUCCESS':
        return jsonify({'error': 'Export not ready'}), 400
    return send_from_directory(current_app.config['EXPORT_DIR'], result.result, as_attachment=True)