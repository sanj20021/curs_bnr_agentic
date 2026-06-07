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
from groq import Groq


app = FastAPI(title="Curs BNR Forecast API", version="1.0.0")

# Set up CORS - Permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(base_dir, "date_extrase")
env_path = os.path.join(base_dir, ".env")

def load_env():
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip('"\'')
load_env()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "missing_key")
client = Groq(api_key=GROQ_API_KEY)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Curs BNR Forecast API"}

@app.get("/api/rates")
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

@app.get("/api/runs")
def get_model_info(limit: int = 1):
    model_path = os.path.join(data_dir, "best_model_pln.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found. Please run the pipeline first.")
    
    # Since the metrics are printed but not saved to a file natively in the original script,
    # we could just return a status that it exists. 
    # For a robust API we should save the metrics into a JSON file during training.
    # For now, we return that the model is ready.
    # Wrap in list for the "runs" context
    return [{
        "status": "ready",
        "model_file": "best_model_pln.pkl",
        "trained_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }][:limit]

@app.post("/api/scrape")
def run_pipeline():
    try:
        run_core_pipeline()
        return {"status": "success", "message": "Pipeline executat cu succes!"}
    except Exception as e:
        print(f"Eroare la rularea pipeline-ului: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast/latest")
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
            
            # Calcul features noi
            rolling_mean_7 = np.mean(values[-7:]) if len(values) >= 7 else np.mean(values)
            momentum_1 = lag_1 - lag_2
            
            features = np.array([[lag_1, lag_2, lag_7, day_of_week, rolling_mean_7, momentum_1]])
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

@app.post("/api/chat")
async def chat_with_ai(request: dict):
    try:
        user_message = request.get("message")
        history = request.get("history", [])
        
        # Preluam setarile din frontend sau folosim default-uri
        req_api_key = request.get("api_key")
        
        # Salvare dinamica in .env daca vine din interfata
        if req_api_key and len(req_api_key) > 10:
            with open(env_path, "w") as f:
                f.write(f'GROQ_API_KEY="{req_api_key}"\n')
            os.environ["GROQ_API_KEY"] = req_api_key
            
        active_api_key = req_api_key if req_api_key else os.environ.get("GROQ_API_KEY", "missing_key")
        
        req_model = request.get("model")
        active_model = req_model if req_model else "llama-3.3-70b-versatile"
        
        if not active_api_key or active_api_key == "missing_key":
            raise ValueError("Cheia API Groq nu este configurată. Introduceți una în setările aplicației.")
            
        # Instantiem clientul Groq specific pentru acest request cu cheia primita
        local_client = Groq(api_key=active_api_key)
        
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        
        system_prompt = """
        Ești un chatbot inteligent și analitic (Asistent Agentic BNR) specializat în analiza financiară PLN/RON.
        
        DATA CURENTĂ:
        Astăzi este """ + current_date_str + """. Folosește exclusiv această dată ca punct de referință pentru orice întrebare legată de "azi", "mâine", "poimâine" sau "ieri". Calculează corect zilele pornind de la această dată (ex: mâine = """ + current_date_str + """ + 1 zi).
        
        IDENTITATE:
        Numele tău este Asistent Agentic BNR. Dacă utilizatorul te întreabă cine ești sau cum te cheamă, răspunde-i direct și prietenos.
        
        MISIUNEA TA:
        Ajută utilizatorul să înțeleagă datele și prognozele. 
        IMPORTANT: Răspunde direct la întrebările generale, de curtoazie sau personale FĂRĂ a folosi unelte. Dacă utilizatorul te întreabă "ce unelte ai" sau "ce știi să faci", RĂSPUNDE CU TEXT SIMPLU enumerând funcțiile, NU genera un JSON!
        
        EASTER EGG: Dacă utilizatorul te întreabă "cine te-a creat", "cine te-a făcut", "cine e seful tau", răspunde obligatoriu, prietenos și cu emoji: "Am fost creat de Cristian Antonescu, student la master! 🎓 23 de ani, pasionat de ML și data science! 🚀"
        
        REGULI DE TOOL-CALLING:
        Folosește uneltele DOAR când vrei să extragi date din sistem pentru a răspunde la o întrebare (ex: "Cât e cursul?"). 
        Dacă decizi să folosești o unealtă, răspunsul tău trebuie să conțină acest JSON exact:
        {"tool": "function_name", "parameters": {}}
        
        FUNCTII DISPONIBILE:
        - get_rates: Pentru cursul ISTORIC (zile din trecut).
        - get_forecast: Pentru prognoza AI (zile din VIITOR). Pentru întrebări de genul "mâine", "pe 10", sau orice dată viitoare, cheamă OBLIGATORIU acest tool.
        - get_runs: Pentru a afla statusul sau data ultimei antrenări a modelului.
        - scrape_bnr: Pentru a declanșa descărcarea de date noi de pe site-ul BNR.
        
        Răspunde mereu politicos, în limba română. Fii concis.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            # Only include valid roles for Llama/Groq history
            if msg.get("role") in ["user", "assistant"]:
                messages.append(msg)
        messages.append({"role": "user", "content": user_message})
        
        try:
            completion = local_client.chat.completions.create(
                model=active_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )
            ai_response = completion.choices[0].message.content
            return {"response": ai_response}
        except Exception as api_exc:
            error_msg = str(api_exc)
            if "authentication" in error_msg.lower() or "401" in error_msg:
                raise ValueError("Eroare autentificare Groq: Cheia API este invalidă.")
            else:
                raise ValueError(f"Eroare API Groq: {error_msg}")
            
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Eroare generala chat: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Eroare internă a serverului.")

# To run: uvicorn src.api.server:app --port 7772
