import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from datetime import datetime, timedelta
from neuralforecast import NeuralForecast

# =========================================================
# 1. SETUP HALAMAN
# =========================================================
st.set_page_config(
    page_title="PGCB Power Forecasting", 
    layout="wide",
    page_icon="⚡"
)

st.title("⚡ PGCB Power Demand Forecasting")
st.markdown("Aplikasi prediksi beban listrik menggunakan **LSTM Neural Network** untuk forecasting demand listrik.")

# =========================================================
# 2. LOAD MODEL & DATA
# =========================================================
@st.cache_resource
def load_lstm_model():
    """Load LSTM model from NeuralForecast"""
    try:
        nf = NeuralForecast.load(path='./lstm_model/')
        return nf
    except Exception as e:
        st.error(f"Error loading LSTM model: {e}")
        return None

@st.cache_data
def load_historical_data(_model):
    """Extract historical data from NeuralForecast model"""
    try:
        # Get the data from NeuralForecast's fitted data
        if hasattr(_model, 'dataset') and _model.dataset is not None:
            # Extract from TimeSeriesDataset
            dataset = _model.dataset
            if hasattr(dataset, 'temporal_df'):
                data = dataset.temporal_df.copy()
            elif hasattr(dataset, 'df'):
                data = dataset.df.copy()
            else:
                # Fallback: create sample data for visualization
                st.warning("Using sample data for visualization")
                import numpy as np
                dates = pd.date_range(end=pd.Timestamp.now(), periods=1000, freq='H')
                data = pd.DataFrame({
                    'ds': dates,
                    'y': np.random.randn(1000).cumsum() + 1000
                })
        else:
            # Create sample data if no dataset available
            st.warning("Model has no historical data. Using sample data.")
            import numpy as np
            dates = pd.date_range(end=pd.Timestamp.now(), periods=1000, freq='H')
            data = pd.DataFrame({
                'ds': dates,
                'y': np.random.randn(1000).cumsum() + 1000
            })
        
        # Ensure proper datetime
        if 'ds' in data.columns:
            data['ds'] = pd.to_datetime(data['ds'])
        
        return data
    except Exception as e:
        st.error(f"Error loading historical data: {e}")
        # Return sample data as fallback
        import numpy as np
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='H')
        return pd.DataFrame({
            'ds': dates,
            'y': np.random.randn(100).cumsum() + 1000
        })

# Load resources
with st.spinner('Loading model dan data...'):
    model = load_lstm_model()
    df_history = load_historical_data(model)

if model is None or df_history is None:
    st.error("❌ Gagal memuat model atau data. Pastikan file `lstm_model/` dan `lstm_model/dataset.pkl` tersedia.")
    st.stop()
else:
    st.success("✅ Model LSTM & Data loaded successfully!")

# =========================================================
# 3. SIDEBAR - KONFIGURASI PREDIKSI
# =========================================================
st.sidebar.header("⚙️ Konfigurasi Forecast")

# Dapatkan tanggal terakhir dari data historis
last_date = df_history['ds'].max()
st.sidebar.info(f"📅 Data terakhir: {last_date.strftime('%Y-%m-%d')}")

# Date picker untuk tanggal mulai prediksi
start_date = st.sidebar.date_input(
    "Tanggal Mulai Prediksi:",
    value=last_date + timedelta(days=1),
    min_value=last_date + timedelta(days=1),
    max_value=last_date + timedelta(days=365)
)

# Slider untuk horizon prediksi
forecast_days = st.sidebar.slider(
    "Horizon Prediksi (hari):",
    min_value=1,
    max_value=90,
    value=30,
    help="Jumlah hari ke depan yang akan diprediksi"
)

# Hitung end date
end_date = start_date + timedelta(days=forecast_days - 1)
st.sidebar.success(f"Prediksi: {start_date.strftime('%Y-%m-%d')} s/d {end_date.strftime('%Y-%m-%d')}")

# =========================================================
# 4. MAIN CONTENT - VISUALISASI DATA HISTORIS
# =========================================================
st.subheader("📊 Data Historis")

# Tampilkan statistik data historis
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Data Points", f"{len(df_history):,}")
with col2:
    if 'y' in df_history.columns:
        st.metric("Avg Demand (MW)", f"{df_history['y'].mean():.2f}")
with col3:
    if 'y' in df_history.columns:
        st.metric("Max Demand (MW)", f"{df_history['y'].max():.2f}")
with col4:
    if 'y' in df_history.columns:
        st.metric("Min Demand (MW)", f"{df_history['y'].min():.2f}")

# Plot data historis (90 hari terakhir)
fig_history = go.Figure()
last_90_days = df_history.tail(90)
fig_history.add_trace(go.Scatter(
    x=last_90_days['ds'],
    y=last_90_days['y'],
    mode='lines',
    name='Historical Demand',
    line=dict(color='#1f77b4', width=2)
))

fig_history.update_layout(
    title="Demand Listrik - 90 Hari Terakhir",
    xaxis_title="Tanggal",
    yaxis_title="Beban Listrik (MW)",
    template="plotly_white",
    hovermode="x unified",
    height=400
)

st.plotly_chart(fig_history, use_container_width=True)

# =========================================================
# 5. PREDIKSI SECTION
# =========================================================
st.subheader("🔮 Forecasting")

if st.button("🚀 Mulai Prediksi", type="primary", use_container_width=True):
    with st.spinner(f'Melakukan forecasting {forecast_days} hari ke depan...'):
        try:
            # Lakukan prediksi dengan LSTM
            forecasts = model.predict(h=forecast_days)
            
            # Pastikan forecasts memiliki kolom yang benar
            if forecasts is None or len(forecasts) == 0:
                st.error("❌ Prediksi gagal. Model tidak menghasilkan output.")
                st.stop()
            
            st.success(f"✅ Prediksi selesai! {len(forecasts)} data points dihasilkan.")
            
            # =========================================================
            # 6. VISUALISASI HASIL PREDIKSI
            # =========================================================
            st.subheader(f"📈 Hasil Prediksi {forecast_days} Hari")
            
            # Tampilkan statistik prediksi
            pred_col = [c for c in forecasts.columns if c not in ['ds', 'unique_id']][0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Avg Forecast (MW)", f"{forecasts[pred_col].mean():.2f}")
            with col2:
                st.metric("📈 Max Forecast (MW)", f"{forecasts[pred_col].max():.2f}")
            with col3:
                st.metric("📉 Min Forecast (MW)", f"{forecasts[pred_col].min():.2f}")
            
            # Plot gabungan: Historical + Forecast
            fig = go.Figure()
            
            # Plot Historical (90 hari terakhir)
            historical_90 = df_history.tail(90)
            fig.add_trace(go.Scatter(
                x=historical_90['ds'],
                y=historical_90['y'],
                mode='lines',
                name='Historical Data',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # Plot Forecast
            fig.add_trace(go.Scatter(
                x=forecasts['ds'],
                y=forecasts[pred_col],
                mode='lines',
                name='LSTM Forecast',
                line=dict(color='#ff4b4b', width=2, dash='dash')
            ))
            
            # Tambahkan marker untuk transisi
            fig.add_vline(
                x=last_date.timestamp() * 1000,  # Convert to milliseconds
                line_dash="dot",
                line_color="gray",
                annotation_text="Forecast Start",
                annotation_position="top"
            )
            
            fig.update_layout(
                title="Forecast vs Historical Data",
                xaxis_title="Tanggal",
                yaxis_title="Beban Listrik (MW)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # =========================================================
            # 7. TABEL DATA PREDIKSI
            # =========================================================
            st.subheader("📋 Data Tabel Prediksi")
            
            # Format tabel untuk display
            display_df = forecasts.copy()
            if 'ds' in display_df.columns:
                display_df['Tanggal'] = pd.to_datetime(display_df['ds']).dt.strftime('%Y-%m-%d')
                display_df = display_df.drop('ds', axis=1)
            
            if 'unique_id' in display_df.columns:
                display_df = display_df.drop('unique_id', axis=1)
            
            # Rename prediction column
            pred_cols = [c for c in display_df.columns if c != 'Tanggal']
            if len(pred_cols) > 0:
                display_df = display_df.rename(columns={pred_cols[0]: 'Prediksi Demand (MW)'})
            
            # Reorder columns
            cols = ['Tanggal'] + [c for c in display_df.columns if c != 'Tanggal']
            display_df = display_df[cols]
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # =========================================================
            # 8. DOWNLOAD BUTTON
            # =========================================================
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Prediksi (CSV)",
                data=csv,
                file_name=f'forecast_{start_date}_{end_date}.csv',
                mime='text/csv',
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"❌ Error saat melakukan prediksi: {str(e)}")
            st.exception(e)

# =========================================================
# 9. FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>PGCB Power Demand Forecasting Dashboard | Powered by NeuralForecast LSTM Model</p>
    </div>
    """,
    unsafe_allow_html=True
)