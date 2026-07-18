import io

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="SIGERCEP PDRB Kabupaten Sambas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PERIODS = [
    "Triwulan I 2023", "Triwulan II 2023", "Triwulan III 2023", "Triwulan IV 2023", "Tahunan 2023",
    "Triwulan I 2024", "Triwulan II 2024", "Triwulan III 2024", "Triwulan IV 2024", "Tahunan 2024",
    "Triwulan I 2025", "Triwulan II 2025", "Triwulan III 2025", "Triwulan IV 2025", "Tahunan 2025",
    "Triwulan I 2026",
]

TREND = pd.DataFrame({
    "Periode": ["2023 TI", "2023 TII", "2023 TIII", "2023 TIV", "2024 TI", "2024 TII", "2024 TIII", "2024 TIV", "2025 TI", "2025 TII", "2025 TIII", "2025 TIV", "2026 TI"],
    "Pertumbuhan y-on-y (%)": [4.21, 4.72, 4.55, 5.21, 4.74, 4.76, 4.56, 4.91, 4.39, 4.93, 4.86, 4.76, 5.21],
})

SECTORS = pd.DataFrame([
    ("A", "Pertanian, Kehutanan, dan Perikanan", 34.53, 3.15, 1.20),
    ("B", "Pertambangan dan Penggalian", 2.38, 2.77, -11.54),
    ("C", "Industri Pengolahan", 11.77, 4.70, 0.83),
    ("D", "Pengadaan Listrik dan Gas", 0.09, 3.25, 1.12),
    ("E", "Pengadaan Air, Pengelolaan Sampah, Limbah dan Daur Ulang", 0.13, 10.22, 2.44),
    ("F", "Konstruksi", 8.26, 7.42, -13.78),
    ("G", "Perdagangan Besar dan Eceran; Reparasi Mobil dan Sepeda Motor", 17.62, 7.60, 1.73),
    ("H", "Transportasi dan Pergudangan", 2.69, 13.74, 3.91),
    ("I", "Penyediaan Akomodasi dan Makan Minum", 2.10, 7.00, 0.96),
    ("J", "Informasi dan Komunikasi", 4.17, 3.97, 1.08),
    ("K", "Jasa Keuangan dan Asuransi", 2.67, 3.49, 0.66),
    ("L", "Real Estate", 2.91, 6.23, 1.15),
    ("M,N", "Jasa Perusahaan", 0.28, 1.43, -4.87),
    ("O", "Administrasi Pemerintahan, Pertahanan dan Jaminan Sosial Wajib", 5.66, 13.04, -2.35),
    ("P", "Jasa Pendidikan", 3.79, 0.75, -4.28),
    ("Q", "Jasa Kesehatan dan Kegiatan Sosial", 1.49, 8.70, 0.32),
    ("R,S,T,U", "Jasa lainnya", 1.62, 0.27, -2.58),
], columns=["Kode", "Lapangan usaha", "Distribusi (%)", "Y-on-Y (%)", "Q-to-Q (%)"])


def status(value: float) -> str:
    if value <= -5:
        return "Kontraksi tajam"
    if value < 0:
        return "Melemah"
    if value < 5:
        return "Tumbuh"
    return "Ekspansif"


st.markdown("""
<style>
    .stApp { background: #f4f7f5; }
    [data-testid="stSidebar"] { background: #082f2a; color: white; }
    [data-testid="stSidebar"] * { color: #f0fdfa; }
    .hero { padding: 2rem; border-radius: 22px; background: linear-gradient(120deg,#0f4c43,#166b5e); color: white; margin-bottom: 1rem; }
    .hero h1 { color: white; font-size: clamp(2rem,4vw,3.5rem); line-height: 1.05; margin: .35rem 0 1rem; }
    .eyebrow { letter-spacing: .12em; text-transform: uppercase; color: #99f6e4; font-size: .78rem; font-weight: 700; }
    .note { color: #52635e; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("SG · SIGERCEP")
    st.caption("Sistem Gerak Cepat Pertumbuhan Ekonomi Daerah")
    st.divider()
    selected_period = st.selectbox("Periode analisis", PERIODS, index=len(PERIODS)-1)
    st.info("Data rinci yang berhasil dipindahkan saat ini tersedia untuk Triwulan I 2026. Seri pertumbuhan tersedia sejak 2023.")
    st.caption("Harga konstan menggunakan tahun dasar 2010.")

st.markdown("""
<section class="hero">
  <div class="eyebrow">Dashboard ekonomi daerah · 6101 Kabupaten Sambas</div>
  <h1>Pertumbuhan ekonomi Kabupaten Sambas dalam satu kendali.</h1>
  <p>Pantau nilai PDRB, kontribusi 17 lapangan usaha, dan sinyal perubahan ekonomi secara cepat untuk mendukung keputusan perangkat daerah.</p>
</section>
""", unsafe_allow_html=True)

if selected_period != "Triwulan I 2026":
    st.warning("Rincian sektoral untuk periode ini belum tersedia pada hasil migrasi. Grafik tren tetap menampilkan angka yang tersedia.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("PDRB harga berlaku", "Rp8,12 T", "Triwulan I 2026")
m2.metric("Pertumbuhan y-on-y", "5,21%", "positif")
m3.metric("Pertumbuhan q-to-q", "-0,07%", "melemah", delta_color="inverse")
m4.metric("PDRB harga konstan", "Rp4,3 T")

st.subheader("Pertumbuhan y-on-y per triwulan")
st.line_chart(TREND.set_index("Periode"), color="#0f766e", height=340)
st.caption("Perekonomian tetap tumbuh positif; Triwulan I 2026 mencapai 5,21% y-on-y.")

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Kontribusi lapangan usaha terbesar")
    top = SECTORS.nlargest(7, "Distribusi (%)").set_index("Lapangan usaha")[["Distribusi (%)"]]
    st.bar_chart(top, color="#14b8a6", horizontal=True, height=430)
with right:
    st.subheader("Sinyal cepat q-to-q")
    signals = SECTORS.nsmallest(6, "Q-to-Q (%)")[["Kode", "Lapangan usaha", "Q-to-Q (%)"]].copy()
    signals["Status"] = signals["Q-to-Q (%)"].map(status)
    st.dataframe(signals, hide_index=True, use_container_width=True, height=430)

st.subheader("Eksplorasi data PDRB lapangan usaha")
query = st.text_input("Cari lapangan usaha", placeholder="Contoh: pertanian atau konstruksi")
filtered = SECTORS[SECTORS["Lapangan usaha"].str.contains(query, case=False, na=False)] if query else SECTORS.copy()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["PDRB ADHB", "PDRB ADHK", "Distribusi", "Pertumbuhan Q-to-Q", "Pertumbuhan Y-on-Y"])
with tab1:
    st.info("Nilai lengkap ADHB per sektor perlu diisi dari workbook sumber.")
with tab2:
    st.info("Nilai lengkap ADHK per sektor perlu diisi dari workbook sumber.")
with tab3:
    st.dataframe(filtered[["Kode", "Lapangan usaha", "Distribusi (%)"]], hide_index=True, use_container_width=True)
with tab4:
    qoq = filtered[["Kode", "Lapangan usaha", "Q-to-Q (%)"]].copy()
    qoq["Status"] = qoq["Q-to-Q (%)"].map(status)
    st.dataframe(qoq, hide_index=True, use_container_width=True)
with tab5:
    yoy = filtered[["Kode", "Lapangan usaha", "Y-on-Y (%)"]].copy()
    yoy["Status"] = yoy["Y-on-Y (%)"].map(status)
    st.dataframe(yoy, hide_index=True, use_container_width=True)

csv = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button("Unduh data CSV", csv, "sigercep_pdrb_sambas_q1_2026.csv", "text/csv", use_container_width=True)

st.divider()
st.markdown("**SIGERCEP PDRB Kabupaten Sambas**")
st.caption("Data 2023 sampai Triwulan I 2026 · Nilai ADHB/ADHK dalam juta rupiah; distribusi dan pertumbuhan dalam persen.")

