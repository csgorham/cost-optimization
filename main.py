from flask import Flask, request, jsonify
from flask_openapi3 import Api
app = Flask(__name__)
api = Api(app)


@app.route("/")
def hello_world():
    return jsonify({"message": "Hello World!"})

spec = api.spec
with open('openapi.json', 'w') as f:
    json.dump(spec, f)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)