from pydantic import BaseModel

#app = Flask(__name__)
#from flask_openapi3 import OpenAPI, Info, Tag
#info = Info(title="Developer Pricing API", version="1.0.0")
#app = OpenAPI(__name__, info=info)
from flask_restful import reqparse
from flask import Flask, request, jsonify
from apiflask import APIFlask
app = APIFlask(__name__, spec_path='/openapi.json')
app.config['OPENAPI_VERSION'] = '3.0.2'
#app.config['SPEC_FORMAT'] = 'yaml'

languages = [
    "English", "Spanish", "French", "German", "Italian", "Portuguese", "Swedish"
]

@app.route("/")
def home():
    return jsonify({
            "status": "online"
        })

@app.route("/languages")
def get_languages():
    return jsonify({
        "languages": languages
    })

def parse_arg_from_requests(arg, **kwargs):
    parse = reqparse.RequestParser()
    parse.add_argument(arg, **kwargs)
    args = parse.parse_args()
    return args[arg]

if __name__ == "__main__":
    app.run(host="0.0.0.0")
    #app.run(debug=True)