from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from threading import Thread
from queue import Queue
import pandas as pd
import geopy.distance as geo
import json
import os



class Hospitals(Resource):
    def get(self):
        lat = request.args.get("lat")
        lng = request.args.get("lng")
        within = request.args.get("within")
        if lat is None:
            return make_response(jsonify({'error': 'Bad request\nlat is required as a query parameter'}), 400)
        elif lng is None:
            return make_response(jsonify({'error': 'Bad request\nlng is required as a query parameter'}), 400)
        elif within is None:
            return make_response(jsonify({'error': 'Bad request\nwithin is required as a query parameter'}), 400)

        else:
            # Create a queue to communicate the results from the worker thread
            queue = Queue()

            # Start a new thread to do some heavy processing
            thread = Thread(target=self.get_nearby_hospitals, args=((lat,lng),within, queue))
            thread.start()

            thread.join()

            # Wait for the worker thread to finish and get the results
            marker_locations = queue.get()

            # Return the response
            # json_results = marker_locations
            if marker_locations is not None:
                return make_response(jsonify({"response" : marker_locations}), 200)
            else:
                return make_response(jsonify({'status': 'Bad Request'}), 400)
            
        # else:
        #     return make_response(jsonify({'status': 'Bad Request'}), 400)

    def get_nearby_hospitals(self,current_location, within_distance,queue):
        """
        This function takes in a `current_location` in the form of a tuple of latitude and longitude coordinates and a `within_distance` in kilometers,
        and returns a list of hospitals within that distance from the `current_location`.
        The result is returned as a JSON string, with each hospital represented as a dictionary.
        """
        # #Get path of current directory

        # path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\","/")+ "/Hospitals.csv"

        # # Read the csv file containing information about hospitals into a Pandas dataframe
        
        # print(path)
        #hospitals DATA
        data = {
            'Place Name': ['Cancer Foundation hospital', 'Bait-ul-Sukoon Cancer Hospital', 'Jinnah Hospital Karachi', ' Abbassi Shaheed Hospital', 'Aga Khan University Hospital', ' Dr. Ziauddin Cancer Hospital', 'Dr. Ruth K.M. Pfau, Civil Hospital Karachi', 'A.O. Hospital', 'Burhani Hospital', 'Kiran Hospital', 'Pak Onco Care (Cancer Treatment Center)', 'PNS Shifa Hospital', 'Shaukat Khanum Memorial Trust', 'Oncology Ward', 'Tahir Medical Center', 'Anklesaria Hospital', 'Neurospinal & cancer care Institute Karachi Sindh Pakistan', 'Saifee Hospital', 'Medicare Cardiac & General Hospital', 'KARACHI MEDICAL COMPLEX Consultant Clinic', 'National Medical center', 'Fatimiyah Hospital, Karachi', 'Sindh Institute of Urology and Transplantation', 'Mamji Hospital', 'Hilal e Ahmer Hospital'], 
            'Latitude': [24.91294769, 24.87321498, 24.85307906, 24.92109422, 24.89248713, 24.92373096, 24.85907683, 24.9179905, 24.85292587, 24.94720397, 24.92372914, 24.83700879, 24.83478576, 24.85968565, 24.88278884, 24.86729051, 24.85476876, 24.93150205, 24.88122728, 24.90216676, 24.83329943, 24.87823562, 24.86119751, 24.93889358, 24.8347477], 
            'Longitude': [67.09308809, 67.07340402, 67.04411956, 67.0296143, 67.0748962, 67.04754945, 67.01012382, 67.03219347, 67.01005865, 67.144677, 67.09081176, 67.05024687, 67.0331277, 67.01170281, 67.08223983, 67.02371797, 67.04346917, 67.03854763, 67.06352577, 67.08133529, 67.17916143, 67.03413041, 67.01204601, 67.07745957, 67.03318767], 
            'Contact': ['(02)134991071', '(021) 34553834', '021 99201300', '021 9260400', '021 111 911 911', '021 36648237', '021 99215740', '021 36685560', '021 99201300', '(021)99261601', '(021)34980057', '(021)48506777', '(021)35872573', '-', '(021)34380163', '(021)32720371', '-', '(021)36789400', '(021)38658901', '(0)3322173522', '-', '(021)111012014', '(021)99215752', '-', '(0)3332442683']
            }
        
        # Extract the latitude and longitude values for each hospital from the dataframe
        

        # Initialize variables to keep track of the hospitals
        row_index = 0
        marker_locations = []

        # Loop through the latitudes and longitudes, and calculate the distance between the current location and each hospital
        # for hospital in data:
        #     hospital_location = zip(hospital["Latitude"], hospital["Longitude"]
        #     if geo.geodesic(current_location, hospital_location).km <= float(within_distance):
        #         # If the hospital is within the specified distance, add it to the list of nearby hospitals
        #         marker_locations.append(hospital.iloc[row_index].to_dict())
        #     row_index = row_index + 1

        for i, j in zip(data['Latitude'], data['Longitude']):
            if geo.geodesic(current_location, (i, j)).km <= float(within_distance):
                # If the hospital is within the specified distance, add it to the list of nearby hospitals
                marker_locations.append({
                    'Place Name': data['Place Name'][row_index],
                    'Latitude': data['Latitude'][row_index],
                    'Longitude': data['Longitude'][row_index],
                    'Contact':data['Contact'][row_index]

                })
            row_index = row_index + 1
        # Return the list of nearby hospitals as a JSON string
        queue.put(marker_locations)
