import os
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended import JWTManager
from werkzeug.security import check_password_hash
from utils import api_response



app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
jwt = JWTManager(app)

# Lưu trữ người dùng trong bộ nhớ
users = {} 

# middleware để kiểm tra token
def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            username = get_jwt_identity()
            current_user = users.get(username)

            if not current_user:
                return api_response(message="User does not exist", status=404)

            return fn(current_user, *args, **kwargs)
        except Exception as e:
            return api_response(message=f"Token is invalid: {str(e)}", status=401)
    return wrapper


@app.route('/register', methods=['POST'])
def register():
    """UC01: Đăng ký một tài khoản người dùng mới."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    email = data.get('email')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    if not full_name:
        return jsonify({'error': 'Missing full name'}), 400

    pw_hash = generate_password_hash(password)

    profile = {
        'username': username,
        'email': email,
        'full_name': full_name,
        'profile_picture': 'default.png',
        'bio': '',
        'created_at': int(datetime.now().timestamp())
    }

    users[username] = {'password': pw_hash, 'profile': profile}
    return api_response(data=profile, message='User registered successfully')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if username not in users:
        return jsonify({'error': 'Invalid username or password'}), 401

    if not check_password_hash(users[username]['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    return api_response(
        message='Login successful',
        data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            "user": users[username]['profile'],
        })

@app.route("/logout", methods=["POST"])
def logout():
    return api_response(message="Logout successful")


@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return api_response(data=current_user['profile'])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))