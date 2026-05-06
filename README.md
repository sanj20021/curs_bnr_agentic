# Prognoza Cursului Valutar PLN/RON - Optimizare XGBoost

Aplicație de predicție a cursului valutar PLN (Zlotul Polonez) față de RON, bazată pe date istorice extrase de pe site-ul BNR. Proiectul implementează un model **XGBoost Regressor** optimizat prin două metode diferite: **Optuna** și **GridSearchCV**.

## 🧠 Funcționalități

- **Web Scraping automat** - extrage istoricul cursului PLN/RON de pe [cursbnr.ro](https://www.cursbnr.ro/curs-valutar-bnr) folosind Playwright
- **Feature Engineering** - generare automată de lag features (t-1, t-2, t-7) și variabile temporale (ziua săptămânii)
- **Optimizare Optuna** - căutare inteligentă a hiperparametrilor cu Time Series Cross-Validation
- **Optimizare GridSearchCV** - căutare exhaustivă clasică pentru comparație
- **Evaluare comparativă** - metrici MAE, RMSE, MAPE pe un test set de 14 zile

## 📂 Structura Proiectului

```
├── main.py                # Orchestrator - rulează pipeline-ul complet
├── scraper.py             # Extragere date BNR via Playwright
├── model.py               # Antrenare XGBoost + optimizare Optuna/GridSearch
├── plan_implementare.md   ## Arhitectură
Proiectul a fost refactorizat într-o aplicație Full-Stack modernă:
- **Backend (FastAPI)**: Servește datele istorice și expune informațiile modelului XGBoost.
- **Frontend (Vite + React JSX)**: Un dashboard modern, glassmorphism, pentru vizualizarea interactivă a predicțiilor.
- **Core (Python)**: Scripturile originale de scraping și machine learning optimizate.

## Dependențe Principale
- `playwright` pentru web scraping (necesită instalare browser).
- `xgboost` & `optuna` & `scikit-learn` pentru modelare.
- `fastapi` & `uvicorn` pentru backend.
- `react` & `recharts` pentru frontend.

## Instalare & Rulare

### 1. Setare Backend (Python)
Creați și activați un mediu virtual:
```bash
python -m venv venv
venv\Scripts\activate
```

Instalați dependențele Python și browserul pentru Playwright:
```bash
pip install -r requirements.txt
playwright install chromium
```

Pentru a extrage datele și a antrena modelul (dacă e prima dată):
```bash
python src/core/pipeline.py
```

Pentru a porni serverul API:
```bash
python -m uvicorn src.api.server:app --port 8000 --reload
```

### 2. Setare Frontend (React)
Deschideți un terminal nou în folderul `frontend/`:
```bash
cd frontend
npm install
npm run dev
```

Aplicația va fi disponibilă la `http://localhost:5173`.

## 🚀 Ghid de Rulare

### 1. Instalare dependențe
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Rulare pipeline complet
```bash
python main.py
```

Aceasta va:
1. Extrage datele istorice PLN de pe BNR (scraping)
2. Antrena și optimiza modelul XGBoost cu Optuna (30 trials)
3. Antrena și optimiza modelul XGBoost cu GridSearchCV
4. Afișa comparația metricilor și un eșantion din predicții

## 📊 Metrici Evaluate

| Metrică | Descriere |
|---------|-----------|
| **MAE** | Eroarea Medie Absolută (în RON) |
| **RMSE** | Root Mean Squared Error (în RON) |
| **MAPE** | Mean Absolute Percentage Error (%) |

## ⚙️ Tehnologii Utilizate

- **Python 3.10+**
- **Playwright** - web scraping headless
- **XGBoost** - gradient boosting regressor
- **Optuna** - optimizare bayesiană a hiperparametrilor
- **Scikit-learn** - GridSearchCV, TimeSeriesSplit, metrici
- **Pandas / NumPy** - procesare date

---

**Autor:** Antonescu Cristian Mihail  
**Tema 3** - Curs AIE, 2026
