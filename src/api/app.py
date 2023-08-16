from flask import Flask, jsonify
import randomname

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Generate a random name including a first name and adjective
    random_name = randomname.generate()
    json = {"name": random_name}
    return jsonify(json)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
