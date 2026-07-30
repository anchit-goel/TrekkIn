from flask import Blueprint, request, jsonify
from app import db
from app.auth import role_required
from app.models import User, Trek, Booking, StaffProfile
from datetime import datetime
from app.cache.redis_client import cache_get, cache_set, cache_delete

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ---------- Dashboard Stats ----------
@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard_stats():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()

    return jsonify({
        'total_treks': total_treks,
        'total_users': total_users,
        'total_staff': total_staff,
        'total_bookings': total_bookings
    }), 200


# ---------- Trek CRUD ----------


@admin_bp.route('/treks', methods=['GET'])
@role_required('admin')
def list_treks():
    cached = cache_get('admin_all_treks')
    if cached is not None:
        return jsonify(cached), 200

    treks = Trek.query.all()
    result = [{
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'difficulty': t.difficulty,
        'duration_days': t.duration_days,
        'total_slots': t.total_slots,
        'available_slots': t.available_slots,
        'assigned_staff_id': t.assigned_staff_id,
        'assigned_staff_name': t.assigned_staff.name if t.assigned_staff else None,
        'status': t.status,
        'start_date': t.start_date.isoformat() if t.start_date else None,
        'end_date': t.end_date.isoformat() if t.end_date else None
    } for t in treks]

    cache_set('admin_all_treks', result, ttl_seconds=30)
    return jsonify(result), 200


@admin_bp.route('/treks', methods=['POST'])
@role_required('admin')
def create_trek():
    data = request.get_json()
    required = ['name', 'location', 'difficulty', 'duration_days', 'total_slots']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    trek = Trek(
        name=data['name'],
        location=data['location'],
        difficulty=data['difficulty'],
        duration_days=data['duration_days'],
        total_slots=data['total_slots'],
        available_slots=data['total_slots'],
        status=data.get('status', 'Pending')
    )
    if data.get('start_date'):
        trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if data.get('end_date'):
        trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    db.session.add(trek)
    db.session.commit()
    return jsonify({'message': 'Trek created', 'id': trek.id}), 201


@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@role_required('admin')
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()

    for field in ['name', 'location', 'difficulty', 'duration_days', 'status']:
        if field in data:
            setattr(trek, field, data[field])

    if 'start_date' in data and data['start_date']:
        trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data and data['end_date']:
        trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    if 'total_slots' in data:
        diff = data['total_slots'] - trek.total_slots
        trek.total_slots = data['total_slots']
        trek.available_slots = max(0, trek.available_slots + diff)

    db.session.commit()
    return jsonify({'message': 'Trek updated'}), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@role_required('admin')
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    return jsonify({'message': 'Trek deleted'}), 200


@admin_bp.route('/treks/<int:trek_id>/assign', methods=['PUT'])
@role_required('admin')
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()
    staff_id = data.get('staff_id')

    if staff_id is None:
        trek.assigned_staff_id = None
        db.session.commit()
        return jsonify({'message': 'Staff unassigned'}), 200

    staff = User.query.filter_by(id=staff_id, role='staff').first()
    if not staff:
        return jsonify({'error': 'Invalid staff ID'}), 400

    trek.assigned_staff_id = staff.id
    db.session.commit()
    return jsonify({'message': f'Staff {staff.name} assigned to trek {trek.name}'}), 200


# ---------- Staff Management ----------
@admin_bp.route('/staff', methods=['GET'])
@role_required('admin')
def list_staff():
    staff_members = User.query.filter_by(role='staff').all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'email': s.email,
        'active': s.active,
        'contact_number': s.staff_profile.contact_number if s.staff_profile else None
    } for s in staff_members]), 200


@admin_bp.route('/staff', methods=['POST'])
@role_required('admin')
def create_staff():
    data = request.get_json()
    required = ['name', 'email', 'password']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    email = data['email'].strip().lower()

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    staff = User(name=data['name'], email=email, role='staff', active=True)
    staff.set_password(data['password'])
    db.session.add(staff)
    db.session.commit()

    profile = StaffProfile(user_id=staff.id, contact_number=data.get('contact_number', ''))
    db.session.add(profile)
    db.session.commit()

    return jsonify({'message': 'Staff created', 'id': staff.id}), 201


# ---------- Users & Staff: view / search / deactivate ----------
@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def list_users():
    users = User.query.filter_by(role='trekker').all()
    return jsonify([{
        'id': u.id, 'name': u.name, 'email': u.email, 'active': u.active
    } for u in users]), 200


@admin_bp.route('/search', methods=['GET'])
@role_required('admin')
def search():
    q = request.args.get('q', '')
    treks = Trek.query.filter(Trek.name.ilike(f'%{q}%')).all()
    users = User.query.filter(User.name.ilike(f'%{q}%')).all()

    return jsonify({
        'treks': [{'id': t.id, 'name': t.name} for t in treks],
        'users': [{'id': u.id, 'name': u.name, 'role': u.role} for u in users]
    }), 200


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['PUT'])
@role_required('admin')
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({'error': 'Cannot deactivate admin'}), 400
    user.active = not user.active
    db.session.commit()
    return jsonify({'message': f'User {"activated" if user.active else "deactivated"}'}), 200


# ---------- Bookings overview ----------
@admin_bp.route('/bookings', methods=['GET'])
@role_required('admin')
def all_bookings():
    bookings = Booking.query.all()
    return jsonify([{
        'id': b.id,
        'user_name': b.user.name,
        'trek_name': b.trek.name,
        'status': b.status,
        'booking_date': b.booking_date.isoformat(),
        'payment_status': b.payment_status
    } for b in bookings]), 200