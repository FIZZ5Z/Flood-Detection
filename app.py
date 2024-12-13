import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from tensorflow.keras.preprocessing import image
import tensorflow as tf
import requests

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Labels for image model predictions
image_labels = ['Flooding', 'No Flooding']

# Preprocessing function for image-based model
def preprocess_image(file):
    img = image.load_img(file, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return tf.keras.applications.mobilenet.preprocess_input(img_array_expanded_dims)

# Flood prediction logic based on weather data
def predict_flood(row):
    score = 0
    if row['pressure'] < 1010: score += 2
    if row['dewpoint'] > 20: score += 2
    if row['humidity'] > 85: score += 2
    if row['cloud'] > 75: score += 2
    if row['sunshine'] < 1.0: score += 1
    if row['windspeed'] > 30: score += 1
    if score >= 8:
        return "Strong Flood Risk"
    elif 5 <= score < 8:
        return "Medium Flood Risk"
    elif 3 <= score < 5:
        return "Low Flood Risk"
    else:
        return "No Flood Risk"

# Load the image-based flood detection model
image_model_path = 'C:/Users/faiza/Desktop/Rain test/best_flood_model.keras'
image_model = tf.keras.models.load_model(image_model_path)

# Load the weather-based flood prediction model
weather_model_path = r"C:\Users\faiza\Desktop\Rain test\rainfall_flood_model.pkl"
with open(weather_model_path, "rb") as file:
    weather_model_data = pickle.load(file)

weather_model = weather_model_data["model"]
feature_names = weather_model_data["feature_names"]

# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for image-based flood detection
@app.route('/predict_image', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Ensure uploads directory exists
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Save the uploaded file
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    # Preprocess the image and make the prediction
    preprocessed_image = preprocess_image(file_path)
    predictions = image_model.predict(preprocessed_image)

    # Get the maximum probability score for predicted class
    result = np.argmax(predictions)
    confidence = float(predictions[0][result])

    if confidence < 0.7:  
        prediction_label = "Flood"
    else:
        prediction_label = "No Flood"

    return jsonify({'prediction': prediction_label, 'confidence': confidence})


# Route for weather-based flood prediction
@app.route('/predict_weather', methods=['GET'])
def predict_weather():
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location is required"}), 400

    api_key = "your_openweathermap_key"
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    weather_response = requests.get(weather_url).json()

    if weather_response.get("cod") != 200:
        return jsonify({"error": "Invalid location or weather data unavailable"}), 400

    # Extract weather parameters
    weather_data = {
        "pressure": weather_response["main"]["pressure"],
        "dewpoint": weather_response["main"]["temp"],
        "humidity": weather_response["main"]["humidity"],
        "cloud": weather_response["clouds"]["all"],
        "sunshine": weather_response["visibility"] / 1000,  # Visibility in km
        "winddirection": weather_response["wind"]["deg"],
        "windspeed": weather_response["wind"]["speed"]
    }

    # Prepare input data
    input_df = pd.DataFrame([weather_data], columns=feature_names)

    # Rainfall prediction
    rainfall_prediction = weather_model.predict(input_df)[0]
    rainfall_result = "Rainfall" if rainfall_prediction == 1 else "No Rainfall"

    # Apply flood prediction logic
    flood_result = predict_flood(input_df.iloc[0])

    return jsonify({
        "Rainfall Prediction": rainfall_result,
        "Flood Prediction": flood_result,
        "Weather Data": weather_data
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
