from flask import Blueprint, request, jsonify, session
from models import User
from BACKEND.db import db


bp = Blueprint('auth', __name__)  # FIXED _name_ -> __name__

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    email = email.lower().strip()

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    password = data.get('password')
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    user = User(
        name=data.get('name'),
        email=email,
        role=data.get('role'),
        organization=data.get('organization')
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role})

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    email = email.lower().strip()

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user.id
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role
    })

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})
