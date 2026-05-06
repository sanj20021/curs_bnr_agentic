# Plan de Optimizare Hiperparametri

## Scop
Documentarea strategiei de optimizare a hiperparametrilor pentru modelul XGBoost folosit in prognoza cursului PLN/RON.

## Context
Proiectul implementeaza un singur tip de model (XGBoost Regressor) dar il optimizeaza prin doua metode diferite pentru a compara performanta si eficienta fiecareia.

## Metoda 1: Optuna (recomandata)

### De ce Optuna?
- Cautare bayesiana eficienta - nu testeaza toate combinatiile, ci invata din trial-urile anterioare
- Pruning - poate opri devreme trial-urile care nu par promitoare
- Spatiu de cautare mai mare si mai fin decat GridSearch
- Suport nativ pentru distributii logaritmice (util pentru learning_rate)

### Configurare
- **Sampler**: TPE (Tree-structured Parzen Estimator) - implicit in Optuna
- **Directie**: minimizare (cautam MAE cat mai mic)
- **Numar trials**: 30 (compromis intre timpul de rulare si calitatea cautarii)
- **Cross-validation**: TimeSeriesSplit cu 3 folds

### Spatiu de cautare
```python
param = {
    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
    'max_depth': trial.suggest_int('max_depth', 3, 10),
    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
    'subsample': trial.suggest_float('subsample', 0.6, 1.0),
    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
}
```

## Metoda 2: GridSearchCV (clasica)

### De ce GridSearch?
- Metoda determinista - testeaza exhaustiv toate combinatiile
- Reproductibilitate garantata - acelasi grid produce mereu aceleasi rezultate
- Simplu de inteles si de explicat
- Potrivit pentru spatii mici de cautare

### Configurare
- **Estimator**: XGBRegressor cu random_state=42
- **Scoring**: neg_mean_absolute_error
- **CV**: TimeSeriesSplit cu 3 folds
- **n_jobs**: -1 (paralelizare pe toate core-urile)

### Grila de cautare
```python
param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2]
}
```

## Validare pentru serii temporale
- Folosim `TimeSeriesSplit` (sklearn) in loc de KFold clasic
- Motivatie: datele temporale nu pot fi amestecate aleator (ar cauza data leakage)
- TimeSeriesSplit respecta ordinea cronologica: fiecare fold de validare vine DUPA fold-ul de antrenare

## Comparatie asteptata
| Aspect | Optuna | GridSearchCV |
|--------|--------|-------------|
| Timp de rulare | Mai rapid (cautare inteligenta) | Mai lent (exhaustiv) |
| Spatiu cautat | Mare, continuu | Mic, discret |
| Reproductibilitate | Depinde de seed | 100% determinista |
| Calitate rezultat | Adesea mai bun | Limitat la grila |
