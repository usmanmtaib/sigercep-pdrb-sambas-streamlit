# SIGERCEP PDRB Kabupaten Sambas — Streamlit

Versi Streamlit dari dashboard Sistem Gerak Cepat Pertumbuhan Ekonomi Daerah Kabupaten Sambas.

## Menjalankan aplikasi

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Memperbarui data

Data lima tabel untuk 17 lapangan usaha dan total PDRB berada di `data/pdrb_long.csv`. Berkas ini mencakup 21 periode dari Triwulan I 2022 sampai Triwulan I 2026 dan dihasilkan dari workbook sumber BPS Kabupaten Sambas.

## Deploy ke Streamlit Community Cloud

1. Hubungkan repositori ini ke Streamlit Community Cloud.
2. Pilih `app.py` sebagai entrypoint.
3. Pilih subdomain, misalnya `sigercep-pdrb-sambas.streamlit.app`.
