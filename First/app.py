from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/hi')
def hi():
    return {"field1": "Hi", "field2": "Flask user"}

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    return str(data['x']+data['y'])

if __name__ == "__main__":
    #app.run() default port is 5000
    app.run(degub=True, host="127.0.0.1", port=80)