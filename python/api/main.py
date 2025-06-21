import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import joblib

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("farmtech_api")

# Define diretório base (raiz do projeto)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'farmtech.db')
MODEL_PATH = os.path.join(BASE_DIR, 'python', 'models', 'model.pkl')

# Payload esperado
class SensorData(BaseModel):
    soil_moisture: float
    temperature: float
    humidity: float
    ph_soil: float
    nutrient_level: float
    rainfall: float
    irrigation_active: bool
    system_error: bool

# Cria API
app = FastAPI(title="FarmTech API")

# Carrega modelo preditivo
try:
    MODEL = joblib.load(MODEL_PATH)
    logger.info(f"Modelo carregado de {MODEL_PATH}")
except Exception as e:
    MODEL = None
    logger.error(f"Falha ao carregar modelo: {e}")


def get_db():
    """
    Abre conexão SQLite com o arquivo farmtech.db na raiz do projeto.
    """
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@app.on_event("startup")
def startup_event():
    """
    Garante criação das tabelas no banco antes do primeiro request.
    """
    from check_db import init_db
    init_db()
    logger.info(f"Banco inicializado em {DB_PATH}")

@app.get("/", response_class=JSONResponse)
def root():
    """Rota raiz para verificação rápida"""
    return {"message": "FarmTech API está rodando", "endpoints": ["/health", "/sensor-data/", "/predict/"]}

@app.post("/sensor-data/", response_class=JSONResponse)
def receive_sensor(data: SensorData):
    """
    Recebe dados de sensores, insere na tabela sensor_data e retorna status.
    """
    logger.info(f"Dados recebidos: {data.json()}")
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO sensor_data
            (timestamp, soil_moisture, temperature, humidity, ph_soil, nutrient_level, rainfall, irrigation_active, system_error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow(),
                data.soil_moisture,
                data.temperature,
                data.humidity,
                data.ph_soil,
                data.nutrient_level,
                data.rainfall,
                int(data.irrigation_active),
                int(data.system_error),
            )
        )
        conn.commit()
        logger.info("Inserção em sensor_data bem-sucedida")
    except Exception as e:
        logger.error(f"Erro ao inserir sensor_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"status": "ok"}

@app.get("/predict/", response_class=JSONResponse)
def predict_irrigation():
    """
    Gera predição de irrigação com base no último dado, registra em predictions e retorna resultado.
    """
    if MODEL is None:
        logger.error("Modelo não carregado na predição.")
        raise HTTPException(status_code=500, detail="Modelo não carregado")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT soil_moisture, temperature, humidity, ph_soil, nutrient_level '
        'FROM sensor_data ORDER BY timestamp DESC LIMIT 1'
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        logger.warning("Nenhum dado de sensor disponível para predição.")
        raise HTTPException(status_code=404, detail="Nenhum dado de sensor disponível")

    features = list(row)
    prob = float(MODEL.predict_proba([features])[0][1])
    decision = bool(MODEL.predict([features])[0])
    recommendation = 'Ligar bomba' if decision else 'Desligar bomba'
    logger.info(f"Predição gerada: prob={prob}, decision={decision}")

    conn = get_db()
    conn.execute(
        "INSERT INTO predictions"
        "(timestamp, irrigation_probability, irrigation_score, recommendation, actual_irrigation)"
        " VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow(), prob, int(decision), recommendation, None)
    )
    conn.commit()
    conn.close()
    logger.info("Registro de predição inserido em predictions")

    return {"probability": prob, "decision": decision, "recommendation": recommendation}

@app.get("/health", response_class=JSONResponse)
def health_check():
    """
    Endpoint de saúde para verificar se a API está ativa.
    """
    return {"status": "alive"}