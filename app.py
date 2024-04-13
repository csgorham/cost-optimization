from pydantic import BaseModel

#app = Flask(__name__)
#from flask_openapi3 import OpenAPI, Info, Tag
#info = Info(title="Developer Pricing API", version="1.0.0")
#app = OpenAPI(__name__, info=info)

from flask import Flask, request, jsonify
from apiflask import APIFlask
app = APIFlask(__name__, spec_path='/openapi.json')
app.config['OPENAPI_VERSION'] = '3.0.2'
#app.config['SPEC_FORMAT'] = 'yaml'

class DeveloperPricing(BaseModel):
    db: str
    ml: str

@app.route("/calc_pricing_options', methods=["POST", "GET"])
def calc_pricing_options():
    products = request.json.get('products')
    options = "Options " + products
    return  options #jsonify({"message": "Hello World!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0")
    #app.run(debug=True)