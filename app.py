import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from numba import njit

# =========================================================
# 1. DEFINISI ULANG FUNGSI NUMBA (WAJIB ADA)
# =========================================================
# Harus PERSIS sama dengan yang ada di Notebook saat training
@njit
def rolling_mean(x, window_size):
    n = len(x)
    out = np.empty(n)
    out[:] = np.nan
    for i in range(window_size, n):
        out[i] = np.mean(x[i-window_size:i])
    return out

@njit
def rolling_max(x, window_size):
    n = len(x)
    out = np.empty(n)
    out[:] = np.nan
    for i in range(window_size, n):
        out[i] = np.max(x[i-window_size:i])
    return out

@njit
def rolling_std(x, window_size):
    n = len(x)
    out = np.empty(n)
    out[:] = np.nan
    for i in range(window_size, n):
        out[i] = np.std(x[i-window_size:i])
    return out

# =========================================================
# 2. SETUP HALAMAN & LOAD DATA
# =========================================================
st.set_page_config(page_title="PGCB Power Forecasting", layout="wide")

st.title("⚡ PGCB Power Demand Forecasting")
st.markdown("Aplikasi prediksi beban listrik menggunakan Machine Learning (XGBoost/LGBM) dengan Feature Engineering.")

# Load Model & Data (Cached agar cepat)
@st.cache_resource
def load_resources():
    # Load model
    model = joblib.load('forecasting_model.pkl')
    # Load data
    data = pd.read_csv('cleaned_data.csv')
    data['datetime'] = pd.to_datetime(data['datetime'])
    return model, data

try:
    mlf, df = load_resources()
    st.success("✅ Model & Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# =========================================================
# 3. INTERFACE PREDIKSI
# =========================================================
st.sidebar.header("Konfigurasi Forecast")
days_to_predict = st.sidebar.slider("Jumlah Hari Prediksi:", min_value=7, max_value=90, value=30)

if st.sidebar.button("Mulai Prediksi"):
    with st.spinner('Sedang melakukan forecasting...'):
        # Lakukan prediksi
        # MLForecast otomatis menangani lag features & rolling window secara rekursif
        forecasts = mlf.predict(h=days_to_predict)
        
        # Tampilkan Hasil
        st.subheader(f"📊 Hasil Prediksi {days_to_predict} Hari Ke Depan")
        
        # Plotting dengan Plotly Interactive
        fig = go.Figure()

        # Plot Data Historis (Ambil 90 hari terakhir saja agar grafik tidak berat)
        last_history = df.tail(90)
        fig.add_trace(go.Scatter(
            x=last_history['datetime'], 
            y=last_history['demand_mw'],
            mode='lines',
            name='Actual (History)',
            line=dict(color='black')
        ))

        # Plot Prediksi (XGBoost/LGBM)
        # Cari kolom prediksi (biasanya nama model, misal 'XGB_Paper' atau 'LGBM_Paper')
        pred_cols = [c for c in forecasts.columns if c != 'ds']
        
        colors = ['red', 'blue', 'green']
        for i, col in enumerate(pred_cols):
            fig.add_trace(go.Scatter(
                x=forecasts['ds'], 
                y=forecasts[col],
                mode='lines',
                name=f'Forecast ({col})',
                line=dict(dash='dash', color=colors[i % len(colors)])
            ))

        fig.update_layout(
            title="Forecast vs History",
            xaxis_title="Tanggal",
            yaxis_title="Beban Listrik (MW)",
            template="plotly_white",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Tampilkan Tabel Data
        st.subheader("📋 Data Tabel Prediksi")
        st.dataframe(forecasts)