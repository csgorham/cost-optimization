from pydantic import BaseModel

#app = Flask(__name__)
#from flask_openapi3 import OpenAPI, Info, Tag
#info = Info(title="Developer Pricing API", version="1.0.0")
#app = OpenAPI(__name__, info=info)
from flask_restful import reqparse
from flask import Flask, request, jsonify, render_template
from apiflask import APIFlask
import os, json, requests

app = APIFlask(__name__, spec_path='/openapi.json')
app.config['OPENAPI_VERSION'] = '3.0.2'
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(app.root_path, 'openapi.json')

@app.route('/chat', methods=['POST'])
def chat():
    params = request.get_json()
    message = params.get('message')
    history = params.get('history')

    if not message:
        return jsonify({"message": "Missing 'message' parameter"}), 400

    response_data = {
        "message": message,
        "history": history,
        "response": 'OK something 1',
    }
    return jsonify(response_data), 200


def parse_arg_from_requests(arg, **kwargs):
    parse = reqparse.RequestParser()
    parse.add_argument(arg, **kwargs)
    args = parse.parse_args()
    return args[arg]

if __name__ == "__main__":
    app.run(host="0.0.0.0")
#    app.run(debug=True)