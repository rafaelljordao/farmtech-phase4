import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Caminhos absolutos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'farmtech.db')
MODEL_PATH = os.path.join(BASE_DIR, 'python', 'models', 'model.pkl')

# Parâmetros de simulação
SYNTHETIC_SAMPLES = 1000
MOISTURE_THRESHOLD = 30.0

def generate_synthetic_data(n_samples=SYNTHETIC_SAMPLES) -> pd.DataFrame:
    """
    Gera dados sintéticos quando não há registros reais:
    - soil_moisture: uniforme 20-80
    - temperature: uniforme 15-35
    - humidity: uniforme 30-90
    - ph_soil: uniforme 5.5-7.5
    - nutrient_level: uniforme 20-80
    - irrigation_active: True se soil_moisture < MOISTURE_THRESHOLD
    """
    rng = np.random.default_rng(seed=42)
    data = {
        'soil_moisture': rng.uniform(20, 80, n_samples),
        'temperature':   rng.uniform(15, 35, n_samples),
        'humidity':      rng.uniform(30, 90, n_samples),
        'ph_soil':       rng.uniform(5.5, 7.5, n_samples),
        'nutrient_level':rng.uniform(20, 80, n_samples)
    }
    df = pd.DataFrame(data)
    df['irrigation_active'] = df['soil_moisture'] < MOISTURE_THRESHOLD
    return df

if __name__ == '__main__':
    print("=== Treinamento de Modelo Irrigation ===")
    print(f"Usando Banco: {DB_PATH}")
    print(f"Modelo será salvo em: {MODEL_PATH}")

    # 1) Carrega dados
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        'SELECT soil_moisture, temperature, humidity, ph_soil, nutrient_level, irrigation_active FROM sensor_data',
        conn
    )
    conn.close()

    # 2) Se não há dados, gera sintéticos
    if df.empty:
        print("Nenhum dado real encontrado: gerando dados sintéticos...")
        df = generate_synthetic_data()

    df.dropna(inplace=True)
    X = df[['soil_moisture','temperature','humidity','ph_soil','nutrient_level']]
    y = df['irrigation_active']

    # 3) Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Treinando com {len(X_train)} amostras e testando com {len(X_test)}...")

    # 4) Treino
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 5) Avaliação
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Acurácia no teste: {acc*100:.2f}%")

    # 6) Salva modelo
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("Modelo salvo com sucesso.")

def predict(features: dict) -> dict:
    """
    Carrega o modelo salvo e retorna probabilidade e decisão de irrigação.
    Espera as chaves: soil_moisture, temperature, humidity, ph_soil, nutrient_level.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modelo não encontrado em {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    X = pd.DataFrame([features])
    prob = float(model.predict_proba(X)[0][1])
    decision = bool(model.predict(X)[0])
    return {'probability': prob, 'decision': decision}
