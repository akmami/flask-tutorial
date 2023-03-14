from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import clasify

app = Flask(__name__)
api = Api(app)

salt = b'$2b$12$kMrFpw/lCi2nNc82fY/qqO'

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognitionDB
users = db['users']

def check_data(data, func):
    if func == 'register':
        if not data['username'] or not data['password']:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}

    if func == 'clasify':
        if not data['username'] or not data['password'] or not data['url']:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}
    
    if func == 'refill':
        if not data['username'] or not data['admin_token'] or not data['amount']:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}

def check_user(username):
    if db.users.find_one({'username': username}):
        return {'status': 302, 'message': "User already exists."}
    return {'status': 200}

def check_passw(username, password):
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)
    
    if not db.users.find_one({'username': username, 'password': hashed}):
        return {'status': 304, 'message': 'Invalid password.'}
    return {'status': 200}

def check_tokens(username):
    tokens = db.users.find_one({'username': username}, {'tokens': 1, '_id': 0})['tokens']

    if tokens <= 0:
        return {'status': 305, 'message': 'Insufficient tokens.'}
    return {'status': 200, 'tokens': tokens}

class Register(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'register')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']

        status = check_user(username)

        if status['status'] != 200:
            return status

        hashed = bcrypt.hashpw(password.encode('utf8'), salt)

        users.insert_one({
            'username': username,
            'password': hashed,
            'tokens': 6
        })

        return {'status': 200, 'message': 'Registered successfully.'}

class Clasify(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'clasify')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']
        url = data['url']

        status = check_user(username)
        
        if status['status'] == 200:
            return {'status': 303, 'message': 'User does not exists'}

        status = check_passw(username, password)
        
        if status['status'] != 200:
            return status
        
        status = check_tokens(username)
        
        if status['status'] != 200:
            return status
        
        tokens = status['tokens']
        db.users.update_one({'username': username}, {'$set': {'tokens': tokens-1}})

        prediction = clasify.clasify(url)
        return {'status': 200, 'prediction': prediction[0], 'accuracy': prediction[1]}

class Refill(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'refill')

        if status['status'] != 200:
            return status
        
        username = data['username']
        token = data['admin_token']
        amount = data['amount']

        status = check_user(username)
        
        if status['status'] == 200:
            return {'status': 303, 'message': 'User does not exists'}

        if not token == 'admin_token_123':
            return {'status': 301, 'message': 'Invalid admin token.'}
        
        db.users.update_one({'username': username}, {'$set': {'tokens': amount}})

        return {'status': 200, 'message': 'Tokens uploaded successfully.'}
          
api.add_resource(Register, "/register")
api.add_resource(Clasify, "/clasify")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)