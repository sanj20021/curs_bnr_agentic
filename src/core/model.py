import pandas as pd
import numpy as np
import xgboost as xgb
import optuna
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import joblib
import os
import warnings

# Ignorăm warning-urile uzuale Optuna pentru afișare mai curată
optuna.logging.set_verbosity(optuna.logging.WARNING)
warnings.filterwarnings('ignore')

def prepare_data(csv_path):
    """
    Încarcă fișierul CSV și aplică transformările de bază:
    - Sortare cronologică.
    - Creare features (lag-uri pentru 1zi, 2zile, 7zile).
    - Eliminarea rândurilor cu valori lipsă.
    """
    df = pd.read_csv(csv_path)
    
    # Coloana Data (ex. "03.01.2020") este convertită în format datetime
    df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y', errors='coerce')
    df = df.dropna(subset=['Data'])
    df = df.sort_values('Data').reset_index(drop=True)
    
    # Presupunem că valoarea cursului se află în coloana 1 (index 1), sau cautăm dup numele monedei
    # Deoarece scraped array are forma: Data | PLN (sau alt curs) | ...
    # Vom lua coloana a doua ca fiind cursul vizat
    target_col = df.columns[1]
    
    # Feature Engineering (crearea de variabile regresive din istoric)
    df['Lag_1'] = df[target_col].shift(1)
    df['Lag_2'] = df[target_col].shift(2)
    df['Lag_7'] = df[target_col].shift(7)
    
    # Extragem ziua saptamanii ca feature (ex. luni=0, ..., vineri=4)
    df['DayOfWeek'] = df['Data'].dt.dayofweek
    
    # Adaugam features noi pentru a preveni "flat forecast" pe random walk
    df['Rolling_Mean_7'] = df['Lag_1'].rolling(window=7).mean()
    df['Momentum_1'] = df['Lag_1'] - df['Lag_2']
    
    df = df.dropna()
    
    return df, target_col

def optimize_hyperparameters(X, y, n_trials=100):
    """
    Lansează optuna pentru a căuta hiperparametrii optimi folosind TimeSeriesSplit.
    """
    def objective(trial):
        param = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'random_state': 42
        }
        
        tscv = TimeSeriesSplit(n_splits=3)
        mae_scores = []
        
        for train_index, val_index in tscv.split(X):
            X_tr, X_val = X.iloc[train_index], X.iloc[val_index]
            y_tr, y_val = y.iloc[train_index], y.iloc[val_index]
            
            model = xgb.XGBRegressor(**param)
            model.fit(X_tr, y_tr, verbose=False)
            
            preds = model.predict(X_val)
            mae = mean_absolute_error(y_val, preds)
            mae_scores.append(mae)
            
        return np.mean(mae_scores)

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    
    return study.best_params

def optimize_hyperparameters_gridsearch(X, y):
    """
    Lanseaza o optimizare clasica folosind GridSearchCV cu TimeSeriesSplit.
    """
    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2]
    }
    
    tscv = TimeSeriesSplit(n_splits=3)
    model = xgb.XGBRegressor(random_state=42)
    
    # Folosim neg_mean_absolute_error deoarece GridSearch cauta sa maximizeze scorul
    grid = GridSearchCV(estimator=model, param_grid=param_grid, 
                        scoring='neg_mean_absolute_error', cv=tscv, n_jobs=-1, verbose=0)
    
    grid.fit(X, y)
    return grid.best_params_

def train_and_evaluate(csv_path, output_dir=".", n_trials=100, method="optuna"):
    """
    Fluxul complet: extrage setul train/test, optimizează, antrenează modelul final și expune metricile.
    14 zile sunt reținute pentru setul de test.
    """
    df, target_col = prepare_data(csv_path)
    
    features = ['Lag_1', 'Lag_2', 'Lag_7', 'DayOfWeek', 'Rolling_Mean_7', 'Momentum_1']
    
    # Reținem ultimele 14 intrări (zile) ca test set orb
    test_size = 14
    train_df = df.iloc[:-test_size]
    test_df = df.iloc[-test_size:]
    
    X_train = train_df[features]
    y_train = train_df[target_col]
    X_test = test_df[features]
    y_test = test_df[target_col]
    
    if method == "optuna":
        print(f"Rulare Optuna cu {n_trials} trials...")
        best_params = optimize_hyperparameters(X_train, y_train, n_trials=n_trials)
    else:
        print("Rulare cautare GridSearch (GridSearchCV)...")
        best_params = optimize_hyperparameters_gridsearch(X_train, y_train)
        
    print("Parametrii cei mai buni gasiti:", best_params)
    
    # Antrenarea finală pe tot training set-ul cu parametrii optimizați
    best_model = xgb.XGBRegressor(**best_params, random_state=42)
    best_model.fit(X_train, y_train)
    
    # Evaluarea pe test set-ul de 14 zile
    preds = best_model.predict(X_test)
    
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mape = mean_absolute_percentage_error(y_test, preds)
    
    # Salvarea modelului sub formă de fișier gata de reluat oricând
    model_filename = os.path.join(output_dir, "best_model_pln.pkl")
    joblib.dump(best_model, model_filename)
    
    metrics = {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape
    }
    
    return metrics, test_df, preds, model_filename

if __name__ == "__main__":
    pass
