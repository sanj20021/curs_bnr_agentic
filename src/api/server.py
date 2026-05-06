from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import joblib
import traceback
import json
from datetime import datetime, timedelta
from src.core.pipeline import main as run_core_pipeline
from src.core.scraper import scrape_curs_bnr

app = FastAPI(title="Curs BNR Forecast API", version="1.0.0")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(base_dir, "date_extrase")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Curs BNR Forecast API"}

@app.get("/api/data")
def get_historical_data():
    csv_path = os.path.join(data_dir, "istoric_curs_pln.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Data file not found. Please run the scraper first.")
    
    df = pd.read_csv(csv_path)
    # Convert dates to ISO format string for easier JSON serialization
    df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
    
    df = df.sort_values(by="Data").reset_index(drop=True)
    
    # Drop NaN values to avoid JSON serialization errors
    df = df.dropna()
    
    # Return as list of dicts
    records = df.to_dict(orient="records")
    return {"data": records}

@app.get("/api/model/info")
def get_model_info():
    model_path = os.path.join(data_dir, "best_model_pln.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found. Please run the pipeline first.")
    
    # Since the metrics are printed but not saved to a file natively in the original script,
    # we could just return a status that it exists. 
    # For a robust API we should save the metrics into a JSON file during training.
    # For now, we return that the model is ready.
    return {
        "status": "ready",
        "model_file": "best_model_pln.pkl"
    }

@app.post("/api/run-pipeline")
def run_pipeline():
    try:
        run_core_pipeline()
        return {"status": "success", "message": "Pipeline executat cu succes!"}
    except Exception as e:
        print(f"Eroare la rularea pipeline-ului: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predict")
def get_predictions():
    """Generates real 7-day predictions using the trained XGBoost model."""
    model_path = os.path.join(data_dir, "best_model_pln.pkl")
    csv_path = os.path.join(data_dir, "istoric_curs_pln.csv")
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Modelul nu a fost antrenat. Rulați pipeline-ul mai întâi.")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Datele istorice nu au fost găsite.")
    
    try:
        model = joblib.load(model_path)
        
        df = pd.read_csv(csv_path)
        df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y', errors='coerce')
        df = df.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)
        
        target_col = df.columns[1]
        values = df[target_col].values.tolist()
        last_date = df['Data'].iloc[-1]
        
        predictions = []
        pred_date = last_date
        
        for i in range(7):
            pred_date = pred_date + timedelta(days=1)
            # Skip weekends (BNR doesn't publish on Sat/Sun)
            while pred_date.weekday() >= 5:
                pred_date = pred_date + timedelta(days=1)
            
            lag_1 = values[-1]
            lag_2 = values[-2]
            lag_7 = values[-7] if len(values) >= 7 else values[0]
            day_of_week = pred_date.weekday()
            
            features = np.array([[lag_1, lag_2, lag_7, day_of_week]])
            pred_value = float(model.predict(features)[0])
            
            values.append(pred_value)
            
            predictions.append({
                "Data": pred_date.strftime('%Y-%m-%d'),
                "Predictie": round(pred_value, 4)
            })
        
        return {"predictions": predictions}
    except Exception as e:
        print(f"Eroare la generarea predicțiilor: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# To run: uvicorn src.api.server:app --reload
