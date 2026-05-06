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

## Interfata utilizator
- **Dashboard Streamlit** cu grafice interactive pentru vizualizarea predictiilor
- Posibilitatea de a selecta valuta si perioada de analiza
- Tab cu rezultatele antrenarii si evaluarii
- Integrare **Optuna Dashboard** pentru vizualizarea studiilor de optimizare

## Backend API
- **FastAPI** cu endpoint-uri REST pentru predictii on-demand
- Endpoint-uri pentru reantrenare model la cerere
- Endpoint pentru compararea modelelor

## Pipeline si DevOps
- Automatizare rulare zilnica a scraper-ului (cron job)
- Reantrenare periodica a modelului cu date noi
- Monitorizare drift al modelului (detectie degradare performanta)
- Logging structurat si alertare la erori
