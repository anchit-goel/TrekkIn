from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.auth import role_required
from app.models import Trek, Booking

staff_bp = Blueprint('staff', __name__, url_prefix='/api/staff')


def get_current_staff_id():
    return int(get_jwt_identity())


@staff_bp.route('/dashboard', methods=['GET'])
@role_required('staff')
def staff_dashboard():
    staff_id = get_current_staff_id()
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()

    total_treks = len(treks)
    total_trekkers = sum(
        Booking.query.filter_by(trek_id=t.id, status='Booked').count() for t in treks
    )
    ongoing = sum(1 for t in treks if t.status == 'Ongoing')

    return jsonify({
        'total_treks': total_treks,
        'total_trekkers': total_trekkers,
        'ongoing_treks': ongoing
    }), 200


@staff_bp.route('/treks', methods=['GET'])
@role_required('staff')
def my_treks():
    staff_id = get_current_staff_id()
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()

    result = []
    for t in treks:
        registered = Booking.query.filter_by(trek_id=t.id, status='Booked').count()
        result.append({
            'id': t.id,
            'name': t.name,
            'location': t.location,
            'difficulty': t.difficulty,
            'duration_days': t.duration_days,
            'total_slots': t.total_slots,
            'available_slots': t.available_slots,
            'registered': registered,
            'status': t.status
        })

    return jsonify(result), 200


def _get_own_trek_or_none(trek_id, staff_id):
    trek = Trek.query.get(trek_id)
    if not trek or trek.assigned_staff_id != staff_id:
        return None
    return trek


@staff_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@role_required('staff')
def update_my_trek(trek_id):
    staff_id = get_current_staff_id()
    trek = _get_own_trek_or_none(trek_id, staff_id)
    if not trek:
        return jsonify({'error': 'Trek not found or not assigned to you'}), 403

    data = request.get_json()

    if 'available_slots' in data:
        new_slots = data['available_slots']
        if new_slots < 0 or new_slots > trek.total_slots:
            return jsonify({'error': 'available_slots must be between 0 and total_slots'}), 400
        trek.available_slots = new_slots

    if 'status' in data:
        allowed = ['Pending', 'Approved', 'Open', 'Ongoing', 'Closed', 'Completed']
        if data['status'] not in allowed:
            return jsonify({'error': f'status must be one of {allowed}'}), 400
        trek.status = data['status']

    db.session.commit()
    return jsonify({'message': 'Trek updated'}), 200


@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@role_required('staff')
def trek_participants(trek_id):
    staff_id = get_current_staff_id()
    trek = _get_own_trek_or_none(trek_id, staff_id)
    if not trek:
        return jsonify({'error': 'Trek not found or not assigned to you'}), 403

    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return jsonify([{
        'booking_id': b.id,
        'user_id': b.user.id,
        'name': b.user.name,
        'email': b.user.email,
        'status': b.status,
        'booking_date': b.booking_date.isoformat()
    } for b in bookings]), 200


@staff_bp.route('/bookings/<int:booking_id>', methods=['PUT'])
@role_required('staff')
def update_booking_status(booking_id):
    staff_id = get_current_staff_id()
    booking = Booking.query.get_or_404(booking_id)
    trek = _get_own_trek_or_none(booking.trek_id, staff_id)
    if not trek:
        return jsonify({'error': 'Not authorized for this booking'}), 403

    data = request.get_json()
    new_status = data.get('status')
    allowed = ['Booked', 'Cancelled', 'Completed']
    if new_status not in allowed:
        return jsonify({'error': f'status must be one of {allowed}'}), 400

    # if cancelling, free up a slot
    if booking.status == 'Booked' and new_status == 'Cancelled':
        trek.available_slots = min(trek.total_slots, trek.available_slots + 1)

    booking.status = new_status
    db.session.commit()
    return jsonify({'message': 'Booking updated'}), 200