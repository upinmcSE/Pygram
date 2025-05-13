from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.models.user import User


def api_response(data=None, message=None, status=200):
    response = {
        'success': 200 <= status < 300,
        'status': status
    }

    if message:
        response['message'] = message
    

    if data is not None:
        response['data'] = data

    return jsonify(response), status


# middleware để kiểm tra token
def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            current_user = User.query.get(user_id)
            
            if not current_user:
                return api_response(message="User does not exist", status=404)
                
            return fn(current_user, *args, **kwargs)
        except Exception as e:
            return api_response(message=f"Token is invalid: {str(e)}", status=401)
    return wrapper