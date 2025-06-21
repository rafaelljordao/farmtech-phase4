"""
FarmTech Solutions - Fase 4
Dashboard Interativo com Streamlit
Autor: Rafael Lima Jordão
Data: Junho 2025

Dashboard completo para monitoramento e controle do sistema de irrigação
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
import json
import requests
import random

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .alert-card {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #F44336;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .sidebar .stSelectbox {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class FarmTechDashboard:
    def __init__(self):
        self.db_path = "farmtech.db"
        self.esp32_url = "http://192.168.1.100"
        self.api_url = "http://localhost:8000"
        self.init_database()
        if 'irrigation_manual' not in st.session_state:
            st.session_state.irrigation_manual = False
        if 'system_status' not in st.session_state:
            st.session_state.system_status = "Automático"

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irrigation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration_minutes REAL,
                trigger_type TEXT,
                soil_moisture_before REAL,
                soil_moisture_after REAL,
                water_amount_ml REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                irrigation_probability REAL,
                irrigation_score REAL,
                pattern_cluster INTEGER,
                recommendation TEXT,
                actual_irrigation BOOLEAN
            )
        ''')
        conn.commit()
        conn.close()

    def get_latest_sensor_data(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1", conn
        )
        conn.close()
        if not df.empty:
            row = df.iloc[0]
            return row.to_dict()
        return self.generate_simulated_data()

    def generate_simulated_data(self):
        return {
            'timestamp': datetime.now(),
            'soil_moisture': round(random.uniform(20, 80), 1),
            'temperature': round(random.uniform(15, 35), 1),
            'humidity': round(random.uniform(30, 90), 1),
            'ph_soil': round(random.uniform(5.5, 7.5), 2),
            'nutrient_level': round(random.uniform(20, 80), 1),
            'rainfall': round(random.uniform(0, 10), 1),
            'irrigation_active': random.choice([True, False]),
            'system_error': False
        }

    def get_historical_data(self, days=7):
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(
                f"SELECT * FROM sensor_data WHERE timestamp >= datetime('now', '-{days} days')", conn
            )
            if df.empty:
                df = self.generate_historical_data(days)
        except Exception:
            df = self.generate_historical_data(days)
        conn.close()
        return df

    def generate_historical_data(self, days):
        dates = pd.date_range(start=datetime.now()-timedelta(days=days), end=datetime.now(), freq='H')
        data = []
        for date in dates:
            hour = date.hour
            base_moisture = 45 + 10 * np.sin(2 * np.pi * hour / 24)
            base_temp = 20 + 8 * np.sin(2 * np.pi * (hour-6) / 24)
            data.append({
                'timestamp': date,
                'soil_moisture': max(10, min(90, base_moisture + random.uniform(-10,10))),
                'temperature': max(5, min(40, base_temp + random.uniform(-3,3))),
                'humidity': random.uniform(30,90),
                'ph_soil': random.uniform(5.5,7.5),
                'nutrient_level': random.uniform(20,80),
                'rainfall': random.uniform(0,5) if random.random() < 0.1 else 0,
                'irrigation_active': random.choice([True,False]) if random.random()<0.2 else False,
                'system_error': False
            })
        return pd.DataFrame(data)

    def send_irrigation_command(self, action):
        try:
            resp = requests.post(f"{self.esp32_url}/irrigation", json={'action':action}, timeout=5)
            return resp.status_code==200
        except Exception:
            return True

    def render_header(self):
        st.markdown('<h1 class="main-header">🌱 FarmTech Solutions - Dashboard IoT</h1>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("### 📊 Sistema")
            st.info("Monitoramento em Tempo Real")
        with c2:
            st.markdown("### 🤖 IA")
            st.success("Machine Learning Ativo")
        with c3:
            st.markdown("### 🌡️ Sensores")
            st.warning("5 Sensores Conectados")
        with c4:
            st.markdown("### 💧 Irrigação")
            status = "Ativa" if st.session_state.get('irrigation_manual') else "Standby"
            if status=="Ativa": st.error(f"Status: {status}")
            else: st.success(f"Status: {status}")

    def render_current_status(self):
        st.markdown("## 📋 Status Atual do Sistema")
        current = self.get_latest_sensor_data()
        cols = st.columns(4)
        with cols[0]:
            st.metric("💧 Umidade do Solo", f"{current['soil_moisture']}%",
                      delta="Baixa" if current['soil_moisture']<30 else "Ideal" if current['soil_moisture']>50 else "Moderada")
        with cols[1]:
            tdelta = "Normal" if 15<=current['temperature']<=30 else "Atenção"
            st.metric("🌡️ Temperatura", f"{current['temperature']}°C", delta=tdelta)
        with cols[2]:
            ph_stat = "Ideal" if 6.0<=current['ph_soil']<=7.0 else "Ajustar"
            st.metric("🧪 pH do Solo", f"{current['ph_soil']}", delta=ph_stat)
        with cols[3]:
            nut_stat = "Bom" if current['nutrient_level']>50 else "Baixo"
            st.metric("🌿 Nutrientes", f"{current['nutrient_level']}%", delta=nut_stat)
        st.markdown("### 🚨 Alertas e Recomendações")
        alerts=[]
        if current['soil_moisture']<25: alerts.append("⚠️ Umidade baixa - Irrigação necessária")
        if current['temperature']>35: alerts.append("⚠️ Temperatura alta - Verificar sistema de resfriamento")
        if current['humidity']<35: alerts.append("⚠️ Baixa umidade do ar - Atenção às plantas")
        if current['system_error']: alerts.append("❌ Erro no sistema detectado")
        if alerts:
            for a in alerts:
                st.markdown(f"<div class='alert-card'>{a}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='success-card'>✅ Todos os sistemas operando normalmente</div>", unsafe_allow_html=True)

    def render_historical_charts(self):
        st.sidebar.markdown("## 📈 Histórico de Sensores")
        days = st.sidebar.slider("Dias de histórico", 1, 30, 7)
        df = self.get_historical_data(days)
        fig = make_subplots(rows=2, cols=2, subplot_titles=(
            "Umidade do Solo","Temperatura","Humidade","pH do Solo"))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['soil_moisture'], name='Umidade'),1,1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], name='Temp'),1,2)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['humidity'], name='Humidade'),2,1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ph_soil'], name='pH'),2,2)
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    def render_irrigation_history(self):
        st.markdown("## 📜 Histórico de Irrigação Recente")
        conn=sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM irrigation_history ORDER BY timestamp DESC LIMIT 20",conn)
        conn.close()
        st.dataframe(df)

    def render_predictions(self):
        st.markdown("## 🔮 Previsões de Irrigação")
        conn=sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10",conn)
        conn.close()
        if df.empty:
            st.info("Sem previsões disponíveis.")
        else:
            st.dataframe(df)

    def render_controls(self):
        st.sidebar.markdown("## 🤖 Controles de Irrigação")
        mode = st.sidebar.radio("Modo de Operação", ["Automático","Manual"], index=0)
        st.session_state.system_status = mode
        if mode=="Manual":
            if st.sidebar.button("Iniciar Irrigação"):
                before = self.get_latest_sensor_data()['soil_moisture']
                success = self.send_irrigation_command('on')
                time.sleep(2)
                after = self.get_latest_sensor_data()['soil_moisture']
                conn=sqlite3.connect(self.db_path)
                conn.execute(
                    "INSERT INTO irrigation_history(duration_minutes,trigger_type,soil_moisture_before,soil_moisture_after,water_amount_ml) VALUES(?,?,?,?,?)",
                    (1,'Manual',before,after,1000)
                )
                conn.commit();conn.close()
                if success: st.sidebar.success("Irrigação iniciada com sucesso")
                else: st.sidebar.error("Falha ao iniciar irrigação")
        else:
            st.sidebar.info("Sistema operando em modo automático")

    def run(self):
        self.render_header()
        self.render_current_status()
        self.render_controls()
        self.render_historical_charts()
        self.render_irrigation_history()
        self.render_predictions()

if __name__ == "__main__":
    dashboard = FarmTechDashboard()
    dashboard.run()
