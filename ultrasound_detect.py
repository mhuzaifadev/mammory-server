from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from threading import Thread
import json
import base64
import PIL.Image as Image
import io
from queue import Queue

class Ultrasound(Resource):
    def post(self):
        account_id = request.args.get("accountID")
        if account_id is None:
            return make_response(jsonify({'error': 'accountID is required as a query parameter'}), 400)

        if 'image' in request.files:
            image = request.files['image']
            image = Image.open(image)

            # Create a queue to communicate the results from the worker thread
            queue = Queue()

            # Start a new thread to do some heavy processing
            thread = Thread(target=ultrasound_detect, args=(image, account_id, queue))
            thread.start()

            thread.join()

            # Wait for the worker thread to finish and get the results
            predictions = queue.get()

            # Return the response
            json_results = json.dumps(list(predictions))
            return make_response(json_results, 200)
        else:
            return make_response(jsonify({'status': 'Bad Request'}), 400)

def ultrasound_detect(image,account_id,queue):
    # Do some heavy processing here
    image_results = {'width': image.width, 'height': image.height}
    print(image_results,"\n\n\n")
    print(account_id)
    # Put the results in the queue
    queue.put((image_results,account_id))

    # # Write JSON results to a file
    # with open('image_results.json', 'w') as outfile:
    #     json.dump(json_results, outfile)
