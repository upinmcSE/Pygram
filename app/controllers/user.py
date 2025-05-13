from flask import Blueprint
from app.utils import api_response, token_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/me', methods=['GET'])
@token_required
def get_profile(current_user):
    return api_response(data=current_user.to_dict())

@user_bp.route('/me', methods=['PUT'])
@token_required
def edit_profile(current_user):
    """UC05: Chỉnh sửa hồ sơ cá nhân (Edit Own Profile)."""
    data = request.get_json() or {}
    allowed_fields = ['fullname', 'email', 'username', 'bio']
    fields_to_update = {k: v for k, v in data.items() if k in allowed_fields and v}

    # If no fields to update, return error
    if not fields_to_update:
        return api_response(message="No fields to update", status=400)

    # Check if username or email already exists
    if 'username' in fields_to_update and fields_to_update['username'] != current_user.username:
        if User.query.filter_by(username=fields_to_update['username']).first():
            return api_response(message="Username already exists", status=400)

    if 'email' in fields_to_update and fields_to_update['email'] != current_user.email:
        if User.query.filter_by(email=fields_to_update['email']).first():
            return api_response(message="Email already exists", status=400)

    # Cập nhật thông tin
    for key, value in fields_to_update.items():
        setattr(current_user, key, value)

    try:
        db.session.commit()
        return api_response(message="Update profile successfully", data=current_user.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error updating profile: {str(e)}", status=500)

@user_bp.route('/<int:user_id>/profile', methods=['GET'])
@token_required
def view_other_profile(current_user, user_id):
    """UC06: Xem hồ sơ người dùng khác (View Other User's Profile)"""
    user = User.query.get(user_id)
    if not user:
        return api_response(message="User not found", status=404)

    return api_response(data=user.to_dict())

