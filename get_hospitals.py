from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from threading import Thread
from queue import Queue
import pandas as pd

class Hospitals(Resource):
    def get(self):
        lat = request.args.get("lat")
        lng = request.args.get("lng")
        within = request.args.get("within")
        if lat is None:
            return make_response(jsonify({'error': 'lat is required as a query parameter'}), 400)
        elif lng is None:
            return make_response(jsonify({'error': 'lng is required as a query parameter'}), 400)
        elif within is None:
            return make_response(jsonify({'error': 'within is required as a query parameter'}), 400)

        else:
            # Create a queue to communicate the results from the worker thread
            queue = Queue()

            # Start a new thread to do some heavy processing
            thread = Thread(target=gethospitals, args=(lat,lng,within, queue))
            thread.start()

            thread.join()

            # Wait for the worker thread to finish and get the results
            marker_locations = queue.get()

            # Return the response
            # json_results = marker_locations
            if marker_locations is not None:
                return make_response(jsonify(marker_locations), 200)
            else:
                return make_response(jsonify({'status': 'Bad Request'}), 400)
            
        # else:
        #     return make_response(jsonify({'status': 'Bad Request'}), 400)

def gethospitals(lat,lng,within, queue):
    # Do some heavy processing here
    # image_results = {'width': image.width, 'height': image.height}
    # print(image_results,"\n\n\n")
    # Put the results in the queue
    df = pd.read_csv('hospitals.csv')
    print(df.to_dict(orient='records'))
    queue.put(df.to_dict(orient='records'))

    # # Write JSON results to a file
    # with open('image_results.json', 'w') as outfile:
    #     json.dump(json_results, outfile)