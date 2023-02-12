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
        #Get path of current directory

        path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\","/")+ "/Hospitals.csv"

        # Read the csv file containing information about hospitals into a Pandas dataframe
        
        print(path)
        data = pd.read_csv(path)
        print(data)
        # Extract the latitude and longitude values for each hospital from the dataframe
        latitudes = list(data["Latitude"])
        longitudes = list(data["Longitude"])

        # Initialize variables to keep track of the hospitals
        row_index = 0
        marker_locations = []

        # Loop through the latitudes and longitudes, and calculate the distance between the current location and each hospital
        for i, j in zip(latitudes, longitudes):
            if geo.geodesic(current_location, (i, j)).km <= float(within_distance):
                # If the hospital is within the specified distance, add it to the list of nearby hospitals
                marker_locations.append(data.iloc[row_index].to_dict())
            row_index = row_index + 1

        # Return the list of nearby hospitals as a JSON string
        queue.put(marker_locations)
        # return json.dumps({"response" : marker_locations}, indent=4)