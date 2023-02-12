from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from threading import Thread
from queue import Queue
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

class Reports(Resource):
    def get(self):
        accountID = request.args.get("accountID")
        
        if accountID is None:
            return make_response(jsonify({'error': 'accountID is required as a query parameter'}), 400)
        else:
            # Create a queue to communicate the results from the worker thread
            queue = Queue()

            # Start a new thread to do some heavy processing
            thread = Thread(target=self.get_reports, args=(accountID, queue))
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

    def get_reports(self, email,queue):

        
        # Get a reference to the database
        ref = db.reference("/")

        # Define the email address to match
        email_to_match = email

        # Query the database for the matching entry
        query = ref.order_by_child('Account ID').equal_to(email_to_match).get()

        # Extract all fields of the matching entry
        all_entries = []
        if query:
            for key in query.keys():
                matching_entry = query[key]
                # Do something with the matching entry, e.g. print all fields
                
                all_entries.append(matching_entry)
        else:
            print('No matching entry found.')
        
        queue.put(all_entries)

