from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from threading import Thread
from queue import Queue
import pandas as pd
import json

class Reports(Resource):
    def get(self):
        accountID = request.args.get("accountID")
        records = request.args.get("records")
        
        if accountID is None:
            return make_response(jsonify({'error': 'lat is required as a query parameter'}), 400)
        elif records is None:
            return make_response(jsonify({'error': 'lng is required as a query parameter'}), 400)
        else:
            # Create a queue to communicate the results from the worker thread
            queue = Queue()

            # Start a new thread to do some heavy processing
            thread = Thread(target=getreports, args=(accountID,records, queue))
            thread.start()

            thread.join()

            # Wait for the worker thread to finish and get the results
            record_data = queue.get()

            # record_data = json.dumps(list(record_data))

            # Return the response
            # json_results = marker_locations
            if record_data is not None:
                return make_response(jsonify(record_data), 200)
            else:
                return make_response(jsonify({'status': 'Bad Request'}), 400)
            
        # else:
        #     return make_response(jsonify({'status': 'Bad Request'}), 400)

def getreports(accountID,records, queue):
    # Do some heavy processing here
    # image_results = {'width': image.width, 'height': image.height}
    # print(image_results,"\n\n\n")
    # Put the results in the queue
    df = pd.read_csv('reports.csv')
    # data = df.to_json()
    print(df.to_dict(orient='records'))
    queue.put(df.to_dict(orient='records'))

    # # Write JSON results to a file
    # with open('image_results.json', 'w') as outfile:
    #     json.dump(json_results, outfile)