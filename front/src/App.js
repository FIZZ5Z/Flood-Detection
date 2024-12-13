import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // Import CSS for styling

function App() {
  const [location, setLocation] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageResult, setImageResult] = useState(null);
  const [imageError, setImageError] = useState('');

  // Handle prediction based on location
  const handlePredict = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/predict_weather', {
        params: { location },
      });
      setResult(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
      setResult(null);
    }
  };

  // Handle image upload and prediction
  const handleImagePredict = async () => {
    if (!selectedFile) {
      setImageError('Please upload an image');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict_image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImageResult(response.data);
      setImageError('');
    } catch (err) {
      setImageError(err.response?.data?.error || 'Something went wrong');
      setImageResult(null);
    }
  };

  return (
    <div className="app-container">
      <h1 className="app-title">Rainfall and Flood Prediction</h1>

      {/* Location-based prediction */}
      <div className="input-container">
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Enter location"
          className="input-field"
        />
        <button onClick={handlePredict} className="predict-button">
          Predict by Location
        </button>
      </div>
      {error && <p className="error-message">{error}</p>}
      {result && (
        <div className="result-container">
          <h3 className="result-title">Predictions</h3>
          <p><strong>Rainfall Prediction:</strong> {result['Rainfall Prediction']}</p>
          <p><strong>Flood Prediction:</strong> {result['Flood Prediction']}</p>
          <h3 className="weather-title">Weather Data</h3>
          <pre className="weather-data">{JSON.stringify(result['Weather Data'], null, 2)}</pre>
        </div>
      )}

      {/* Image-based prediction */}
      <div className="image-container">
        <h2 className="section-title">Flood Detection by Image</h2>
        <input
          type="file"
          onChange={(e) => setSelectedFile(e.target.files[0])}
          className="file-input"
        />
        <button onClick={handleImagePredict} className="predict-button">
          Predict by Image
        </button>
        {imageError && <p className="error-message">{imageError}</p>}
        {imageResult && (
          <div className="image-result-container">
            <h3 className="result-title">Image Prediction</h3>
            <p><strong>Prediction:</strong> {imageResult.prediction}</p>
            
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
