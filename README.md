# ⚡ PGCB Power Demand Forecasting Dashboard

Aplikasi web interaktif untuk prediksi beban listrik PGCB (Power Grid Company of Bangladesh) menggunakan **LSTM (Long Short-Term Memory)** neural network model dari NeuralForecast.

## 🎯 Fitur Utama

- 📊 **Visualisasi Data Historis**: Grafik interaktif data beban listrik 90 hari terakhir
- 🔮 **Prediksi Berbasis Tanggal**: Pilih tanggal mulai dan horizon prediksi (1-90 hari)
- 📈 **Grafik Prediksi**: Visualisasi perbandingan data historis vs prediksi LSTM
- 📋 **Tabel Hasil**: Data prediksi dalam format tabel yang mudah dibaca
- 📥 **Export CSV**: Download hasil prediksi untuk analisis lebih lanjut
- 📊 **Metrics Dashboard**: Statistik real-time (min, max, average demand)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Instalasi Lokal

1. **Clone repository:**
```bash
git clone https://github.com/adinnhd/PGCB-Dashboard.git
cd PGCB-Dashboard
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Jalankan aplikasi:**
```bash
streamlit run app.py
```

4. **Buka browser** dan akses `http://localhost:8501`

## 📂 Struktur Folder

```
forecast_deploy/
├── app.py                      # Aplikasi Streamlit utama
├── requirements.txt            # Dependencies Python
├── forecasting_model.pkl       # Model forecasting (legacy)
├── lstm_model/                 # LSTM Model dari NeuralForecast
│   ├── LSTM_0.ckpt            # Model weights
│   ├── configuration.pkl       # Konfigurasi model
│   ├── dataset.pkl            # Data historis
│   └── alias_to_model.pkl     # Model alias mapping
├── .streamlit/
│   └── config.toml            # Konfigurasi Streamlit Cloud
├── .gitignore                 # Git ignore file
└── README.md                  # Dokumentasi ini
```

## 🌐 Deploy ke Streamlit Cloud

### Langkah-langkah Deployment:

1. **Push ke GitHub:**
```bash
git add .
git commit -m "Update LSTM forecasting dashboard"
git push origin main
```

2. **Login ke Streamlit Cloud:**
   - Kunjungi [streamlit.io/cloud](https://streamlit.io/cloud)
   - Login dengan GitHub account

3. **Deploy App:**
   - Klik "New app"
   - Pilih repository: `adinnhd/PGCB-Dashboard`
   - Set main file path: `app.py`
   - Klik "Deploy"

4. **Tunggu build selesai** (sekitar 2-5 menit)

5. **Akses aplikasi** di URL yang diberikan

### Troubleshooting Deployment:

**Jika build gagal:**
- Check logs di Streamlit Cloud dashboard
- Pastikan `requirements.txt` benar
- Pastikan semua file model ada di repository

**Jika app lambat:**
- Model LSTM memerlukan waktu loading ~10-30 detik pertama kali
- Setelah cache, prediksi akan lebih cepat

**File size warning:**
- Jika model file terlalu besar (>100MB), pertimbangkan menggunakan Git LFS
- Atau upload model ke cloud storage (Google Drive, S3) dan download saat runtime

## 📊 Cara Menggunakan

1. **Lihat Data Historis:**
   - Dashboard menampilkan grafik 90 hari terakhir secara otomatis
   - Lihat statistik: Total data points, Average, Max, Min demand

2. **Konfigurasi Prediksi:**
   - Di sidebar, pilih **Tanggal Mulai Prediksi**
   - Atur **Horizon Prediksi** (1-90 hari)
   - Sistem akan menampilkan range tanggal prediksi

3. **Mulai Prediksi:**
   - Klik tombol **"🚀 Mulai Prediksi"**
   - Tunggu proses forecasting (5-15 detik)

4. **Analisis Hasil:**
   - Lihat statistik prediksi (avg, max, min)
   - Analisis grafik perbandingan historical vs forecast
   - Review tabel data lengkap

5. **Download Hasil:**
   - Klik **"📥 Download Prediksi (CSV)"**
   - Simpan untuk analisis atau reporting

## 🛠️ Teknologi yang Digunakan

- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly
- **ML Model:** NeuralForecast (LSTM)
- **Deep Learning Framework:** PyTorch Lightning
- **Model Persistence:** Joblib

## 📈 Model Information

- **Type:** LSTM (Long Short-Term Memory)
- **Framework:** NeuralForecast
- **Input:** Historical demand data
- **Output:** Future demand predictions
- **Training Data:** PGCB historical power demand

## 📝 Notes

- Model telah dilatih menggunakan data historis PGCB
- Prediksi bersifat estimasi dan dapat berbeda dengan realisasi actual
- Untuk hasil terbaik, gunakan horizon prediksi ≤ 30 hari
- Data historis di-cache untuk performa lebih baik

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Contact

Untuk pertanyaan atau feedback, silakan buat issue di repository ini.

## 📄 License

MIT License - feel free to use this project for your own purposes.

---

**Made with ❤️ using Streamlit and NeuralForecast**
