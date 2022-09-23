import time
from flask import Flask, request
import json

# importing sys
import sys
# importing sys
# adding Folder_2 to the system path
sys.path.insert(0, '/Users/rodericktabalba/Documents/GitHub/articulate-/python/smarthub_beta_main')
app = Flask(__name__)
from run_smarthub import SmarthubSession

smarthub = SmarthubSession()
# from setuptools import setup

# setup(
#     name='/Users/rodericktabalba/Documents/GitHub/articulate-/python/smarthub_beta_main',
#     packages=['/Users/rodericktabalba/Documents/GitHub/articulate-/python/smarthub_beta_main'],
#     include_package_data=True,
#     install_requires=[
#         'flask',
# ],)


@app.route('/', methods=["POST"])
def makePrediction():
    command = request.get_json()
    data1 = smarthub.run(command)
    return json.dumps(data1)