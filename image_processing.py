import numpy as np
import cv2
from tensorflow import keras
import tensorflow as tf
import os
from io import BytesIO
import docx

import matplotlib.pyplot as plt


class Image_Processing:

    def ultrasound_detect(self, image):
        # Convert the image data to a byte string
        # self.image = image.tobytes()

        # Read the image using tf.io.read_file()
        
        self.image = tf.io.decode_image(image, channels=3)
        self.image = tf.image.convert_image_dtype(self.image, tf.float32) / 255.0
        self.image = tf.image.resize(self.image, (224, 224))
        self.image = tf.expand_dims(self.image, 0)

        if tf.shape(self.image)[2] == tf.convert_to_tensor(1):
            self.image = tf.image.grayscale_to_rgb(self.image)

        path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\","/")
        model = keras.models.load_model(path+"/ultrasound-model.h5")
        prediction = model.predict(self.image)
        
        class_type = np.argmax(prediction)
        print(prediction)
        risk_factor = np.max(prediction)

        lesion, headline, sub_text = self.message(class_type, risk_factor)
        if lesion == "Normal":
            risk_factor = 1 - risk_factor
        
        return "Ultrasound", lesion, "%.2f" % (risk_factor*100), headline, sub_text


    def mammogram_detect(self, image):
        try:
            self.image = image

            # Convert the binary data to a numpy array
            self.image = np.frombuffer(self.image, dtype=np.uint8)


            # # Decode the numpy array using OpenCV
            self.image = cv2.imdecode(self.image, cv2.IMREAD_UNCHANGED)
            # self.image = cv2.imread("C:/Users/kingh/Downloads/mdb001.jpg")

            # grayscale to BGR


            # Receive image from API in the form of body file, read it using cv2
        
            self.image = cv2.resize(self.image, (224, 224))
            self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
            self.image = np.expand_dims(self.image, axis = 0)
            self.image = self.image.astype('float32')
            self.image /= 255
            
            path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).replace("\\","/")
            self.model = keras.models.load_model(path+"/mammogram-model.h5")
            prediction = self.model.predict(self.image)
            class_type = np.argmax(prediction)
            print(prediction)
            risk_factor = np.max(prediction)

            lesion, headline, sub_text = self.message(class_type, risk_factor)
            if lesion == "Normal":
                risk_factor = 1 - risk_factor
            
            return "Mammogram", lesion, "%.2f" % (risk_factor*100), headline, sub_text
        except:
            return "Mammogram", "Error", "Error", "Error", "Error"

    def message(self, class_type, risk_factor):
        if class_type == 0:
            lesion = "Normal"
            risk_factor = 1 - risk_factor
            headline = "Normal Screening Result: No Evidence of Breast Cancer Detected"
            sub_text = "While it's great news that your recent breast cancer screening results came back normal, it's important to remember that regular check-ups and screenings are crucial in early detection and prevention. We recommend scheduling a screening at least once a year, and if you have any concerns or questions, don't hesitate to seek a second opinion from a trusted medical professional. Stay proactive and vigilant in your health journey!"

        else:
            if class_type == 1:
                lesion = "Benign"
            elif class_type == 2:
                lesion = "Malignant"

            if risk_factor < 0.3:
                headline = "Your Wellness is so far assured: No Evidence of Breast Cancer Detected"
                sub_text = "While it's great news that your recent breast cancer screening results came back normal, it's important to remember that regular check-ups and screenings are crucial in early detection and prevention. We recommend scheduling a screening at least once a year, and if you have any concerns or questions, don't hesitate to seek a second opinion from a trusted medical professional. Stay proactive and vigilant in your health journey!"
            elif risk_factor < 0.5:
                headline = "Doctor Consultation Recommended: Taking a Proactive Approach to Your Health"
                sub_text = "While it's important to take control of your health and seek medical advice, it doesn't mean there is necessarily a problem. Receiving a less-than-ideal result from a breast cancer screening can be scary, but it's important to remember that additional testing and consultation with a doctor can provide a clearer picture of your health. Don't hesitate to seek a second opinion and get all the information you need to make informed decisions about your well-being. You deserve to feel confident and empowered in your health journey."
            elif risk_factor < 0.75:
                headline = "Possible " +lesion+ " Lesion: Further Evaluation Required"
                sub_text = "A "+lesion+" lesion detected in your breast cancer screening requires further evaluation. We recommend seeking a second opinion and consulting with a doctor. Your well-being is our top priority, and we are here to support you. Stay positive and proactive during this time."
            else:
                headline = "Classified with " +lesion+ " Breast Cancer: Prompt Medical Attention Necessary"
                sub_text = "A "+lesion+" breast cancer diagnosis is a serious matter and requires immediate medical attention. We recommend seeking a second opinion from a trusted doctor to ensure the most accurate information and appropriate treatment plan. It's important to stay positive and proactive during this time and do not hesitate in seeking the support and guidance of medical professionals. Early detection is key in successfully managing and treating breast cancer. Remember, you are not alone in this journey and there is a wealth of resources and support available to you."

        return lesion, headline, sub_text


    def image_processing_grid(self, image, image_type):
        
        # Convert the binary data to a numpy array
        image = np.frombuffer(image, dtype=np.uint8)

        # # Decode the numpy array using OpenCV
        image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
        
        # Resize image to 224x224
        
        gray = cv2.resize(image, (224, 224), interpolation = cv2.INTER_LINEAR)
        
        # Convert to grayscale
        if image_type == "Ultrasound":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Median filtering
        median = cv2.medianBlur(gray, 5)
        
        # Contrast stretching
        contrast_stretched = np.interp(median, (median.min(), median.max()), (0, 255))
        
        # Thresholding
        _, thresholded = cv2.threshold(contrast_stretched, 128, 255, cv2.THRESH_BINARY)
        
        # Stack all images in the same row
        f, ax = plt.subplots(1, 4, figsize=(20, 5))
        ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax[0].set_title("Input Feed")
        ax[1].imshow(median, cmap='bone')
        ax[1].set_title("Median Filtering")
        ax[2].imshow(contrast_stretched, cmap='twilight', vmin=0, vmax=255)
        ax[2].set_title("Mass Density Stretching")
        ax[3].imshow(thresholded, cmap='viridis')
        ax[3].set_title("Lesion Thresholding")
        

        image_data = BytesIO()

        plt.savefig(image_data, format='png')
        plt.close()

        image_data.seek(0)
        return image_data

