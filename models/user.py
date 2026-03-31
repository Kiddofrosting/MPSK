from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId


def _db():
    from db import get_db
    return get_db()


class User(UserMixin):
    def __init__(self, data):
        self.id            = str(data['_id'])
        self.username      = data['username']
        self.email         = data['email']
        self.password_hash = data['password_hash']
        self.role          = data.get('role', 'admin')
        self.full_name     = data.get('full_name', '')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(user_id):
        try:
            data = _db().users.find_one({'_id': ObjectId(user_id)})
            return User(data) if data else None
        except Exception:
            return None

    @staticmethod
    def get_by_username(username):
        try:
            data = _db().users.find_one({'username': username})
            return User(data) if data else None
        except Exception:
            return None

    @staticmethod
    def create(username, email, password, full_name='', role='admin'):
        result = _db().users.insert_one({
            'username':      username,
            'email':         email,
            'password_hash': generate_password_hash(password),
            'full_name':     full_name,
            'role':          role,
        })
        return str(result.inserted_id)
