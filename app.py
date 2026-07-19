from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="SIGERCEP PDRB Kabupaten Sambas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "pdrb_long.csv"
PERIODS = [
    "Triwulan I 2022", "Triwulan II 2022", "Triwulan III 2022", "Triwulan IV 2022", "Tahunan 2022",
    "Triwulan I 2023", "Triwulan II 2023", "Triwulan III 2023", "Triwulan IV 2023", "Tahunan 2023",
    "Triwulan I 2024", "Triwulan II 2024", "Triwulan III 2024", "Triwulan IV 2024", "Tahunan 2024",
    "Triwulan I 2025", "Triwulan II 2025", "Triwulan III 2025", "Triwulan IV 2025", "Tahunan 2025",
    "Triwulan I 2026",
]
TABLE_LABELS = {
    "ADHB": "PDRB ADHB",
    "ADHK": "PDRB ADHK",
    "Distribusi": "Distribusi",
    "Q-to-Q": "Pertumbuhan Q-to-Q",
    "Y-on-Y": "Pertumbuhan Y-on-Y",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    frame = pd.read_csv(DATA_PATH)
    frame["nilai"] = pd.to_numeric(frame["nilai"], errors="coerce")
    return frame


def format_id(value: float, decimals: int = 2) -> str:
    if pd.isna(value):
        return "Belum tersedia"
    return f"{value:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def status(value: float) -> str:
    if pd.isna(value):
        return "Belum tersedia"
    if value <= -5:
        return "Kontraksi tajam"
    if value < 0:
        return "Melemah"
    if value < 5:
        return "Tumbuh"
    return "Ekspansif"


data = load_data()

st.markdown("""
<style>
    .stApp { background: #f4f7f5; }
    [data-testid="stSidebar"] { background: #082f2a; color: white; }
    [data-testid="stSidebar"] * { color: #f0fdfa; }
    .hero { padding: 2rem; border-radius: 22px; background: linear-gradient(120deg,#0f4c43,#166b5e); color: white; margin-bottom: 1rem; }
    .hero h1 { color: white; font-size: clamp(2rem,4vw,3.5rem); line-height: 1.05; margin: .35rem 0 1rem; }
    .eyebrow { letter-spacing: .12em; text-transform: uppercase; color: #99f6e4; font-size: .78rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("SG · SIGERCEP")
    st.caption("Sistem Gerak Cepat Pertumbuhan Ekonomi Daerah")
    st.divider()
    selected_period = st.selectbox("Periode analisis", PERIODS, index=len(PERIODS) - 1)
    st.success("Data lengkap lima tabel tersedia untuk 2022–Triwulan I 2026.")
    st.caption("Harga konstan menggunakan tahun dasar 2010.")

st.markdown("""
<section class="hero">
  <div class="eyebrow">Dashboard ekonomi daerah · 6101 Kabupaten Sambas</div>
  <h1>Pertumbuhan ekonomi Kabupaten Sambas dalam satu kendali.</h1>
  <p>Pantau nilai PDRB, kontribusi 17 lapangan usaha, dan sinyal perubahan ekonomi secara cepat untuk mendukung keputusan perangkat daerah.</p>
</section>
""", unsafe_allow_html=True)

period_data = data[data["periode"] == selected_period]
pdrb = period_data[period_data["kode"] == "PDRB"].set_index("tabel")["nilai"]
sectors = period_data[period_data["kode"] != "PDRB"].pivot(
    index=["kode", "lapangan_usaha"], columns="tabel", values="nilai"
).reset_index()

m1, m2, m3, m4 = st.columns(4)
m1.metric("PDRB harga berlaku", f"Rp{format_id(pdrb['ADHB'] / 1_000_000)} T", selected_period)
m2.metric("Pertumbuhan y-on-y", f"{format_id(pdrb['Y-on-Y'])}{'%' if pd.notna(pdrb['Y-on-Y']) else ''}", status(pdrb["Y-on-Y"]))
m3.metric("Pertumbuhan q-to-q", f"{format_id(pdrb['Q-to-Q'])}{'%' if pd.notna(pdrb['Q-to-Q']) else ''}", status(pdrb["Q-to-Q"]), delta_color="inverse")
m4.metric("PDRB harga konstan", f"Rp{format_id(pdrb['ADHK'] / 1_000_000)} T")

trend = data[
    (data["tabel"] == "Y-on-Y")
    & (data["kode"] == "PDRB")
    & data["periode"].str.startswith("Triwulan")
].copy()
trend = trend.dropna(subset=["nilai"])
trend["Urutan"] = trend["periode"].map({period: index for index, period in enumerate(PERIODS)})
trend = trend.sort_values("Urutan")
trend["Periode"] = (
    trend["periode"]
    .str.replace("Triwulan IV", "T4", regex=False)
    .str.replace("Triwulan III", "T3", regex=False)
    .str.replace("Triwulan II", "T2", regex=False)
    .str.replace("Triwulan I", "T1", regex=False)
)
trend["Pertumbuhan"] = trend["nilai"]
trend["Kondisi"] = trend["Pertumbuhan"].map(lambda value: "Kontraksi" if value < 0 else "Tumbuh")
trend["Sorotan"] = trend["periode"].eq(selected_period)

period_order = trend["Periode"].tolist()
x_axis = alt.X(
    "Periode:N",
    sort=period_order,
    title=None,
    axis=alt.Axis(labelAngle=0, labelColor="#475569", labelPadding=10, tickSize=0),
)
y_axis = alt.Y(
    "Pertumbuhan:Q",
    title="Pertumbuhan (%)",
    scale=alt.Scale(zero=True, nice=True),
    axis=alt.Axis(
        format=".1f",
        gridColor="#dbe7e3",
        gridDash=[3, 4],
        labelColor="#475569",
        titleColor="#334155",
        titlePadding=14,
    ),
)
tooltip = [
    alt.Tooltip("periode:N", title="Periode"),
    alt.Tooltip("Pertumbuhan:Q", title="Pertumbuhan", format=".2f"),
    alt.Tooltip("Kondisi:N", title="Kondisi"),
]

base = alt.Chart(trend).encode(x=x_axis, y=y_axis)
area = base.mark_area(
    interpolate="monotone",
    opacity=0.18,
    color=alt.Gradient(
        gradient="linear",
        stops=[
            alt.GradientStop(color="#0f766e", offset=0),
            alt.GradientStop(color="#99f6e4", offset=1),
        ],
        x1=1,
        x2=1,
        y1=0,
        y2=1,
    ),
)
line = base.mark_line(interpolate="monotone", color="#0f766e", strokeWidth=3.5)
points = base.mark_circle(size=105, stroke="#ffffff", strokeWidth=2).encode(
    color=alt.Color(
        "Kondisi:N",
        scale=alt.Scale(domain=["Tumbuh", "Kontraksi"], range=["#0f766e", "#dc2626"]),
        legend=None,
    ),
    tooltip=tooltip,
)
zero_line = alt.Chart(pd.DataFrame({"Pertumbuhan": [0]})).mark_rule(
    color="#94a3b8", strokeDash=[6, 5], strokeWidth=1
).encode(y="Pertumbuhan:Q")
highlight = (
    base.transform_filter(alt.datum.Sorotan)
    .mark_circle(size=260, color="#f59e0b", stroke="#ffffff", strokeWidth=3)
    .encode(tooltip=tooltip)
)

yoy_chart = (area + zero_line + line + points + highlight).properties(height=350).configure_view(
    stroke=None
).configure_axis(
    domain=False
)

with st.container(border=True):
    st.subheader("Pertumbuhan y-on-y per triwulan")
    st.caption("Arah pertumbuhan ekonomi dibandingkan dengan triwulan yang sama pada tahun sebelumnya.")
    st.altair_chart(yoy_chart, width="stretch")

    latest = trend.iloc[-1]
    previous = trend.iloc[-2]
    peak = trend.loc[trend["Pertumbuhan"].idxmax()]
    change = latest["Pertumbuhan"] - previous["Pertumbuhan"]
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Pertumbuhan terbaru",
        f"{format_id(latest['Pertumbuhan'])}%",
        latest["Periode"],
        delta_color="off",
    )
    c2.metric("Perubahan dari triwulan lalu", f"{format_id(change)} poin persentase")
    c3.metric(
        "Pertumbuhan tertinggi",
        f"{format_id(peak['Pertumbuhan'])}%",
        peak["Periode"],
        delta_color="off",
    )

growth_text = f"{format_id(pdrb['Y-on-Y'])}%" if pd.notna(pdrb["Y-on-Y"]) else "belum tersedia pada workbook sumber"
st.caption(f"Pada {selected_period}, pertumbuhan y-on-y {growth_text}.")

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Kontribusi lapangan usaha terbesar")
    top = sectors.nlargest(7, "Distribusi").set_index("lapangan_usaha")[["Distribusi"]]
    st.bar_chart(top, color="#14b8a6", horizontal=True, height=430)
with right:
    st.subheader("Sinyal cepat q-to-q")
    signals = sectors.nsmallest(6, "Q-to-Q")[["kode", "lapangan_usaha", "Q-to-Q"]].copy()
    signals["Status"] = signals["Q-to-Q"].map(status)
    signals.columns = ["Kode", "Lapangan usaha", "Q-to-Q (%)", "Status"]
    st.dataframe(signals, hide_index=True, width="stretch", height=430)

st.subheader("Eksplorasi data PDRB lapangan usaha")
query = st.text_input("Cari lapangan usaha", placeholder="Contoh: pertanian atau konstruksi")

tabs = st.tabs(list(TABLE_LABELS.values()))
for tab, (table_key, table_label) in zip(tabs, TABLE_LABELS.items()):
    with tab:
        table = period_data[period_data["tabel"] == table_key][["kode", "lapangan_usaha", "nilai"]].copy()
        if query:
            table = table[table["lapangan_usaha"].str.contains(query, case=False, na=False)]
        unit = "Juta rupiah" if table_key in {"ADHB", "ADHK"} else "Persen"
        table.columns = ["Kode", "Lapangan usaha", f"{selected_period} ({unit})"]
        if table_key in {"Q-to-Q", "Y-on-Y"}:
            table["Status"] = table.iloc[:, 2].map(status)
        st.dataframe(table, hide_index=True, width="stretch")

download = period_data.pivot(index=["kode", "lapangan_usaha"], columns="tabel", values="nilai").reset_index()
csv = download.to_csv(index=False).encode("utf-8-sig")
safe_period = selected_period.lower().replace(" ", "_")
st.download_button("Unduh data periode aktif", csv, f"sigercep_{safe_period}.csv", "text/csv", width="stretch")

st.divider()
st.markdown("**SIGERCEP PDRB Kabupaten Sambas**")
st.caption("Sumber: 6101 Kab Sambas PDRB Lapus Q1 2026_Putaran 5.xlsx · Nilai ADHB/ADHK dalam juta rupiah; distribusi dan pertumbuhan dalam persen.")
