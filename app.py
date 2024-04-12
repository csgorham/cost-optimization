from pydantic import BaseModel

#from flask import Flask, request, jsonify
from flask_openapi3 import OpenAPI, Info, Tag
#from flask_rest_api import Api
#app = Flask(__name__)
#extension = FlaskOpenAPIExtension(app)

info = Info(title="Developer Pricing API", version="1.0.0")
app = OpenAPI(__name__, info=info)
#api = Api(app)

class DeveloperPricing(BaseModel):
    db: str
    ml: str


@app.route("/")
def hello_world():
    return jsonify({"message": "Hello World!"})


if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000)
    app.run(debug=True)