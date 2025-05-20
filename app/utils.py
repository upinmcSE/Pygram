from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.models.user import User
from google.cloud import storage
import uuid
from datetime import timedelta

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

BUCKET_NAME = "pygram-bucket"
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_gcs(file_obj, destination_folder):
    filename = f"{destination_folder}/{uuid.uuid4().hex}_{file_obj.filename}"
    blob = bucket.blob(filename)
    blob.upload_from_file(file_obj, content_type=file_obj.content_type)
    return blob.public_url

def delete_file_from_gcs(filename, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.delete()

def generate_signed_url(filename, bucket_name, expiration_minutes=15):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )

    return url