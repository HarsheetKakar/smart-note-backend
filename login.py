import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


class JWT:
    def __init__(self, secret_key, UserTable):
        self.secret_key = secret_key
        self.UserTable = UserTable

    def get_token(self, id, time_delta):
        return jwt.encode({
            'id': id,
            'exp': datetime.datetime.utcnow() + time_delta
        }, self.secret_key).decode('UTF-8')

    def login_required(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                token = request.headers.get('idToken', None)

                if(not token):
                    return jsonify({'error': 'Login required',
                                    'solution': 'Login and pass id token as header idToken'}), 401

                data = jwt.decode(token, self.secret_key)
                user_id = data['id']
                current_user = None
                if(user_id):
                    current_user = self.UserTable.query.filter_by(
                        id=user_id).first()

                return func(*args, current_user=current_user, **kwargs)
            except ExpiredSignatureError as e:
                print(e)
                return jsonify({'error': 'signature expired'}), 401
            except InvalidTokenError as e:
                print(e)
                return jsonify({'error': 'invalid token'}), 401

        return decorated

    def super_admin_required(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                token = request.headers.get('idToken', None)

                if(not token):
                    return jsonify({'error': 'Login required',
                                    'solution': 'Login and pass id token as header idToken'}), 401

                data = jwt.decode(token, self.secret_key)
                user_id = data['id']
                current_user = None
                if(user_id):
                    current_user = self.UserTable.query.filter_by(
                        id=user_id).first()

                if(not current_user.super_admin):
                    return jsonify({'error': 'super admin required'}), 401

                return func(*args, current_user=current_user, **kwargs)
            except ExpiredSignatureError as e:
                print(e)
                return jsonify({'error': 'signature expired'}), 401
            except InvalidTokenError as e:
                print(e)
                return jsonify({'error': 'invalid token'}), 401
        return decorated
