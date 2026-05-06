import os
from src.core.scraper import scrape_curs_bnr
from src.core.model import train_and_evaluate

def main():
    # Definim directorul rădăcină al proiectului
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "date_extrase")
    
    # Ne asigurăm că folderul restrâns pentru date există
    os.makedirs(data_dir, exist_ok=True)
    
    currency = "PLN"
    
    print("=" * 60)
    print(f"Incepe procesul automat de prognoza pentru {currency}")
    print("=" * 60)
    
    # Pasul 1: Extragerea datelor brute
    print("\n[Pasul 1/2] Extragere date BNR...")
    df_scraped = scrape_curs_bnr(currency_code=currency, output_dir=data_dir)
    
    if df_scraped is None:
        print("S-a raportat o problema la Scraping. Iesire din program.")
        return

    csv_path = os.path.join(data_dir, f"istoric_curs_{currency.lower()}.csv")
    
    # Pasul 2A: Antrenare și optimizare Optuna
    print("\n[Pasul 2/3] Optimizare model XGBoost cu Optuna...")
    metrics_optuna, test_data_optuna, preds_optuna, mod_optuna = train_and_evaluate(
        csv_path=csv_path, 
        output_dir=data_dir, 
        n_trials=30,
        method="optuna"
    )
    
    # Pasul 2B: Antrenare și optimizare GridSearchCV
    print("\n[Pasul 3/3] Optimizare model XGBoost cu GridSearchCV...")
    metrics_grid, _, preds_grid, mod_grid = train_and_evaluate(
        csv_path=csv_path, 
        output_dir=data_dir, 
        method="gridsearch"
    )
    
    print("\n" + "=" * 60)
    print("REPREZENTARE REZULTATE FINALE (OPTUNA)")
    print("=" * 60)
    print(f"Modelul Optuna a fost salvat cu succes la: {mod_optuna}")
    print(f"Eroarea Medie Absoluta (MAE): {metrics_optuna['MAE']:.6f} RON")
    print(f"Root Mean Squared Error (RMSE): {metrics_optuna['RMSE']:.6f} RON")
    print(f"Mean Absolute Percentage Error (MAPE): {metrics_optuna['MAPE']*100:.4f}%\n")
    
    print("=" * 60)
    print("REPREZENTARE REZULTATE FINALE (GRIDSEARCH)")
    print("=" * 60)
    print(f"Eroarea Medie Absoluta (MAE): {metrics_grid['MAE']:.6f} RON")
    print(f"Root Mean Squared Error (RMSE): {metrics_grid['RMSE']:.6f} RON")
    print(f"Mean Absolute Percentage Error (MAPE): {metrics_grid['MAPE']*100:.4f}%")
    
    target_col = test_data_optuna.columns[1]
    comparison_df = test_data_optuna[['Data', target_col]].copy()
    comparison_df.columns = ['Data', 'Valoare_Reala']
    comparison_df['Predictie_Optuna'] = preds_optuna
    comparison_df['Predictie_Grid'] = preds_grid
    
    print("\nEsantion din ultimele predictii pe setul de test:")
    print(comparison_df.tail(7).to_string(index=False))

if __name__ == "__main__":
    main()
