from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

salt = b'$2b$12$kMrFpw/lCi2nNc82fY/qqO'

client = MongoClient("mongodb://db:27017")
db = client.SentenceDB
users = db['users']

def check_data(data, func):
    if func == 'register' or func == 'get':
        if not data['username'] or not data['password']:
            return {'status': 301, 'message': 'Missing parameters'}
        return {'status': 200}
    
    if func == 'store':
        if not data['username'] or not data['password'] or not data['sentence']:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}

    if func == 'delete':
        if not data['username']:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}


def verify_passw(username, password):
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)
    
    if not db.users.find_one({'username': username, 'password': hashed}):
        return False
    
    return True


def check_tokens(username):
    tokens = db.users.find_one({'username': username}, {'tokens': 1, '_id': 0})['tokens']
    
    if tokens > 0:
        return True
    
    return False


class Register(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'register')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']

        hashed = bcrypt.hashpw(password.encode('utf8'), salt)

        users.insert_one({
            'username': username,
            'password': hashed,
            'sentence': '',
            'tokens': 6
        })

        return {'status': 200, 'message': 'Registered successfully.'}

class User(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'delete')

        if status['status'] != 200:
            return status
        
        username = data['username']

        users.delete_many({'username': username})

        return {'status': 200}


class Store(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'store')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']
        sentence = data['sentence']

        correct_passw = verify_passw(username, password)

        if not correct_passw:
            return {'status': 302, 'message': correct_passw}

        token_status = check_tokens(username)

        if not token_status:
            return {'status': 301}
        
        users.update_one({'username': username}, {'$set': {'sentence': sentence}})

        tokens = users.find_one({'username': username})['tokens']
        users.update_one({'username': username}, {'$set': {'tokens': tokens-1}})

        return {'status': 200, 'message': 'Sentence saved succesfully.'}

class Get(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'get')

        if status['status'] != 200:
            return status

        username = data['username']
        password = data['password']

        correct_passw = verify_passw(username, password)

        if not correct_passw:
            return {'status': 302}
        
        token_status = check_tokens(username)

        if not token_status:
            return {'status': 301}

        sentence = users.find_one({'username': username})['sentence']

        tokens = users.find_one({'username': username})['tokens']
        users.update_one({'username': username}, {'$set': {'tokens': tokens-1}})

        return {'status': 200, 'sentence': sentence}

    
api.add_resource(Register, "/register")
api.add_resource(User, "/delete")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)