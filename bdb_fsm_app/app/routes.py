from app import app
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.dates as md
from flask import request
from flask import jsonify
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import json
import pprint
import rapidjson
from transitions.extensions import GraphMachine
from app.thermostat_fsm import FSM
from cryptoconditions import Fulfillment
from flask import render_template, abort
from sha3 import sha3_256
from datetime import datetime, timedelta


bdb_root_url = 'http://localhost:9984'
bdb = BigchainDB(bdb_root_url)
keys = generate_keypair()

collection = bdb.assets
transactions = bdb.transactions

fsm = FSM()

thermostat = GraphMachine(model=fsm, states=list(fsm.states.keys()), initial=fsm.initial_state, transitions=fsm.transitions)

#### FSM initialization ####
last_state = collection.get(search="fsm")

if len(last_state) > 0:
    last_state = last_state[-1]
    fsm.initialize_fsm(last_state)
#### FSM initialization ####


@app.route("/data", methods=['POST'])
def create_transaction():
    data = json.loads(request.data)
    transaction_data = fsm.run_fsm(data)
    transaction_data["data"]["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    prepared_creation_tx = bdb.transactions.prepare(operation='CREATE', signers=keys.public_key, asset=transaction_data)
    fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx, private_keys=keys.private_key)
    sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)
    return '{}'.format(json.dumps(sent_creation_tx))
    

@app.route("/graph", methods=['GET'])
def graph():
    return render_template('grafico.html')


@app.route("/graphimages", methods=["GET"])
def get_graph_images():

    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    if start_date != None and end_date != None and start_date <= end_date:

        json_response = {}

        input_labels = []
        output_labels = []

        ### FSM image ###
        b = io.BytesIO()
        fsm.get_graph().draw(b, format="png", prog='dot')
        b.seek(0)
        fsm_img_str = base64.b64encode(b.read()).decode('utf-8')
        json_response["fsm_img_str"] = fsm_img_str
        ### FSM image ###

        transitions = collection.get(search="fsm")

        transitions = [transition for transition in transitions if transition['data']['timestamp'] >= start_date and transition['data']['timestamp'] <= end_date]

        ### Get labels for legends in graphs ###
        if len(transitions)>0:
            data_model = transitions[-1]
            input_labels = data_model['data']['input'].keys()
            output_labels = data_model['data']['output'].keys()

        ### Get labels for legends in graphs ###

        inputs = [list(entry['data']['input'].values()) for entry in transitions]
        outputs = [list(entry['data']['output'].values()) for entry in transitions]
        state_trans = [entry['data']['to'] for entry in transitions]
        timestamps = [entry['data']['timestamp'] for entry in transitions]
        
        timestamps = [datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S') for timestamp in timestamps]
        

        ### Inputs graph ###
        b = io.BytesIO()
        plt.step(timestamps, inputs, marker='o', where='post')
        plt.legend(input_labels)
        plt.xticks(timestamps)
        plt.xticks(rotation=90)
        ax=plt.gca()
        ax.set_xticks(timestamps)
        xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.savefig(b, format='png')
        b.seek(0)
        input_img_str = base64.b64encode(b.read()).decode('utf-8')
        plt.close()
        json_response["input_img_str"] = input_img_str
        ### Inputs graph ###

        ### Output graph ###
        b = io.BytesIO()
        plt.step(timestamps, outputs, marker='o', where='post')
        plt.legend(output_labels)
        plt.xticks(timestamps)
        plt.xticks(rotation=90)
        ax=plt.gca()
        ax.set_xticks(timestamps)
        xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.savefig(b, format='png')
        b.seek(0)
        output_img_str = base64.b64encode(b.read()).decode('utf-8')
        plt.close()
        json_response["output_img_str"] = output_img_str
        ### Output graph ###
        
        ### State transitions graph ###
        b = io.BytesIO()
        plt.step(timestamps, state_trans, marker='o', where='post')
        plt.xticks(timestamps)
        plt.xticks(rotation=90)
        ax=plt.gca()
        ax.set_xticks(timestamps)
        xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.savefig(b, format='png')
        b.seek(0)
        states_img_str = base64.b64encode(b.read()).decode('utf-8')
        plt.close()
        json_response["states_img_str"] = states_img_str
        ### State transitions graph ###
        return jsonify(json_response)
    else:
        abort(400, "Parameters are missing or wrong.")