from html import escape
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


def format_percent(value: float) -> str:
    return "—" if pd.isna(value) else f"{format_id(value)}%"


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


def status_tone(value: float) -> str:
    if pd.isna(value):
        return "neutral"
    if value < 0:
        return "negative"
    if value < 5:
        return "warning"
    return "positive"


def short_period(period: str) -> str:
    return (
        period.replace("Triwulan IV", "T4")
        .replace("Triwulan III", "T3")
        .replace("Triwulan II", "T2")
        .replace("Triwulan I", "T1")
    )


def extreme_row(frame: pd.DataFrame, column: str, largest: bool = True) -> pd.Series:
    candidates = frame.dropna(subset=[column])
    if candidates.empty:
        return pd.Series({"kode": "—", "lapangan_usaha": "Belum tersedia", column: float("nan")})
    ranked = candidates.nlargest(1, column) if largest else candidates.nsmallest(1, column)
    return ranked.iloc[0]


def indicator_card(number: str, label: str, value: str, detail: str) -> str:
    return f"""
    <article class="indicator-card">
        <div class="indicator-top">
            <span>{escape(label)}</span><small>{number}</small>
        </div>
        <div class="indicator-value">{escape(value)}</div>
        <div class="indicator-detail">{escape(detail)}</div>
    </article>
    """


data = load_data()

st.markdown(
    """
    <style>
        :root {
            --navy: #073c68;
            --navy-deep: #062f52;
            --blue: #096cac;
            --blue-mid: #0b78bc;
            --cyan: #72d6f7;
            --ice: #dff5ff;
            --text-soft: #b9d7e9;
            --line: rgba(196, 230, 248, .26);
            --panel: rgba(8, 91, 146, .76);
        }

        html { scroll-behavior: smooth; }
        .stApp {
            color: #f7fbff;
            background:
                radial-gradient(circle at 90% 0%, rgba(41, 156, 210, .28), transparent 34rem),
                linear-gradient(135deg, #07578e 0%, #084b7c 48%, #063a64 100%);
        }
        [data-testid="stHeader"] {
            height: 3.4rem;
            background: rgba(5, 48, 83, .78);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(255, 255, 255, .08);
        }
        [data-testid="stToolbar"] { right: 1rem; }
        .block-container {
            max-width: 1480px;
            padding: 1.3rem 2rem 3rem;
        }
        h1, h2, h3, p { color: inherit; }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b6dab 0%, #0a5f98 58%, #084c7a 100%);
            border-right: 1px solid rgba(214, 240, 255, .22);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.1rem; }
        [data-testid="stSidebar"] * { color: #f4fbff; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.18); }
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div {
            color: white;
            background: rgba(4, 57, 96, .44);
            border-color: rgba(202, 234, 250, .34);
            border-radius: 12px;
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: .75rem;
            padding: .3rem .15rem 1.05rem;
        }
        .sidebar-logo, .top-logo {
            display: grid;
            place-items: center;
            background: #f7fbff;
            color: #0b568a !important;
            font-weight: 850;
            border-radius: 13px;
            box-shadow: 0 8px 22px rgba(2, 36, 64, .2);
        }
        .sidebar-logo { width: 45px; height: 45px; }
        .sidebar-brand strong { display: block; letter-spacing: .04em; }
        .sidebar-brand small { display: block; color: #c4dfef !important; line-height: 1.25; }
        .sidebar-kicker, .section-kicker {
            margin: .4rem 0 .55rem;
            color: #bfe7f8 !important;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .15em;
            text-transform: uppercase;
        }
        .sidebar-nav { display: grid; gap: .24rem; margin-bottom: 1.3rem; }
        .sidebar-nav a {
            color: #eaf7ff !important;
            text-decoration: none;
            padding: .58rem .75rem;
            border: 1px solid transparent;
            border-radius: 11px;
            font-size: .92rem;
        }
        .sidebar-nav a:first-child,
        .sidebar-nav a:hover {
            background: rgba(5, 61, 101, .32);
            border-color: rgba(211, 239, 253, .52);
        }
        .sidebar-note {
            margin-top: 1rem;
            padding: 1rem;
            border-radius: 16px;
            background: rgba(5, 56, 93, .5);
            border: 1px solid rgba(210, 239, 253, .28);
        }
        .sidebar-note span {
            display: block;
            color: #c1e2f1 !important;
            font-size: .72rem;
            font-weight: 750;
            letter-spacing: .12em;
            text-transform: uppercase;
        }
        .sidebar-note strong { display: block; margin: .48rem 0; font: 700 1.15rem Georgia, serif; }
        .sidebar-note p { margin: 0; color: #c1dae8 !important; font-size: .82rem; line-height: 1.45; }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: .2rem 0 1.2rem;
        }
        .top-brand { display: flex; align-items: center; gap: .75rem; }
        .top-logo { width: 46px; height: 46px; }
        .top-brand strong { display: block; font-size: 1.05rem; letter-spacing: .045em; }
        .top-brand span { color: var(--text-soft); font-size: .82rem; }
        .top-badges { display: flex; gap: .6rem; flex-wrap: wrap; justify-content: flex-end; }
        .top-pill {
            padding: .48rem .78rem;
            border: 1px solid rgba(208, 237, 252, .28);
            border-radius: 999px;
            background: rgba(255, 255, 255, .07);
            color: #eff9ff;
            font-size: .8rem;
            font-weight: 720;
            letter-spacing: .03em;
        }
        .hero-grid { display: grid; grid-template-columns: minmax(0, 2.05fr) minmax(280px, .95fr); gap: 1rem; }
        .hero-main, .signal-card, .indicator-card {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            box-shadow: 0 22px 55px rgba(2, 34, 59, .16);
        }
        .hero-main {
            min-height: 390px;
            padding: 2rem;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(13, 111, 176, .96), rgba(8, 81, 137, .92));
        }
        .hero-main::after {
            content: "";
            position: absolute;
            width: 270px;
            height: 270px;
            right: -80px;
            top: -110px;
            border-radius: 50%;
            background: rgba(89, 181, 224, .16);
            box-shadow: -80px 105px 0 rgba(33, 139, 195, .15);
        }
        .hero-content { position: relative; z-index: 1; max-width: 800px; }
        .eyebrow {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            color: #caecfa;
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .16em;
            text-transform: uppercase;
        }
        .fresh { color: #90d48a; letter-spacing: 0; text-transform: none; white-space: nowrap; }
        .fresh::before { content: "●"; margin-right: .35rem; }
        .hero-main h1 {
            max-width: 760px;
            margin: .35rem 0 .9rem;
            font: 500 clamp(2.45rem, 4.4vw, 4.2rem)/.99 Georgia, "Times New Roman", serif;
            letter-spacing: -.035em;
        }
        .hero-main p { max-width: 730px; margin: 0; color: #c5deec; font-size: 1.02rem; line-height: 1.65; }
        .hero-actions { display: flex; gap: .65rem; margin-top: 1.4rem; flex-wrap: wrap; }
        .hero-action {
            display: inline-flex;
            align-items: center;
            padding: .62rem 1rem;
            border-radius: 999px;
            background: #73c7e9;
            color: #084d7a !important;
            text-decoration: none;
            font-size: .84rem;
            font-weight: 800;
        }
        .hero-action.secondary { color: #f1f9ff !important; background: transparent; border: 1px solid rgba(255,255,255,.28); }
        .hero-meta {
            display: flex;
            gap: 1.3rem;
            flex-wrap: wrap;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(222, 243, 253, .2);
            color: #bbd9e8;
            font-size: .78rem;
        }
        .hero-meta strong { color: white; margin-right: .28rem; }

        .signal-card {
            min-height: 390px;
            padding: 1.7rem;
            border-radius: 24px;
            background: linear-gradient(160deg, rgba(13, 109, 176, .98), rgba(7, 79, 134, .96));
        }
        .signal-head { display: flex; justify-content: space-between; gap: .75rem; align-items: flex-start; }
        .signal-head span:first-child { color: #c2e3f2; font-size: .73rem; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; }
        .status-badge { padding: .25rem .55rem; border-radius: 999px; font-size: .7rem; font-weight: 800; }
        .status-badge.positive { color: #155b45; background: #b9f3d9; }
        .status-badge.warning { color: #7a4d12; background: #ffe4a8; }
        .status-badge.negative { color: #802e35; background: #ffd0d3; }
        .status-badge.neutral { color: #405669; background: #dbe8ef; }
        .signal-period { margin-top: .38rem; font: 500 1.55rem/1.08 Georgia, serif; }
        .signal-number { margin-top: 2.1rem; font: 500 clamp(3.3rem, 5vw, 4.5rem)/1 Georgia, serif; letter-spacing: -.04em; }
        .signal-label { margin-top: .45rem; color: #bcd8e7; font-size: .82rem; }
        .mini-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; margin-top: 2rem; }
        .mini-card { padding: .72rem .8rem; border-radius: 14px; background: rgba(4, 53, 89, .46); }
        .mini-card span { display: block; color: #a9cfdf; font-size: .68rem; text-transform: uppercase; }
        .mini-card strong { display: block; margin-top: .15rem; font-size: 1.03rem; }
        .signal-foot { margin-top: 1.4rem; color: #b5d3e2; font-size: .75rem; }

        .indicator-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .85rem; margin: 1rem 0 1.7rem; }
        .indicator-card {
            min-height: 180px;
            padding: 1.25rem;
            border-radius: 19px;
            background: linear-gradient(145deg, rgba(14, 111, 177, .95), rgba(7, 78, 132, .88));
        }
        .indicator-top { display: flex; justify-content: space-between; gap: .75rem; color: #cae8f6; }
        .indicator-top span { max-width: 160px; font-size: .7rem; font-weight: 800; letter-spacing: .1em; line-height: 1.25; text-transform: uppercase; }
        .indicator-top small { color: #a8cadb; }
        .indicator-value { margin-top: 1.55rem; font: 500 clamp(1.25rem, 2vw, 1.75rem)/1.12 Georgia, serif; }
        .indicator-detail { margin-top: .48rem; color: #b9d6e5; font-size: .78rem; line-height: 1.35; }

        .section-anchor { display: block; position: relative; top: -4rem; visibility: hidden; }
        .section-heading { margin: 1.5rem 0 .85rem; }
        .section-heading h2 { margin: .16rem 0 .2rem; font: 500 clamp(1.65rem, 2.8vw, 2.35rem)/1.1 Georgia, serif; }
        .section-heading p { margin: 0; color: #b9d6e5; font-size: .88rem; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(7, 71, 119, .5);
            border-color: var(--line);
            border-radius: 20px;
            box-shadow: 0 18px 40px rgba(2, 33, 57, .12);
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] p { color: #bcd9e8; }
        .trend-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .65rem; margin-top: .4rem; }
        .trend-stat { padding: .85rem 1rem; border-radius: 14px; background: rgba(3, 48, 82, .38); }
        .trend-stat span { display: block; color: #a9cfdf; font-size: .7rem; letter-spacing: .07em; text-transform: uppercase; }
        .trend-stat strong { display: block; margin-top: .22rem; font-size: 1.15rem; }
        .trend-stat small { color: #b6d4e2; }
        .signal-list { display: grid; gap: .5rem; }
        .signal-row {
            display: grid;
            grid-template-columns: 38px minmax(0, 1fr) auto;
            align-items: center;
            gap: .7rem;
            padding: .72rem .8rem;
            border-radius: 13px;
            background: rgba(4, 54, 91, .34);
            border: 1px solid rgba(192, 226, 243, .12);
        }
        .signal-code { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; background: rgba(106, 207, 242, .17); color: #aee6fa; font-weight: 800; }
        .signal-name { min-width: 0; color: #eff9ff; font-size: .82rem; line-height: 1.25; }
        .signal-value { text-align: right; }
        .signal-value strong { display: block; color: #ffd0d3; font-size: .9rem; }
        .signal-value span { color: #a9cad9; font-size: .66rem; }

        [data-testid="stDataFrame"] { border: 1px solid rgba(200, 232, 247, .18); border-radius: 14px; overflow: hidden; }
        [data-testid="stTextInput"] input {
            color: white;
            background: rgba(4, 54, 91, .52);
            border-color: rgba(200, 232, 247, .22);
            border-radius: 12px;
        }
        [data-testid="stTextInput"] label, [data-testid="stSelectbox"] label { color: #dff3fc; }
        button[data-baseweb="tab"] { color: #bcd9e8; }
        button[data-baseweb="tab"][aria-selected="true"] { color: white; }
        [data-testid="stDownloadButton"] button {
            color: #074b78;
            background: #79d4f3;
            border: 0;
            border-radius: 999px;
            font-weight: 800;
        }
        .footer {
            margin-top: 2rem;
            padding-top: 1.2rem;
            border-top: 1px solid rgba(203, 234, 249, .18);
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            color: #a9cad9;
            font-size: .76rem;
        }
        .footer strong { color: #eef9ff; }

        @media (max-width: 1050px) {
            .hero-grid { grid-template-columns: 1fr; }
            .signal-card { min-height: auto; }
            .indicator-grid { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 720px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .topbar { align-items: flex-start; }
            .top-badges .top-pill:last-child { display: none; }
            .hero-main { min-height: auto; padding: 1.35rem; }
            .hero-main h1 { font-size: 2.35rem; }
            .eyebrow { align-items: flex-start; flex-direction: column; }
            .indicator-grid { grid-template-columns: 1fr; }
            .trend-stats { grid-template-columns: 1fr; }
            .footer { flex-direction: column; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">SG</div>
            <div><strong>SIGERCEP PDRB</strong><small>Sistem Gerak Cepat<br>Pertumbuhan Ekonomi Daerah</small></div>
        </div>
        <div class="sidebar-kicker">Navigasi</div>
        <nav class="sidebar-nav">
            <a href="#ringkasan">Ringkasan utama</a>
            <a href="#tren">Tren pertumbuhan</a>
            <a href="#kontribusi">Kontribusi sektor</a>
            <a href="#sinyal">Sinyal cepat</a>
            <a href="#tabel">Tabel data</a>
        </nav>
        <div class="sidebar-kicker">Periode analisis</div>
        """,
        unsafe_allow_html=True,
    )
    selected_period = st.selectbox("Pilih periode", PERIODS, index=len(PERIODS) - 1, label_visibility="collapsed")
    st.markdown(
        """
        <div class="sidebar-note">
            <span>Cakupan data</span>
            <strong>2022 — Triwulan I 2026</strong>
            <p>Lima tabel analisis untuk PDRB dan 17 lapangan usaha. Harga konstan menggunakan tahun dasar 2010.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

period_data = data[data["periode"] == selected_period]
pdrb = period_data[period_data["kode"] == "PDRB"].set_index("tabel")["nilai"]
sectors = period_data[period_data["kode"] != "PDRB"].pivot(
    index=["kode", "lapangan_usaha"], columns="tabel", values="nilai"
).reset_index()

adhb = pdrb.get("ADHB", float("nan"))
adhk = pdrb.get("ADHK", float("nan"))
yoy = pdrb.get("Y-on-Y", float("nan"))
qoq = pdrb.get("Q-to-Q", float("nan"))

top_contributor = extreme_row(sectors, "Distribusi")
top_yoy = extreme_row(sectors, "Y-on-Y")
lowest_qoq = extreme_row(sectors, "Q-to-Q", largest=False)

st.markdown('<span id="ringkasan" class="section-anchor"></span>', unsafe_allow_html=True)
st.markdown(
    f"""
    <header class="topbar">
        <div class="top-brand">
            <div class="top-logo">SG</div>
            <div><strong>SIGERCEP PDRB</strong><span>Sistem Gerak Cepat Pertumbuhan Ekonomi Daerah</span></div>
        </div>
        <div class="top-badges">
            <span class="top-pill">6101 · Kabupaten Sambas</span>
            <span class="top-pill">Data BPS · Tahun dasar 2010</span>
        </div>
    </header>

    <section class="hero-grid">
        <article class="hero-main">
            <div class="hero-content">
                <div class="eyebrow"><span>Dashboard ekonomi daerah</span><span class="fresh">Data terbaru tersedia</span></div>
                <h1>Pertumbuhan ekonomi Kabupaten Sambas dalam satu kendali.</h1>
                <p>Pantau nilai PDRB, kontribusi 17 lapangan usaha, dan sinyal perubahan ekonomi secara cepat untuk mendukung keputusan perangkat daerah.</p>
                <div class="hero-actions">
                    <a class="hero-action" href="#sinyal">Lihat sinyal cepat</a>
                    <a class="hero-action secondary" href="#tabel">Jelajahi data periode</a>
                </div>
                <div class="hero-meta">
                    <span><strong>{escape(selected_period)}</strong> periode aktif</span>
                    <span><strong>5 tabel</strong> sumber analisis</span>
                    <span><strong>17 sektor</strong> dipantau</span>
                </div>
            </div>
        </article>

        <article class="signal-card">
            <div class="signal-head">
                <span>Sinyal ekonomi</span>
                <span class="status-badge {status_tone(yoy)}">{escape(status(yoy))}</span>
            </div>
            <div class="signal-period">{escape(selected_period)}</div>
            <div class="signal-number">{format_percent(yoy)}</div>
            <div class="signal-label">Pertumbuhan y-on-y PDRB ADHK</div>
            <div class="mini-grid">
                <div class="mini-card"><span>Q-to-Q</span><strong>{format_percent(qoq)}</strong></div>
                <div class="mini-card"><span>ADHK</span><strong>Rp{format_id(adhk / 1_000_000)} T</strong></div>
            </div>
            <div class="signal-foot">Angka tahunan menunjukkan realisasi satu tahun penuh; angka 2026 baru mencakup Triwulan I.</div>
        </article>
    </section>
    """,
    unsafe_allow_html=True,
)

cards = "".join(
    [
        indicator_card("01", "PDRB harga berlaku", f"Rp{format_id(adhb / 1_000_000)} T", selected_period),
        indicator_card(
            "02",
            "Kontributor terbesar",
            str(top_contributor["lapangan_usaha"]),
            f"{format_percent(top_contributor['Distribusi'])} dari PDRB",
        ),
        indicator_card(
            "03",
            "Pertumbuhan Y-on-Y tertinggi",
            str(top_yoy["lapangan_usaha"]),
            format_percent(top_yoy["Y-on-Y"]),
        ),
        indicator_card(
            "04",
            "Kontraksi Q-to-Q terdalam",
            str(lowest_qoq["lapangan_usaha"]),
            format_percent(lowest_qoq["Q-to-Q"]),
        ),
    ]
)
st.markdown(f'<section class="indicator-grid">{cards}</section>', unsafe_allow_html=True)

trend = data[
    (data["tabel"] == "Y-on-Y")
    & (data["kode"] == "PDRB")
    & data["periode"].str.startswith("Triwulan")
].copy()
trend = trend.dropna(subset=["nilai"])
trend["Urutan"] = trend["periode"].map({period: index for index, period in enumerate(PERIODS)})
trend = trend.sort_values("Urutan")
trend["Periode"] = trend["periode"].map(short_period)
trend["Pertumbuhan"] = trend["nilai"]
trend["Kondisi"] = trend["Pertumbuhan"].map(lambda value: "Kontraksi" if value < 0 else "Tumbuh")
trend["Sorotan"] = trend["periode"].eq(selected_period)

period_order = trend["Periode"].tolist()
x_axis = alt.X(
    "Periode:N",
    sort=period_order,
    title=None,
    axis=alt.Axis(labelAngle=0, labelColor="#b9d7e9", labelPadding=10, tickSize=0),
)
y_axis = alt.Y(
    "Pertumbuhan:Q",
    title="Pertumbuhan (%)",
    scale=alt.Scale(zero=True, nice=True),
    axis=alt.Axis(
        format=".1f",
        gridColor="#3679a6",
        gridDash=[3, 4],
        labelColor="#b9d7e9",
        titleColor="#dff5ff",
        titlePadding=14,
    ),
)
tooltip = [
    alt.Tooltip("periode:N", title="Periode"),
    alt.Tooltip("Pertumbuhan:Q", title="Pertumbuhan (%)", format=".2f"),
    alt.Tooltip("Kondisi:N", title="Kondisi"),
]
base = alt.Chart(trend).encode(x=x_axis, y=y_axis)
area = base.mark_area(
    interpolate="monotone",
    opacity=0.24,
    color=alt.Gradient(
        gradient="linear",
        stops=[
            alt.GradientStop(color="#79dcfa", offset=0),
            alt.GradientStop(color="#0a6fae", offset=1),
        ],
        x1=1,
        x2=1,
        y1=0,
        y2=1,
    ),
)
line = base.mark_line(interpolate="monotone", color="#9be8ff", strokeWidth=3.5)
points = base.mark_circle(size=105, stroke="#073c68", strokeWidth=2).encode(
    color=alt.Color(
        "Kondisi:N",
        scale=alt.Scale(domain=["Tumbuh", "Kontraksi"], range=["#9be8ff", "#ff9aa2"]),
        legend=None,
    ),
    tooltip=tooltip,
)
zero_line = alt.Chart(pd.DataFrame({"Pertumbuhan": [0]})).mark_rule(
    color="#8fb9d1", strokeDash=[6, 5], strokeWidth=1
).encode(y="Pertumbuhan:Q")
highlight = (
    base.transform_filter(alt.datum.Sorotan)
    .mark_circle(size=270, color="#ffc869", stroke="#fff7e3", strokeWidth=3)
    .encode(tooltip=tooltip)
)
yoy_chart = (
    (area + zero_line + line + points + highlight)
    .properties(height=350, background="transparent")
    .configure_view(stroke=None)
    .configure_axis(domain=False)
)

latest = trend.iloc[-1]
previous = trend.iloc[-2]
peak = trend.loc[trend["Pertumbuhan"].idxmax()]
change = latest["Pertumbuhan"] - previous["Pertumbuhan"]

st.markdown('<span id="tren" class="section-anchor"></span>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-heading">
        <div class="section-kicker">Tren pertumbuhan</div>
        <h2>Jejak pertumbuhan ekonomi triwulanan</h2>
        <p>Perbandingan terhadap triwulan yang sama pada tahun sebelumnya.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
with st.container(border=True):
    st.altair_chart(yoy_chart, theme=None, width="stretch")
    st.markdown(
        f"""
        <div class="trend-stats">
            <div class="trend-stat"><span>Pertumbuhan terbaru</span><strong>{format_percent(latest['Pertumbuhan'])}</strong><small>{escape(latest['Periode'])}</small></div>
            <div class="trend-stat"><span>Perubahan triwulanan</span><strong>{format_id(change)} p.p.</strong><small>Dibanding periode sebelumnya</small></div>
            <div class="trend-stat"><span>Pertumbuhan tertinggi</span><strong>{format_percent(peak['Pertumbuhan'])}</strong><small>{escape(peak['Periode'])}</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

top = sectors.nlargest(7, "Distribusi")[["lapangan_usaha", "Distribusi"]].copy()
top["Label"] = top["Distribusi"].map(lambda value: f"{format_id(value)}%")
contribution_chart = (
    alt.Chart(top)
    .mark_bar(cornerRadiusEnd=8, height=24, color="#78d6f4")
    .encode(
        x=alt.X(
            "Distribusi:Q",
            title="Kontribusi terhadap PDRB (%)",
            axis=alt.Axis(gridColor="#3679a6", labelColor="#b9d7e9", titleColor="#dff5ff"),
        ),
        y=alt.Y(
            "lapangan_usaha:N",
            sort="-x",
            title=None,
            axis=alt.Axis(labelColor="#dff5ff", labelLimit=235, labelPadding=8),
        ),
        tooltip=[
            alt.Tooltip("lapangan_usaha:N", title="Lapangan usaha"),
            alt.Tooltip("Distribusi:Q", title="Kontribusi (%)", format=".2f"),
        ],
    )
    .properties(height=365, background="transparent")
    .configure_view(stroke=None)
    .configure_axis(domain=False)
)

signals = sectors.nsmallest(6, "Q-to-Q")[["kode", "lapangan_usaha", "Q-to-Q"]].copy()
if signals.empty:
    signal_rows = """
    <div class="signal-row">
        <div class="signal-code">—</div>
        <div class="signal-name">Data Q-to-Q belum tersedia untuk periode ini.</div>
        <div class="signal-value"><strong>—</strong><span>Belum tersedia</span></div>
    </div>
    """
else:
    signal_rows = "".join(
        f"""
        <div class="signal-row">
            <div class="signal-code">{escape(str(row.kode))}</div>
            <div class="signal-name">{escape(str(row.lapangan_usaha))}</div>
            <div class="signal-value"><strong>{format_percent(row._2)}</strong><span>{escape(status(row._2))}</span></div>
        </div>
        """
        for row in signals.itertuples(index=False)
    )

left, right = st.columns([1.18, .82], gap="large")
with left:
    st.markdown('<span id="kontribusi" class="section-anchor"></span>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-heading">
            <div class="section-kicker">Struktur ekonomi</div>
            <h2>Kontribusi lapangan usaha</h2>
            <p>Tujuh sektor dengan porsi terbesar pada periode aktif.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.altair_chart(contribution_chart, theme=None, width="stretch")

with right:
    st.markdown('<span id="sinyal" class="section-anchor"></span>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-heading">
            <div class="section-kicker">Sinyal cepat</div>
            <h2>Sektor yang perlu dicermati</h2>
            <p>Enam perubahan Q-to-Q terendah pada periode aktif.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(f'<div class="signal-list">{signal_rows}</div>', unsafe_allow_html=True)

st.markdown('<span id="tabel" class="section-anchor"></span>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-heading">
        <div class="section-kicker">Eksplorasi data</div>
        <h2>Data PDRB lapangan usaha</h2>
        <p>Cari sektor, berpindah tabel, lalu unduh data untuk periode aktif.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
query = st.text_input("Cari lapangan usaha", placeholder="Contoh: pertanian atau konstruksi")

tabs = st.tabs(list(TABLE_LABELS.values()))
for tab, (table_key, table_label) in zip(tabs, TABLE_LABELS.items()):
    with tab:
        table = period_data[period_data["tabel"] == table_key][["kode", "lapangan_usaha", "nilai"]].copy()
        if query:
            table = table[table["lapangan_usaha"].str.contains(query, case=False, na=False)]
        unit = "Juta rupiah" if table_key in {"ADHB", "ADHK"} else "Persen"
        value_column = f"{selected_period} ({unit})"
        table.columns = ["Kode", "Lapangan usaha", value_column]
        if table_key in {"Q-to-Q", "Y-on-Y"}:
            table["Status"] = table[value_column].map(status)
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={value_column: st.column_config.NumberColumn(format="%.2f")},
        )

download = period_data.pivot(index=["kode", "lapangan_usaha"], columns="tabel", values="nilai").reset_index()
csv = download.to_csv(index=False).encode("utf-8-sig")
safe_period = selected_period.lower().replace(" ", "_")
st.download_button(
    "Unduh data periode aktif",
    csv,
    f"sigercep_{safe_period}.csv",
    "text/csv",
    width="stretch",
)

st.markdown(
    """
    <footer class="footer">
        <span><strong>SIGERCEP PDRB Kabupaten Sambas</strong><br>Sistem Gerak Cepat Pertumbuhan Ekonomi Daerah</span>
        <span>Sumber: BPS Kabupaten Sambas · ADHB/ADHK dalam juta rupiah · Tahun dasar 2010</span>
    </footer>
    """,
    unsafe_allow_html=True,
)
