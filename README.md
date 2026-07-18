# SIGERCEP PDRB Kabupaten Sambas — Streamlit

Versi Streamlit dari dashboard Sistem Gerak Cepat Pertumbuhan Ekonomi Daerah Kabupaten Sambas.

## Menjalankan aplikasi

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Memperbarui data

Data tren dan data 17 lapangan usaha berada di bagian awal `app.py`. Untuk migrasi penuh lima tabel dan seluruh periode, masukkan workbook sumber lalu pindahkan tabelnya ke berkas CSV di folder `data/`.

## Deploy ke Streamlit Community Cloud

1. Hubungkan repositori ini ke Streamlit Community Cloud.
2. Pilih `app.py` sebagai entrypoint.
3. Pilih subdomain, misalnya `sigercep-pdrb-sambas.streamlit.app`.

