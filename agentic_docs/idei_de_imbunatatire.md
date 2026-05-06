# Idei de Imbunatatire

## Modele aditionale
- Adaugarea unui model **SARIMA** pentru componente autoregresive si sezoniere
- Adaugarea modelului **Prophet** (Meta) pentru captarea trendurilor si sezonalitatilor multiple
- Testarea unui model **LSTM** (retea neuronala recurenta) pentru serii temporale complexe
- Implementarea unui **ensemble model** - medie ponderata a predictiilor celor mai bune modele

## Feature engineering extins
- Adaugarea de **rolling statistics** - medie mobila si deviatie standard pe ferestre de 3, 7, 14 zile
- Adaugarea de **expanding mean** - media cumulativa
- Indicatori de **volatilitate** - rolling volatility
- **Indicatori sezonieri** - sin/cos pentru componente anuale/saptamanale
- Indicator de **zi lucratoare vs. weekend**

## Date externe ca features
- Istoric **dobanda de referinta BNR**
- Istoric **rata inflatiei** (Romania si Polonia)
- Curs **EUR/RON** si **EUR/PLN** ca features aditionale
- Indici bursieri relevanti (BET, WIG20)

## Implementate (Finalizate cu Succes)
- **Dashboard Web (Vite + React JSX)** cu grafice interactive, Dark Mode, glassmorphism.
- Funcționalitate de **"Run Pipeline" (Refresh & Reantrenare)** direct din interfață.
- **Backend API (FastAPI)** care expune datele și primește trigger-ul de reantrenare.

## Idei pentru Viitor (DevOps)
- Automatizare rulare zilnică a scraper-ului (cron job) - momentan se face manual via UI.
- Monitorizare drift al modelului (detecție degradare performanță)
- Logging structurat și alertare la erori
