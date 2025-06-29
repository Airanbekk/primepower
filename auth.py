from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime
from models import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user = User(username=data['username'], password=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    token = jwt.encode(
        {'user': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        current_app.config['SECRET_KEY'], algorithm='HS256'
    )
    return jsonify({'token': token})

@auth_bp.route('/profile', methods=['GET'])
def profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'user': data['user']})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
