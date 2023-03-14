from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

salt = b'$2b$12$kMrFpw/lCi2nNc82fY/qqO'
bank = 'Demo Bank'

client = MongoClient('mongodb://db:27017')
db = client.BankAPI
users = db['users']

if not db.users.find_one({'username': bank}):
    hashed = bcrypt.hashpw('pass123'.encode('utf8'), salt)
    db.users.insert_one({
        'username': bank,
        'password': hashed,
        'balance': 0,
        'debt': 0
    })

def check_data(data, func):
    if func == 'register' or func == 'balance':
        if 'username' not in data or 'password' not in data:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}
    
    if func == 'deposit' or func == 'loan' or func == 'pay':
        if 'username' not in data or 'password' not in data or 'amount' not in data:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}
    
    if func == 'transfer':
        if 'username' not in data or 'password' not in data or 'receiver' not in data or 'amount' not in data:
            return {'status': 301, 'message': 'Missing parameters.'}
        return {'status': 200}

def check_user(username):
    if db.users.find_one({'username': username}):
        return {'status': 200, 'message': "User already exists."}
    return {'status': 304, 'message': "User does not exists."}

def check_passw(username, password):
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)
    
    if not db.users.find_one({'username': username, 'password': hashed}):
        return {'status': 304, 'message': 'Invalid password.'}
    return {'status': 200, 'message': 'Authentication success.'}

def get_balance(username):
    balance = db.users.find_one({'username': username}, {'balance': 1, '_id': 0})
    if balance:
        return {'status': 200, 'balance': balance['balance']}
    return {'status': 305, 'message': 'User does not exists.'}

def get_debt(username):
    debt = db.users.find_one({'username': username}, {'debt': 1, '_id': 0})
    if debt:
        return {'status': 200, 'debt': debt['debt']}
    return {'status': 305, 'message': 'User does not exists.'}

def update_balanace(username, balance):
    db.users.update_one({'username': username}, {'$set': {'balance': balance}})

def update_debt(username, debt):
    db.users.update_one({'username': username}, {'$set': {'debt': debt}})

class Register(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'register')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']

        status = check_user(username)

        if status['status'] == 200:
            return status

        hashed = bcrypt.hashpw(password.encode('utf8'), salt)

        users.insert_one({
            'username': username,
            'password': hashed,
            'balance': 0,
            'debt': 0
        })

        return {'status': 200, 'message': 'Registered successfully.'}

class Deposit(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'deposit')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']
        amount = data['amount']

        if amount <= 0:
            return {'status': 307, 'message': 'Invalid amount is provided.'}

        status = check_user(username)

        if status['status'] != 200:
            return status

        status = check_passw(username, password)
        
        if status['status'] != 200:
            return status
        
        balance_user = get_balance(username)['balance']
        balance_bank = get_balance(bank)['balance']
        update_balanace(username, balance_user+amount-1)
        update_balanace(bank, balance_bank+1)

        return {'status': 200, 'message': 'Deposit successfully executed.'}

class Transfer(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'transfer')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']
        receiver = data['receiver']
        amount = data['amount']

        if amount <= 0:
            return {'status': 307, 'message': 'Invalid amount is provided.'}

        status = check_user(username)

        if status['status'] != 200:
            return status

        status = check_passw(username, password)
        
        if status['status'] != 200:
            return status
        
        balance_sender = get_balance(username)['balance']
        balance_bank = get_balance(bank)['balance']

        balance_receiver = get_balance(receiver)
        if balance_receiver['status'] != 200:
            return balance_receiver
        balance_receiver = balance_receiver['balance']
        
        if balance_sender < amount:
            return {'status': 308, 'message': 'Insufficient amount of money in balance.'}
        
        update_balanace(username, balance_sender-amount)
        update_balanace(receiver, balance_receiver+amount-1)
        update_balanace(bank, balance_bank+1)

        return {'status': 200, 'message': 'Transfer completed successfully.'}
    
class Balance(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'balance')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']
        
        status = check_user(username)

        if status['status'] != 200:
            return status

        status = check_passw(username, password)
        
        if status['status'] != 200:
            return status
        
        balance = get_balance(username)['balance']
        debt = get_debt(username)['debt']
        
        return {'status': 200, 'balance': balance, 'debt': debt}

class Loan(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'loan')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']
        amount = data['amount']

        if amount <= 0:
            return {'status': 307, 'message': 'Invalid amount is provided.'}

        status = check_user(username)

        if status['status'] != 200:
            return status

        status = check_passw(username, password)
        
        if status['status'] != 200:
            return status
        
        balance = get_balance(username)['balance']
        debt = get_debt(username)['debt']
        update_balanace(username, balance+amount)
        update_debt(username, debt+amount)

        return {'status': 200, 'message': 'Load taken successfully.'}

class Pay(Resource):
    def post(self):
        data = request.get_json()

        status = check_data(data, 'pay')

        if status['status'] != 200:
            return status
        
        username = data['username']
        password = data['password']
        amount = data['amount']

        if amount <= 0:
            return {'status': 307, 'message': 'Invalid amount is provided.'}

        status = check_user(username)

        if status['status'] != 200:
            return status

        status = check_passw(username, password)
        
        if status['status'] != 200:
            return status
        
        balance = get_balance(username)['balance']
        debt = get_debt(username)['debt']

        if debt < amount:
            return {'status': 309, 'message': 'Invalid amount provided.'}
        
        if balance < amount:
            return {'status': 309, 'message': 'Invalid amount provided.'}
        
        update_balanace(username, balance-amount)
        update_debt(username, debt-amount)

        return {'status': 200, 'message': 'Load payed successfully.'}
    
api.add_resource(Register, "/register")
api.add_resource(Deposit, "/deposit")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(Loan, "/loan")
api.add_resource(Pay, "/pay")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)