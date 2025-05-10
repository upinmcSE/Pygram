from flask import jsonify


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