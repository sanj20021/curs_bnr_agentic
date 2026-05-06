# Plan de Antrenare si Optimizare Model XGBoost

## Obiectiv
Dezvoltarea unui model de tip XGBoost Regressor capabil sa prezica cursul de schimb PLN/RON pentru ziua urmatoare, bazat pe date istorice extrase de la BNR.

## Date de intrare
- Fisier CSV cu coloanele: `Data`, `PLN` (cursul valutar)
- Perioada acoperita: din 01/01/2020 pana in prezent
- Sursa: BNR via cursbnr.ro (scraping automat)

## Preprocesare date
1. **Conversie data** - coloana `Data` este convertita din format `DD.MM.YYYY` in datetime
2. **Sortare cronologica** - datele sunt ordonate crescator dupa data
3. **Eliminare valori lipsa** - randurile cu date invalide sunt eliminate

## Feature Engineering
Am creat urmatoarele variabile predictive:
- **Lag_1** - cursul din ziua precedenta (t-1)
- **Lag_2** - cursul de acum 2 zile (t-2)
- **Lag_7** - cursul de acum 7 zile (t-7) - pentru captarea pattern-urilor saptamanale
- **DayOfWeek** - ziua saptamanii (0=Luni, 4=Vineri) - variabila temporala

## Split date
- **Training set** - toate datele cu exceptia ultimelor 14 zile
- **Test set** - ultimele 14 intrari (zile) - set de test "orb" pentru evaluare finala

## Doua variante de optimizare

### Varianta 1: Optuna (cautare bayesiana)
- **Metoda**: Cautare inteligenta a spatiului de hiperparametri folosind Tree-structured Parzen Estimator (TPE)
- **Numar trials**: 30 (configurabil)
- **Validare**: TimeSeriesSplit cu 3 split-uri (walk-forward validation)
- **Metrica de optimizare**: MAE (Mean Absolute Error)
- **Hiperparametri cautati**:
  - `n_estimators`: 50 - 300
  - `max_depth`: 3 - 10
  - `learning_rate`: 0.01 - 0.3 (scala logaritmica)
  - `subsample`: 0.6 - 1.0
  - `colsample_bytree`: 0.6 - 1.0

### Varianta 2: GridSearchCV (cautare exhaustiva)
- **Metoda**: Cautare exhaustiva clasica prin toate combinatiile posibile din grila predefinita
- **Validare**: TimeSeriesSplit cu 3 split-uri
- **Metrica de optimizare**: neg_mean_absolute_error (MAE negativ, deoarece GridSearch maximizeaza scorul)
- **Grila de hiperparametri**:
  - `n_estimators`: [50, 100, 150]
  - `max_depth`: [3, 5, 7]
  - `learning_rate`: [0.01, 0.1, 0.2]
- **Total combinatii**: 3 x 3 x 3 = 27 configuratii

## Metrici de evaluare
- **MAE** (Mean Absolute Error) - eroarea medie absoluta in RON
- **RMSE** (Root Mean Squared Error) - penalizeaza erorile mari
- **MAPE** (Mean Absolute Percentage Error) - eroarea relativa procentuala

## Salvare model
- Modelul final este salvat cu `joblib` in fisierul `date_extrase/best_model_pln.pkl`
- Poate fi reincarcat oricand pentru predictii noi fara reantrenare

## Comparatie finala
- Pipeline-ul ruleaza ambele variante secvential
- Afiseaza un tabel comparativ cu metricile ambelor modele
- Prezinta un esantion din ultimele 7 predictii vs. valori reale
