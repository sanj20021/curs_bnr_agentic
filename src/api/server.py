from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import joblib

app = FastAPI(title="Curs BNR Forecast API", version="1.0.0")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
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
    
    # Sort by date
    df = df.sort_values(by="Data").reset_index(drop=True)
    
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

# To run: uvicorn src.api.server:app --reload
