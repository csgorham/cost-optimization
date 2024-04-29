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
db_file = './database-pricing.csv'
df_db = pd.DataFrame(pd.read_csv("database-pricing.csv"))

df_ec2 = pd.read_csv(ec2_file)
df_azure = pd.read_csv(azure_file)
df_ec2['RAM'] = pd.to_numeric(df_ec2['RAM'])
df_ec2['VCPU'] = pd.to_numeric(df_ec2['VCPU'])
df_azure['RAM'] = pd.to_numeric(df_azure['RAM'])
df_azure['VCPU'] = pd.to_numeric(df_azure['VCPU'])




@app.route('/chat', methods=['POST'])
def chat(RAM=1, VCPU=1, service=1):
    params = request.get_json()
    RAM = params.get('RAM')
    VCPU = params.get('VCPU')

    type = params.get('type')
    service = params.get('service')

    if RAM is None:
        RAM = "1"
    if VCPU is None:
        VCPU = "1"

    if type[0] == 'd' or 'D':

        df_db_reqservice_type = df_db.loc[df_db['Service'] == service, 'Type']
        df_db_reqservice_cloud = df_db.loc[df_db['Service'] == service, 'Cloud Provider']
        df_db_reqservice_price = df_db.loc[df_db['Service'] == service, 'Basic Minimum Price (Starting)']
        df_db_reqservice_type.reset_index(drop=True, inplace=True)
        df_db_reqservice_cloud.reset_index(drop=True, inplace=True)
        df_db_reqservice_price.reset_index(drop=True, inplace=True)
        df_db_reqservice_type = df_db_reqservice_type[0]
        df_db_reqservice_cloud = df_db_reqservice_cloud[0]
        df_db_reqservice_price = df_db_reqservice_price[0]

        if df_db_reqservice_cloud == 'AWS':
            df_db_alt = df_db.loc[df_db['Type'] == df_db_reqservice_type]
            df_db_alt = df_db_alt.loc[df_db_alt['Cloud Provider'] == 'Azure']
            df_db_alt_l = df_db_alt.loc[ df_db_alt['Basic Minimum Price (Starting)'] == 'Pay-per-use (compute and storage)']
            df_db_alt_l = list(df_db_alt_l['Service'])
            df_db_alt = df_db_alt.loc[ df_db_alt['Basic Minimum Price (Starting)'] != 'Pay-per-use (compute and storage)']
            df_db_alt.reset_index(drop=True, inplace=True)
        elif df_db_reqservice_cloud == 'Azure':
            df_db_alt = df_db.loc[df_db['Type'] == df_db_reqservice_type]
            df_db_alt = df_db_alt.loc[df_db_alt['Cloud Provider'] == 'AWS']
            df_db_alt_l = df_db_alt.loc[ df_db_alt['Basic Minimum Price (Starting)'] == 'Pay-per-use (compute and storage)']
            df_db_alt_l = list(df_db_alt_l['Service'])
            df_db_alt = df_db_alt.loc[df_db_alt['Basic Minimum Price (Starting)'] != 'Pay-per-use (compute and storage)']
            df_db_alt.reset_index(drop=True, inplace=True)

        if len(df_db_alt_l) > 0:
            response = service + " cost is " + df_db_reqservice_price.lower() + ". A " + df_db_reqservice_type.lower() + \
                       " alternative from " + df_db_alt['Cloud Provider'][0] + " is " + df_db_alt['Service'][
                           0] + " which costs " + \
                       df_db_alt['Basic Minimum Price (Starting)'][
                           0].lower() + ". " + "Other Azure options are: " + ', '.join(str(x) for x in df_db_alt_l) \
                       + ' which are pay-per-use (compute and storage).'

        else:
            response = service + " cost is " + df_db_reqservice_price.lower() + ". A " + df_db_reqservice_type.lower() + \
                       " alternative from " + df_db_alt['Cloud Provider'][0] + " is " + df_db_alt['Service'][
                           0] + " which costs " + \
                       df_db_alt['Basic Minimum Price (Starting)'][0].lower() + ". "

        response_data = {
        "RAM": 0,
        "VCPU": 0,
        "response": response,
    }

    if type[0] == 'v' or 'V':
#        RAM = params.get('RAM')
        RAM = float(''.join(filter(lambda x: x.isdigit() or x in '.', RAM)))

 #       VCPU = params.get('VCPU')
        VCPU = int(''.join(filter(lambda x: x.isdigit(), VCPU)))

        df_ec2_match = df_ec2[df_ec2['VCPU'] == VCPU]
        df_ec2_match = df_ec2_match[df_ec2_match['RAM'] == RAM]
        df_ec2_match = df_ec2_match.sort_values(by=['HOURLY ON DEMAND'])

        df_azure_match = df_azure[df_azure['VCPU'] == VCPU]
        df_azure_match = df_azure_match[df_azure_match['RAM'] == RAM]
        df_azure_match = df_azure_match.sort_values(by=['HOURLY ON DEMAND'])

        df_together = pd.DataFrame()

        if df_azure_match.empty:
            pass
        else:
            if len(df_azure_match) >= 2:
                df_together = pd.concat([df_together, pd.DataFrame(['Azure', df_azure_match['INSTANCE'].iloc[0],
                                                                df_azure_match['HOURLY ON DEMAND'].iloc[0]]).T],
                                    ignore_index=True)

                df_together = pd.concat([df_together, pd.DataFrame(['Azure', df_azure_match['INSTANCE'].iloc[-1],
                                                                df_azure_match['HOURLY ON DEMAND'].iloc[-1]]).T],
                                    ignore_index=True)
            elif len(df_azure_match) == 1:
                df_together = pd.concat([df_together, pd.DataFrame(['Azure', df_azure_match['INSTANCE'].iloc[0],
                                                                df_azure_match['HOURLY ON DEMAND'].iloc[0]]).T],
                                    ignore_index=True)

        if df_ec2_match.empty:
            pass
        else:
            if len(df_ec2_match) >= 2:
                df_together = pd.concat([df_together, pd.DataFrame(['AWS', df_ec2_match['INSTANCE'].iloc[0],
                                                                df_ec2_match['HOURLY ON DEMAND'].iloc[0]]).T],
                                    ignore_index=True)

                df_together = pd.concat([df_together, pd.DataFrame(['AWS', df_ec2_match['INSTANCE'].iloc[-1],
                                                                df_ec2_match['HOURLY ON DEMAND'].iloc[-1]]).T],
                                    ignore_index=True)
            elif len(df_ec2_match) == 1:
                df_together = pd.concat([df_together, pd.DataFrame(['AWS', df_ec2_match['INSTANCE'].iloc[0],
                                                                df_ec2_match['HOURLY ON DEMAND'].iloc[0]]).T],
                                    ignore_index=True)

        if df_together.empty:
            pass
        else:
            df_together.columns = ['provider', 'name', 'hourly-on-demand']
            df_together['hourly-on-demand'] = pd.to_numeric(df_together['hourly-on-demand'])
            df_together = df_together.sort_values(by=['hourly-on-demand'])

        if (df_azure_match.empty == False) and (df_ec2_match.empty == False):
            response = "Your lowest cost option for " + str(RAM) + "Gb RAM and " + str(VCPU) + " vCPU is " + \
                   df_together['name'].iloc[0] + " from " + \
                   df_together['provider'].iloc[0] + " which costs $" + str(df_together['hourly-on-demand'].iloc[0]) + \
                   " hourly on demand. The lowest cost option from " + df_together['provider'].iloc[1] + " is " + \
                   df_together['name'].iloc[1] + \
                   " which costs $" + str(df_together['hourly-on-demand'].iloc[1]) + " hourly on demand."

        elif (df_ec2_match.empty == False) and (df_azure_match.empty == True):
            response = "Azure does not provide this option. Your lowest cost option for " + str(RAM) + "Gb RAM and " + str(
            VCPU) + " vCPU is " + df_together['name'].iloc[0] + " from " + \
                   df_together['provider'].iloc[0] + " which costs $" + str(df_together['hourly-on-demand'].iloc[0]) + \
                   " hourly on demand."

        elif (df_azure_match.empty == False) and (df_ec2_match.empty == True):
            response = "AWS does not provide this option. Your lowest cost option for " + str(RAM) + "Gb RAM and " + str(
            VCPU) + " vCPU is " + df_together['name'].iloc[0] + " from " + \
                   df_together['provider'].iloc[0] + " which costs $" + str(df_together['hourly-on-demand'].iloc[0]) + \
                   " hourly on demand."

        elif (df_azure_match.empty == True) and (df_ec2_match.empty == True):
            response = "This option is not available from AWS or Azure. Try another set of requirements."

        if not RAM:
            return jsonify({"message": "Missing 'RAM' parameter"}), 400

        response_data = {
        "RAM": RAM,
        "VCPU": VCPU,
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