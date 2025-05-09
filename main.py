import os
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended import JWTManager



# Khởi tạo ứng dụng Flask và thiết lập secret key cho JWT (sẽ dùng sau)
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
jwt = JWTManager(app)

# Lưu trữ người dùng trong bộ nhớ (chỉ dành cho mục đích phát triển)
users = {}  # { username: { password: hashed_password, profile: {...} } }

# Decorator để kiểm tra JWT và xác thực người dùng
def token_required(f):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Kiểm tra xem có JWT token hợp lệ trong request không
            verify_jwt_in_request()
            # Lấy username (identity) từ JWT token
            username = get_jwt_identity()
            # Lấy thông tin người dùng từ bộ nhớ (trong ứng dụng thực tế sẽ là database)
            current_user = users.get(username)

            # Kiểm tra xem người dùng có tồn tại không
            if not current_user:
                return api_response(message="User does not exist", status=404)

            # Gọi hàm endpoint ban đầu, truyền thông tin người dùng đã xác thực vào
            return fn(current_user, *args, **kwargs)
        except Exception as e:
            # Nếu có lỗi trong quá trình xác thực token (ví dụ: token hết hạn, không hợp lệ)
            return api_response(message=f"Token is invalid: {str(e)}", status=401)
    return wrapper


# Hàm xử lý đăng ký tài khoản
@app.route('/register', methods=['POST'])
def register():
    """UC01: Đăng ký một tài khoản người dùng mới."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    email = data.get('email')

    # Kiểm tra username, password và email
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

    # Mã hóa mật khẩu trước khi lưu trữ
    pw_hash = generate_password_hash(password)
    # Thông tin hồ sơ người dùng cơ bản
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

# Hàm tiện ích để tạo JSON response chuẩn cho API
def api_response(data=None, message=None, status=200):
    """Hàm tiện ích để tạo JSON response chuẩn cho API."""
    response = {
        'success': 200 <= status < 300,
        'status': status
    }

    if message:
        response['message'] = message
    

    if data is not None:
        response['data'] = data

    return jsonify(response), status


# Hàm xử lý đăng nhập
@app.route('/login', methods=['POST'])
def login():
    """UC02: Đăng nhập vào một tài khoản người dùng đã tồn tại."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    # Kiểm tra xem tên đăng nhập có tồn tại trong hệ thống hay không
    if username not in users:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Kiểm tra mật khẩu đã nhập có khớp với mật khẩu đã mã hóa hay không
    if not check_password_hash(users[username]['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Nếu tên đăng nhập và mật khẩu đều đúng, tạo access token và refresh token
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    # Trả về response thành công kèm theo token và thông tin người dùng
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
def get_profile():
    """UC04: Lấy thông tin hồ sơ của người dùng hiện tại."""
    return api_response(data=current_user['profile'])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))