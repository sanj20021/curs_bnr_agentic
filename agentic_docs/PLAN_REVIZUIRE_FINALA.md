# Plan Revizuire Finală Proiect

## 1. Context și Obiective
Această revizuire adresează problemele de comunicare ale chatbot-ului ("Eroare de comunicare cu creierul AI") cauzate de lipsa sau invaliditatea cheii API. Vom implementa o modalitate sigură și prietenoasă pentru configurarea asistentului AI direct din interfața grafică. Totodată, extindem optimizarea hiperparametrilor pentru a obține o prognoză mai precisă.

## 2. Modificări Planificate

### 2.1. Backend (`src/api/server.py`)
- **Endpoint-ul `/api/chat`**: Va fi modificat pentru a accepta parametri adiționali în payload-ul JSON: `api_key` și `model_name`.
- **Logica Groq**: Dacă frontend-ul trimite o cheie API validă prin request, o vom folosi pe aceea. Dacă nu, vom face fallback la o cheie "default" setată în backend (unde vei putea pune tu cheia pentru profesor, ca aplicația să fie "plug-and-play").
- **Gestiunea Erorilor**: Vom intercepta eroarea de autentificare Groq (invalid API key) și o vom transmite clar către interfață, evitând 500 Server Error.

### 2.2. Frontend (`frontend/src/App.jsx`)
- **Buton de Setări (Settings)**: Vom adăuga o iconiță subtilă de setări (⚙️) în antetul ferestrei de chat.
- **Interfața de Configurare**: Când este apăsat butonul, chat-ul va face loc unui mic formular cu:
  - Câmp pentru introducerea `Groq API Key`.
  - Dropdown pentru selecția modelului (ex: `llama-3.3-70b-versatile`, `llama3-8b-8192`, `mixtral-8x7b-32768`).
- **Stocare Locală (LocalStorage)**: Setările vor fi salvate automat în browser, astfel încât utilizatorul (sau profesorul) să nu trebuiască să le introducă la fiecare refresh.
- Aceste date vor fi trimise către backend la fiecare mesaj.

### 2.3. Core Machine Learning (`src/core/model.py` & `src/core/pipeline.py`)
- **Creșterea Numărului de Trials**: Așa cum ai sugerat, vom mări numărul implicit de încercări de la `30` la `100` pentru Optuna.
- **Impact**: Algoritmul va explora mai adânc spațiul hiperparametrilor și va găsi o configurație superioară pentru XGBoost. Timpul de antrenare va crește (probabil de la câteva zeci de secunde la 1-2 minute), dar rezultatele vor fi net superioare pentru o aplicație de tip "Proiect Final".

## 3. Rezultat Așteptat
- **Fiabilitate**: Profesorul poate folosi chatbot-ul imediat (prin cheia ta default) dar are și "Feature-ul" avansat de a-și pune propria cheie / a alege modelul dorit direct din UI.
- **Performanță ML**: Eroare mai mică (MAE/RMSE îmbunătățite) garantată de un Hyperparameter Tuning veritabil.

---
*Proiect realizat de: Cristian Antonescu*
