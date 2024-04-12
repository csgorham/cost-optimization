from pydantic import BaseModel

from flask import Flask, request, jsonify
#app = Flask(__name__)


#from flask_openapi3 import OpenAPI, Info, Tag
#info = Info(title="Developer Pricing API", version="1.0.0")
#app = OpenAPI(__name__, info=info)

from apiflask import APIFlask
app = APIFlask(__name__, spec_path='/openapi.json')
app.config['OPENAPI_VERSION'] = '3.0.2'
#app.config['SPEC_FORMAT'] = 'yaml'

class DeveloperPricing(BaseModel):
    db: str
    ml: str

@app.route("/")
def hello_world():
    return jsonify({"message": "Hello World!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0")
    #app.run(debug=True)