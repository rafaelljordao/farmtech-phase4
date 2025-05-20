import numpy as np
import pandas as pd

from src.data_processing     import load_and_clean, prepare_profile
from src.feature_engineering import prepare_features
from src.modeling            import train_all_models
from src.visualization       import (
    plot_distributions,
    plot_correlation,
    plot_profile,
    plot_model_comparison
)

def main():
    # fixa semente global para consistência
    np.random.seed(42)

    # 1) Carrega e limpa
    df = load_and_clean("data/fertilizer_prediction.csv")

    # 2) EDA / gráficos iniciais
    plot_distributions(df)
    plot_correlation(df)

    # 3) Perfil ideal
    profile_df = prepare_profile(df)
    plot_profile(profile_df)

    # 4) Feature‐engineering e split
    X_train, X_test, y_train, y_test = prepare_features(df)

    # 5) Treina e avalia
    results = train_all_models(X_train, y_train, X_test, y_test)

    # 6) Gráfico comparativo e relatório final
    plot_model_comparison(results)
    print("\n=== Resultados finais de acurácia ===")
    for name, acc in results.items():
        print(f"{name}: {acc:.2%}")

if __name__ == "__main__":
    main()
