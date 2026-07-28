from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'error': 'Missing fields'}), 400

    email = email.strip().lower()

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(name=name, email=email, role='trekker', active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email:
        email = email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.active:
        return jsonify({'error': 'Account deactivated'}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'name': user.name}
    )

    return jsonify({'access_token': token, 'role': user.role, 'name': user.name}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({'name': user.name, 'role': user.role, 'email': user.email}), 200
