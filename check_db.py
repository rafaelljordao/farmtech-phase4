# check_db.py
import sqlite3

DB_PATH = "farmtech.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de dados dos sensores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME,
        soil_moisture REAL,
        temperature REAL,
        humidity REAL,
        ph_soil REAL,
        nutrient_level REAL,
        rainfall REAL,
        irrigation_active BOOLEAN,
        system_error BOOLEAN
    )
    ''')

    # Tabela de histórico de irrigação
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS irrigation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME,
        duration_minutes REAL,
        trigger_type TEXT,
        soil_moisture_before REAL,
        soil_moisture_after REAL,
        water_amount_ml REAL
    )
    ''')

    # Tabela de previsões
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME,
        irrigation_probability REAL,
        irrigation_score BOOLEAN,
        recommendation TEXT,
        actual_irrigation BOOLEAN
    )
    ''')

    conn.commit()
    conn.close()
    print("✔ Banco inicializado com sucesso em", DB_PATH)

if __name__ == "__main__":
    init_db()
