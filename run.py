from flask import Flask, request, jsonify, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '94546b6495b0b52c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=True)

    def __str__(self):
        return f'user: {self.username}'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'my_token' in request.headers:
            token = request.headers['my_token']

        if not token:
            return jsonify({'message': 'Token is required'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = UserModel.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'Token is invalid'})
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/', methods=['GET'])
def all_user():
    users = UserModel.query.all()
    lst = []
    for u in users:
        dct = {'name': u.username, 'description': u.description}
        lst.append(dct)
    return jsonify({'users': lst})
    # return jsonify({'message': 'hello world'})


@app.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = UserModel(username=data['username'], password=data['password'], description=data['description'])
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'massage': 'user has been created successfully'})

    except:
        return jsonify({'massage': 'there is an error in creating user'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = UserModel.query.filter_by(username=data['username']).first()
    if user.password == data['password']:
        token = jwt.encode({'username': data['username'], 'password': data['password']}, app.config['SECRET_KEY'],
                           algorithm='HS256')
        return jsonify({'massage': 'login successfully',
                        'token': token.decode('utf-8')
                        })
    return jsonify({'message': 'there is an error for login'})


@app.route('/profile', methods=['GET'])
@token_required
def get_user(current_user):
    # user = UserModel.query.filter_by(username=username).first()
    user = current_user
    if user:
        return jsonify({'username': user.username,
                        'password': user.password,
                        'description': user.description})
    return jsonify({'message': 'user not found'})


@app.route('/modify', methods=['POST'])
@token_required
def modify(current_user):
    data = request.get_json()
    # user = UserModel.query.filter_by(username=username).first()
    user = current_user
    if not user:
        return jsonify({'message': 'user not found'})
    user.description = data['description']
    db.session.commit()
    return jsonify({'message': 'user has been modified'})
    # return redirect(url_for('all_user'))


@app.route('/delete', methods=['DELETE'])
@token_required
def delete(current_user):
    # user = UserModel.query.filter_by(username=username).first()
    user = current_user
    if not user:
        return jsonify({'message': 'not found'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'user has been deleted'})
    # return redirect(url_for('all_user'))


if __name__ == '__main__':
    app.run(debug=True)
