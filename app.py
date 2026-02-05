import os
# =========================================================
# 1. FIX CRASH NUMBA (WAJIB DI PALING ATAS)
# =========================================================
# Mematikan kompilasi Numba agar kompatibel dengan Python 3.13 di Streamlit Cloud
os.environ["NUMBA_DISABLE_JIT"] = "1"

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from datetime import timedelta

# =========================================================
# 2. DEFINISI ULANG FUNGSI (WAJIB ADA)
# =========================================================
# Kita gunakan fungsi Python biasa (tanpa @njit) atau dummy decorator
# karena kita sudah set NUMBA_DISABLE_JIT = 1

def rolling_mean(x, window_size):
    n = len(x)
    out = np.empty(n)
    out[:] = np.nan
    for i in range(window_size, n):
        out[i] = np.mean(x[i-window_size:i])
    return out

def rolling_max(x, window_size):
    n = len(x)
    out = np.empty(n)
    out[:] = np.nan
    for i in range(window_size, n):
        out[i] = np.max(x[i-window_size:i])
    return out

def rolling_std(x, window_size):
    n = len(x)
    out = np.empty(n)
    out[:] = np.nan
    for i in range(window_size, n):
        out[i] = np.std(x[i-window_size:i])
    return out

# =========================================================
# 3. SETUP & LOAD DATA
# =========================================================
st.set_page_config(page_title="PGCB Forecasting Dashboard", layout="wide")

st.title("⚡ Dashboard Prediksi Beban Listrik PGCB")
st.markdown("""
Aplikasi ini memprediksi beban listrik menggunakan Machine Learning.
Silakan pilih model dan tanggal target untuk melihat analisisnya.
""")

@st.cache_resource
def load_resources():
    try:
        # Load model & data
        model = joblib.load('forecasting_model.pkl')
        data = pd.read_csv('cleaned_data.csv')
        data['datetime'] = pd.to_datetime(data['datetime'])
        return model, data
    except Exception as e:
        return None, str(e)

mlf, df_raw = load_resources()

# Error Handling jika file tidak ketemu/rusak
if isinstance(df_raw, str): # Jika return-nya string error
    st.error(f"Terjadi kesalahan saat memuat model: {df_raw}")
    st.warning("Tips: Pastikan file 'forecasting_model.pkl' dan 'cleaned_data.csv' ada di folder yang sama.")
    st.stop()

df = df_raw.copy()
last_available_date = df['datetime'].max().date()

# =========================================================
# 4. SIDEBAR KONTROL
# =========================================================
st.sidebar.header("⚙️ Konfigurasi")

# Pilihan Model (Mendeteksi kolom model yang tersedia di MLForecast)
# Biasanya nama modelnya 'XGB_Paper', 'LGBM_Paper', dll.
try:
    # Mengambil nama model dari object MLForecast jika mungkin, 
    # atau hardcode jika kita tahu nama modelnya dari notebook training
    available_models = list(mlf.models_.keys()) 
except:
    # Fallback jika struktur berbeda
    available_models = ['XGB_Paper', 'LGBM_Paper'] 

selected_model = st.sidebar.selectbox("Pilih Model:", available_models)

# Pilihan Tanggal
min_date = df['datetime'].min().date()
# Default tanggal: 30 hari dari data terakhir
default_date = last_available_date + timedelta(days=30) 

target_date = st.sidebar.date_input(
    "Lihat Data Hingga Tanggal:", 
    value=default_date,
    min_value=min_date
)

# =========================================================
# 5. LOGIKA PREDIKSI & VISUALISASI
# =========================================================

# Hitung selisih hari dari data terakhir
delta_days = (target_date - last_available_date).days

if st.sidebar.button("Tampilkan Analisis"):
    
    # Container Grafik
    fig = go.Figure()
    
    # 1. KASUS: TANGGAL MASA LALU (HISTORIS SAJA)
    if delta_days <= 0:
        st.info(f"📅 Tanggal {target_date} adalah data historis (Masa Lalu). Menampilkan data aktual.")
        
        # Filter data historis sampai tanggal yang dipilih
        mask = df['datetime'].dt.date <= target_date
        # Ambil max 90 hari ke belakang dari tanggal yang dipilih agar grafik tidak terlalu padat
        filtered_df = df[mask].tail(90) 
        
        fig.add_trace(go.Scatter(
            x=filtered_df['datetime'],
            y=filtered_df['demand_mw'],
            mode='lines',
            name='Data Aktual (History)',
            line=dict(color='black', width=2)
        ))
        
        display_df = filtered_df
        
    # 2. KASUS: TANGGAL MASA DEPAN (FORECASTING)
    else:
        st.success(f"🚀 Melakukan forecasting untuk {delta_days} hari ke depan (sampai {target_date}).")
        
        with st.spinner('Sedang memproses model...'):
            # Lakukan Prediksi
            forecasts = mlf.predict(h=delta_days)
            
            # --- GABUNGKAN DATA ---
            # Ambil data historis 60 hari terakhir sebagai konteks
            history_context = df.tail(60)
            
            # Plot Data Historis
            fig.add_trace(go.Scatter(
                x=history_context['datetime'],
                y=history_context['demand_mw'],
                mode='lines',
                name='Data Aktual (Terakhir)',
                line=dict(color='black', width=2)
            ))
            
            # Plot Data Prediksi (Model Terpilih)
            if selected_model in forecasts.columns:
                fig.add_trace(go.Scatter(
                    x=forecasts['ds'],
                    y=forecasts[selected_model],
                    mode='lines',
                    name=f'Prediksi ({selected_model})',
                    line=dict(color='red', width=2, dash='dash')
                ))
            else:
                st.error(f"Model '{selected_model}' tidak ditemukan dalam hasil prediksi.")
            
            display_df = forecasts

    # Layout Grafik
    fig.update_layout(
        title=f"Analisis Beban Listrik (Model: {selected_model})",
        xaxis_title="Waktu",
        yaxis_title="Beban (MW)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tampilkan Tabel
    with st.expander("Lihat Detail Data Tabel"):
        st.dataframe(display_df)

else:
    st.info("👈 Silakan atur konfigurasi di sidebar dan klik 'Tampilkan Analisis'")
