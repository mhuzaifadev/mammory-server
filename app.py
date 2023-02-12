from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from threading import Thread

# from gunicorn import glogging
import os
import firebase_admin
from firebase_admin import credentials

# code for endpoints
from mammo_detect import Mammogram
from ultrasound_detect import Ultrasound

from get_hospitals import Hospitals
from get_reports import Reports

app = Flask(__name__)
api = Api(app)

#define path for the json file with credentials
path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\","/")+"/mammory-firebase-adminsdk-6ofc3-a36c7f4805.json"
# Initialize Firebase app
cred = credentials.Certificate(path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mammory-default-rtdb.firebaseio.com/'
})

class Index(Resource):
    def get(self):
        return make_response(
                jsonify(
                    {
                        'message': 'Welcome to the API for Mammory App\nStatus is OKAY!'
                        }), 
                    200)
# API Endpoints
api.add_resource(Index, '/api/', methods=['GET'])

#For mammogram Model
api.add_resource(Mammogram, '/api/mammogram', methods=['POST'])

#For ultrasound Model
api.add_resource(Ultrasound, '/api/ultrasound',methods= ['POST'])

#
api.add_resource(Hospitals, '/api/gethospitals', methods=['GET'])
api.add_resource(Reports, '/api/getreports', methods=['GET'])

if __name__ == '__main__':
    # run app with os environment host and port

    app.run(threaded = True)
