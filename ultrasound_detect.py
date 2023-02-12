from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from threading import Thread
import json
from queue import Queue
from image_processing import Image_Processing
from report_generation import ReportGeneration

class Ultrasound(Resource):
    def post(self):
        email = request.args.get("email")
        full_name = request.args.get("full_name")
        date_of_birth = request.args.get("date_of_birth")

        if email is None:
            return make_response(jsonify({'error': 'email is required as a query parameter'}), 400)
        elif full_name is None:
            return make_response(jsonify({'error': 'full_name is required as a query parameter'}), 400)
        elif date_of_birth is None:
            return make_response(jsonify({'error': 'date_of_birth is required as a query parameter'}), 400)

        if 'image' in request.files:
            image = request.files['image'].read()


            # Create a queue to communicate the results from the worker thread
            queue = Queue()

            # Start a new thread to do some heavy processing
            thread = Thread(target=self.ultrasound_detect, args=(image,full_name,date_of_birth,email, queue))
            thread.start()

            thread.join()

            # Wait for the worker thread to finish and get the results
            predictions = queue.get()

            # Return the response
            json_results = json.dumps(list(predictions))
            return make_response(json_results, 200)
        else:
            return make_response(jsonify({'status': 'Bad Request'}), 400)

    def ultrasound_detect(self, image,full_name,date_of_birth,email,queue):
        
        report_type, lesion, risk_factor, message, sub_text = Image_Processing().ultrasound_detect(image)
        # print(report_type, lesion, risk_factor, message, sub_text)
        processed_image_grid = Image_Processing().image_processing_grid(image,"Ultrasound")

        pdf_file_name, data = ReportGeneration().generate_report(full_name, date_of_birth, email, lesion, risk_factor, processed_image_grid, message, sub_text, report_type)
        response = ReportGeneration().push_to_firebase(pdf_file_name, data)

        # Put the results in the queue
        queue.put(response)
