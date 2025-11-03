# Machine Learning-Based Intrusion Detection System (IDS)

A complete web application for detecting network intrusions using machine learning, built with React frontend and Flask backend.

## ✅ What we've achieved

- End-to-end app working: React frontend + Flask backend with CORS configured for `http://localhost:3000`.
- Model auto-loading from `backend/models/` with fallback to `artifacts/` and robust logging via `LOG_LEVEL`.
- CSV/Parquet file predictions via `POST /api/predict` with preprocessing (column cleaning, numeric coercion, inf/NaN handling, memory downcast).
- Manual input and JSON batch predictions via `POST /api/predict-batch` supporting `feature_names` order alignment.
- Model metadata endpoint `GET /api/metadata` to fetch `feature_names`, classes, and metrics.
- Frontend features:
  - Manual input UI with grouped parameters and 5 cycling sample presets.
  - Results dashboard with summary badges, pie + bar charts, and detailed breakdown.
  - Status indicators and graceful loading states.
- Tests and utilities: backend integration test, CORS test, model tests, app load test.
- Scripts: `setup.sh` for environment setup and `restart_flask.sh` for quick backend restarts.
- Sample data: `cic_ids_test_sample.csv` for quick validation.

## 📁 Project Structure

```
cn project/
├── main.ipynb                 # Jupyter notebook for model training
├── frontend/                  # React application
│   ├── public/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── styles/          # CSS styling
│   │   └── App.js
│   └── package.json
├── backend/                  # Flask API
│   ├── app.py               # Main Flask application
│   ├── models/              # Model files (.joblib) + metadata
│   └── requirements.txt
├── artifacts/               # Alternative model storage (fallback)
├── setup.sh                 # Convenience setup script
└── restart_flask.sh         # Restart helper for backend
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Step 1: Train the Model

1. Open `main.ipynb` in Jupyter Notebook
2. Run all cells to train the model
3. The trained model will be saved in `artifacts/` directory

### Step 2: Setup Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (if not already created):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy model files to backend/models (if needed):
```bash
# The app will automatically look for models in artifacts/ or models/
# Make sure your trained model .joblib files are accessible
```

5. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5050`

Optional helpers:
- `./setup.sh` to bootstrap environments (if applicable)
- `./restart_flask.sh` to restart the backend quickly

### Step 3: Setup Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## 🎯 Features

- **Beautiful Modern UI**: Clean, responsive design with gradient themes
- **File Upload**: Drag-and-drop or click to upload CSV/Parquet files
- **Real-time Analysis**: Instant predictions on network traffic data
- **Visual Analytics**: 
  - Pie chart showing attack distribution
  - Bar chart for detailed attack breakdown
  - Summary statistics with threat level indicators
- **Status Monitoring**: API connection and model status indicators
- **Manual Input Mode**: Grouped features, presets, and ordered submission respecting `feature_names`

## 📊 Usage

1. Ensure both backend and frontend servers are running
2. Open the React app in your browser
3. Check that the status indicator shows "Model Ready"
4. Upload a CSV or Parquet file containing network traffic data
5. View the detection results with detailed statistics and visualizations

## 🔧 API Endpoints

### `GET /api/health`
Check API and model status

### `POST /api/predict`
Upload a file for prediction
- **Request**: Form data with `file` field (CSV or Parquet)
- **Response**: JSON with predictions, counts, statistics, classes

### `POST /api/predict-batch`
Batch predict from JSON arrays or manual input
- **Request**: `{ data: [[...]], feature_names: [...] }` or `{ data: [{...}, {...}] }`
- Aligns to training order using saved metadata

### `GET /api/metadata`
Fetch model metadata
- **Response**: feature names, class names, counts, optional model name and macro F1

## 📦 Dependencies

### Backend
- Flask, flask-cors
- pandas, numpy
- scikit-learn
- joblib
- imbalanced-learn

### Frontend
- React 18.2.0
- recharts (for visualizations)
- axios (for API calls)

## 🛠️ Development

To modify the frontend:
- Edit components in `frontend/src/components/`
- Update styles in `frontend/src/styles/`
- The app will hot-reload automatically

To modify the backend:
- Edit `backend/app.py`
- Restart the Flask server after changes (or use `restart_flask.sh`)

## 📝 Notes

- Make sure to train the model first using the Jupyter notebook
- The model files should be in `.joblib` format
- Supported file formats: CSV and Parquet
- The app expects network traffic features compatible with CSE-CIC-IDS2018 dataset format
- Backend port: `5050` (update frontend API base if needed)

## 🎨 Customization

### Change API URL
Edit `frontend/src/App.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';
```

### Modify Colors
Edit the CSS files in `frontend/src/styles/` to change the color scheme

## 📄 License

This project is for educational purposes.

