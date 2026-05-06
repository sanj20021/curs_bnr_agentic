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
├── plan_implementare.md   # Documentația planului de implementare
├── requirements.txt       # Dependențe Python
├── date_extrase/
│   ├── istoric_curs_pln.csv   # Datele istorice extrase
│   └── best_model_pln.pkl     # Modelul antrenat (generat automat)
└── README.md              # Acest fișier
```

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
**Tema 3** - Curs AIE, 2025
