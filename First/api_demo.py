from flask import Flask, request
from flask_restful import Api, Resource

# To run the application:
# flask --app api_demo run

# GET: retrieve
# POST: create
# PUT: update
# DELETE: delete source

# Documentation structure
# 1) Resource  
# 2) Method
# 3) Path
# 4) Used For
# 5) Param
# 6) On Error/Status


app = Flask(__name__)
api = Api(app)


def check_data_post(data, function_name):
    if function_name == "add" or function_name == "sub" or function_name == 'mul':
        if 'x' not in data or 'y' not in data:
            return 301
        else:
            return 200
    if function_name == "div":
        if 'x' not in data or 'y' not in data:
            return 301
        elif data['y'] == 0:
            return 302
        else:
            return 200

class Add(Resource):
    def post(self):
        # if I am here, then the resource Add was requested using the method POST
        # same can be implemented for get, put, delete

        data = request.get_json()

        status = check_data_post(data, "add")
        if status != 200:
            return {'message': 'missing parameter', 'status': status}
        
        x, y = int(data['x']), int(data['y'])

        return {'message': x+y, 'status': 200}
    pass

class Subtract(Resource):
    def post(self):
        data = request.get_json()

        status = check_data_post(data, "sub")
        if status != 200:
            return {'message': 'missing parameter', 'status': status}
        
        x, y = int(data['x']), int(data['y'])

        return {'message': x-y, 'status': 200}
    pass

class Multiply(Resource):
    def post(self):
        data = request.get_json()

        status = check_data_post(data, "mul")
        if status != 200:
            return {'message': 'missing parameter', 'status': status}
        
        x, y = int(data['x']), int(data['y'])

        return {'message': x*y, 'status': 200}
    pass

class Divide(Resource):
    def post(self):
        data = request.get_json()

        status = check_data_post(data, "div")
        if status != 200:
            if status == 301:
                return {'message': 'missing parameter', 'status': status}
            elif status == 302:
                return {'message': 'divider cannot be zero', 'status': status}
            else:
                return {'message': 'unhandled error', 'status': status}
        
        x, y = int(data['x']), int(data['y'])

        return {'message': (1.0*x)/y, 'status': 200}
    pass


api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")


if __name__ == "__main__":
    app.run(debug=True)