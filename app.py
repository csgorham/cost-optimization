from pydantic import BaseModel

#app = Flask(__name__)
#from flask_openapi3 import OpenAPI, Info, Tag
#info = Info(title="Developer Pricing API", version="1.0.0")
#app = OpenAPI(__name__, info=info)
from flask_restful import reqparse
from flask import Flask, request, jsonify, render_template
from apiflask import APIFlask
import os, json, requests
import pandas as pd

app = APIFlask(__name__, spec_path='/openapi.json')
app.config['OPENAPI_VERSION'] = '3.0.2'
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(app.root_path, 'openapi.json')

ec2_file = './Amazon-Amazon-EC2-Instance-Types.csv'
azure_file = './Azure-Azure-Virtual-Machines.csv'
df_ec2 = pd.read_csv(ec2_file)
df_azure = pd.read_csv(azure_file)
df_ec2['RAM'] = pd.to_numeric(df_ec2['RAM'])
df_ec2['VCPU'] = pd.to_numeric(df_ec2['VCPU'])
df_azure['RAM'] = pd.to_numeric(df_azure['RAM'])
df_azure['VCPU'] = pd.to_numeric(df_azure['VCPU'])




@app.route('/chat', methods=['POST'])
def chat():
    params = request.get_json()
    #message = params.get('message')
    #history = params.get('history')

    message = params.get('RAM')
    history = params.get('VCPU')
    RAM = 8
    VCPU = 2

    df_ec2_match = df_ec2[df_ec2['VCPU'] == VCPU]
    df_ec2_match = df_ec2_match[df_ec2_match['RAM'] == RAM]
    df_ec2_match = df_ec2_match.sort_values(by=['HOURLY ON DEMAND'])

    df_azure_match = df_azure[df_azure['VCPU'] == VCPU]
    df_azure_match = df_azure_match[df_azure_match['RAM'] == RAM]
    df_azure_match = df_azure_match.sort_values(by=['HOURLY ON DEMAND'])

    df_together = pd.DataFrame()

    df_together = pd.concat([df_together, pd.DataFrame(['Azure', df_azure_match['INSTANCE'].iloc[0],
                                                        df_azure_match['HOURLY ON DEMAND'].iloc[0]]).T],
                            ignore_index=True)

    df_together = pd.concat([df_together, pd.DataFrame(['Azure', df_azure_match['INSTANCE'].iloc[-1],
                                                        df_azure_match['HOURLY ON DEMAND'].iloc[-1]]).T],
                            ignore_index=True)

    df_together = pd.concat([df_together, pd.DataFrame(['AWS', df_ec2_match['INSTANCE'].iloc[0],
                                                        df_ec2_match['HOURLY ON DEMAND'].iloc[0]]).T],
                            ignore_index=True)

    df_together = pd.concat([df_together, pd.DataFrame(['AWS', df_ec2_match['INSTANCE'].iloc[-1],
                                                        df_ec2_match['HOURLY ON DEMAND'].iloc[-1]]).T],
                            ignore_index=True)
    df_together.columns = ['provider', 'name', 'hourly-on-demand']
    df_together['hourly-on-demand'] = pd.to_numeric(df_together['hourly-on-demand'])
    df_together = df_together.sort_values(by=['hourly-on-demand'])

    response = "Your lowest cost option for " + str(RAM) + "Gb RAM and " + str(VCPU) + " vCPU is " + \
               df_together['name'].iloc[0] + " from " + \
               df_together['provider'].iloc[0] + " which costs $" + str(df_together['hourly-on-demand'].iloc[0]) + \
               " hourly on demand. The lowest cost option from " + df_together['provider'].iloc[1] + " is " + \
               df_together['name'].iloc[1] + \
               " which costs $" + str(df_together['hourly-on-demand'].iloc[1]) + " hourly on demand."
    print(response)


    if not message:
        return jsonify({"message": "Missing 'message' parameter"}), 400

    response_data = {
        "message": message,
        "history": history,
        "response": response,
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