# python/simple_ingest.py

import sqlite3
from datetime import datetime

def insert_reading(
    soil_moisture: float,
    temperature: float,
    humidity: float,
    ph_soil: float,
    nutrient_level: float,
    rainfall: float,
    irrigation_active: bool,
    system_error: bool,
    db_path: str = "farmtech.db"
):
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO sensor_data
        (timestamp, soil_moisture, temperature, humidity, ph_soil, nutrient_level, rainfall, irrigation_active, system_error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(sep=" "),
        soil_moisture,
        temperature,
        humidity,
        ph_soil,
        nutrient_level,
        rainfall,
        int(irrigation_active),
        int(system_error)
    ))
    conn.commit()
    conn.close()
    print("Leitura inserida com sucesso.")

if __name__ == "__main__":
    # Exemplo de uso: valores aleatórios ou fixos
    insert_reading(
        soil_moisture=42.5,
        temperature=23.1,
        humidity=55.0,
        ph_soil=6.8,
        nutrient_level=50.0,
        rainfall=0.0,
        irrigation_active=False,
        system_error=False
    )
