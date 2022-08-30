import time
from flask import Flask, request
import SmarthubSession as smarthub
import json

# importing sys
import sys
# adding Folder_2 to the system path
# sys.path.insert(0, '/Users/rodericktabalba/Documents/Articulate/abhinav_articulate/smarthub_beta/smarthub_beta_main')
app = Flask(__name__)
# from run_smarthub import RunSmartHub
# smarthub = RunSmartHub()

@app.route('/', methods=["POST"])
def makePrediction():
    utterance = request.json['data']
    gesture = -1
    data = utterance, gesture
    smarthub.run(data)
    # smarthub.GetPrediction(request.json['data'], -1)
    # print(request.json['data'])
    return {'time': time.time()}

