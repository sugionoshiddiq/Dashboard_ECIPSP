import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network

# ------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CSS
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Rekomendasi Produk",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ── SEMBUNYIKAN TOMBOL COLLAPSE SIDEBAR ── */
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"] > div:first-child { resize: none !important; }
    section[data-testid="stSidebar"] {
        min-width: 290px !important;
        max-width: 290px !important;
    }

    /* ── BACKGROUND UTAMA ── */
    .main { background-color: #f0f7f0; }
    [data-testid="stAppViewContainer"] { background-color: #f0f7f0; }
    [data-testid="stHeader"] { background-color: #f0f7f0; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] { background-color: #1a4d2e !important; }
    section[data-testid="stSidebar"] * { color: #b8dcc4 !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: #6aab7e !important; }
    section[data-testid="stSidebar"] .stRadio label { color: #b8dcc4 !important; }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #b8dcc4 !important; }

    /* ── SIDEBAR LOGO ── */
    .sb-logo {
        background-color: #1a4d2e;
        padding: 16px 18px 14px;
        border-bottom: 1px solid #2d6b42;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sb-logo-icon {
        width: 34px; height: 34px;
        background: #4caf73;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .sb-logo-title {
        font-size: 13px;
        font-weight: 600;
        color: #e8f5ec !important;
        line-height: 1.3;
    }

    /* ── SIDEBAR SECTION HEADER ── */
    .sb-section {
        font-size: 10px;
        font-weight: 600;
        color: #5a9e6e !important;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        padding: 12px 16px 6px;
    }

    /* ── SCORECARD SIDEBAR ── */
    .sc-card {
        background: #133524;
        border-radius: 10px;
        padding: 11px 13px;
        margin-bottom: 8px;
        border: 0.5px solid #2d6b42;
        border-left: 3px solid #4caf73;
        position: relative;
    }
    .sc-label {
        font-size: 10px;
        color: #5a9e6e !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 3px;
    }
    .sc-value {
        font-size: 22px;
        font-weight: 600;
        color: #e8f5ec !important;
        line-height: 1.1;
    }
    .sc-rank {
        font-size: 10px;
        color: #6aab7e !important;
        margin-top: 2px;
    }
    .sc-badge {
        display: inline-block;
        background: #1a4d2e;
        border: 0.5px solid #2d6b42;
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 10px;
        color: #4caf73 !important;
        margin-top: 4px;
        font-weight: 500;
    }

    /* ── CARD KONTEN UTAMA ── */
    .main-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 18px;
        border: 0.5px solid #d4e8d4;
    }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #1a4d2e;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 6px;
        border-bottom: 1px solid #eaf3de;
        padding-bottom: 8px;
    }

    /* ── PAGE HEADER ── */
    .page-header {
        background: #ffffff;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 16px;
        border: 0.5px solid #d4e8d4;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .page-title {
        font-size: 16px;
        font-weight: 600;
        color: #1a4d2e;
    }
    .page-sub {
        font-size: 12px;
        color: #639922;
        margin-top: 2px;
    }
    .page-chip {
        background: #eaf3de;
        border: 0.5px solid #c0dd97;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        color: #3b6d11;
        display: inline-block;
    }

    /* ── PRODUK INFO BANNER ── */
    .produk-banner {
        background: #eaf3de;
        border: 0.5px solid #c0dd97;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .produk-banner-icon {
        width: 40px; height: 40px;
        background: #4caf73;
        border-radius: 9px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }
    .produk-banner h3 {
        font-size: 14px;
        font-weight: 600;
        color: #1a4d2e;
        margin: 0 0 3px 0;
    }
    .produk-banner p {
        font-size: 12px;
        color: #639922;
        margin: 0;
    }
    .produk-chip {
        display: inline-block;
        background: #ffffff;
        border: 0.5px solid #97c459;
        border-radius: 4px;
        padding: 2px 9px;
        font-size: 11px;
        color: #3b6d11;
        margin-top: 6px;
        margin-right: 5px;
        font-weight: 500;
    }

    /* ── PROV CARD ── */
    .prov-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 14px;
        border: 0.5px solid #d4e8d4;
        border-top: 3px solid #4caf73;
        margin-bottom: 4px;
    }
    .prov-card h4 {
        font-size: 13px;
        font-weight: 600;
        color: #1a4d2e;
        margin: 0 0 8px 0;
    }
    .prov-metric {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        margin-bottom: 3px;
    }
    .prov-metric .pm-label { color: #888; }
    .prov-metric .pm-val  { font-weight: 600; color: #1a4d2e; }
    .prov-badge {
        background: #eaf3de;
        color: #3b6d11;
        padding: 1px 5px;
        border-radius: 3px;
        font-size: 10px;
        margin-left: 4px;
    }

    /* ── REKOMENDASI TABLE ── */
    .rec-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .rec-count {
        background: #eaf3de;
        border: 0.5px solid #c0dd97;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 12px;
        color: #3b6d11;
        font-weight: 500;
    }

    /* ── PLOTLY TRANSPARENT ── */
    .js-plotly-plot .plotly { background-color: transparent !important; }

    /* ── HIDE STREAMLIT ELEMENTS ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }

    /* ── DIVIDER ── */
    .sb-divider {
        height: 0.5px;
        background: #2d6b42;
        margin: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------
@st.cache_data
def load_data():
    df1 = pd.read_excel("Data Utama.xlsx")
    df2 = pd.read_excel("Data Proximity.xlsx")
    df3 = pd.read_excel("HS4_Reference.xlsx")
    return df1, df2, df3

df1, df2, df3 = load_data()

# ------------------------------------------------------------
# NORMALISASI NAMA KOLOM DF2
# ------------------------------------------------------------
df2.columns = [str(col).strip() for col in df2.columns]

def normalize_column(df, keywords, target_name):
    for col in df.columns:
        if any(keyword in col.lower() for keyword in keywords):
            df.rename(columns={col: target_name}, inplace=True)
            return True
    return False

for kw, tgt in [
    (["provinsi"], "Provinsi"),
    (["produk 1","produk1"], "Produk 1"),
    (["produk 2","produk2"], "Produk 2"),
]:
    if not normalize_column(df2, kw, tgt):
        st.error(f"Kolom '{tgt}' tidak ditemukan. Kolom: {', '.join(df2.columns)}")
        st.stop()

normalize_column(df2, ["chapter 1","chapter1"], "Chapter 1")
normalize_column(df2, ["chapter 2","chapter2"], "Chapter 2")
normalize_column(df2, ["rekomendasi"], "Rekomendasi")
normalize_column(df2, ["rule strength","rule_strength"], "Rule Strength")

for col in ["Provinsi","Produk 1","Produk 2","Rekomendasi"]:
    if col not in df2.columns:
        st.error(f"Kolom '{col}' tidak ada. Kolom tersedia: {', '.join(df2.columns)}")
        st.stop()

# ------------------------------------------------------------
# KONVERSI NUMERIK
# ------------------------------------------------------------
pilar_cols = [
    "Pilar 1 (Institusi)", "Pilar 2 (Infrastruktur)", "Pilar 3 (Adopsi TIK)",
    "Pilar 4 (Stabilitas Ekonomi)", "Pilar 5 (Kesehatan)", "Pilar 6 (Keterampilan)",
    "Pilar 7 (Pasar Produk)", "Pilar 8 (Pasar Tenaga Kerja)", "Pilar 9 (Sistem Keuangan)",
    "Pilar 10 (Ukuran Pasar)", "Pilar 11 (Dinamika Bisnis)", "Pilar 12 (Kapabilitas Inovasi)"
]
for col in ["ICOR","ECI","IDSD"] + pilar_cols:
    if col in df1.columns:
        df1[col] = pd.to_numeric(df1[col], errors='coerce')
if "Proximity" in df2.columns:
    df2["Proximity"] = pd.to_numeric(df2["Proximity"], errors='coerce')

# ------------------------------------------------------------
# PERSIAPAN DATA PROVINSI
# ------------------------------------------------------------
df1_prov = df1[df1["Nama Daerah"] != "NASIONAL"].copy()
df1_prov['rank_ECI']  = df1_prov['ECI'].rank(ascending=False, method='min').astype('Int64')
df1_prov['rank_ICOR'] = df1_prov['ICOR'].rank(ascending=True,  method='min').astype('Int64')
rank_ec_dict  = df1_prov.set_index('Nama Daerah')['rank_ECI'].to_dict()
rank_ic_dict  = df1_prov.set_index('Nama Daerah')['rank_ICOR'].to_dict()

# ------------------------------------------------------------
# PERSIAPAN REFERENSI HS4
# ------------------------------------------------------------
df3_ref = df3.copy()
df3_ref["HS4"] = pd.to_numeric(df3_ref["HS4"], errors="coerce").astype("Int64")
df3_ref["HS2"] = df3_ref["HS4"].astype(str).str.zfill(4).str[:2]
hs4_to_desc    = df3_ref.set_index("HS4")["Description"].to_dict()
hs4_to_chapter = df3_ref.set_index("HS4")["Chapter"].to_dict()


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def make_bar_chart(df_bar, x_col, y_col, highlight=None, title="", x_title="", color_active="#1a4d2e", color_default="#4caf73"):
    colors = []
    opacities = []
    for name in df_bar[y_col]:
        if highlight is None or str(name).upper().strip() == str(highlight).upper().strip():
            colors.append(color_active if highlight else color_default)
            opacities.append(1.0)
        else:
            colors.append("#c8e6c9")
            opacities.append(0.6)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_bar[y_col], x=df_bar[x_col],
        orientation='h',
        marker=dict(color=colors, opacity=opacities),
        text=df_bar[x_col].apply(lambda v: f'{v:.2f}' if pd.notna(v) else ""),
        textposition='outside',
        hoverinfo='y+x'
    ))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title=x_title,
        yaxis=dict(tickfont=dict(size=9)),
        height=480,
        margin=dict(l=0, r=40, t=10, b=10),
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig


def make_radar(values, categories, title=""):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(76,175,115,0.20)',
        line=dict(color='#4caf73', width=2),
        hovertemplate="<b>%{theta}</b><br>Nilai: %{r:.2f}<extra></extra>"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1], tickfont=dict(size=8), gridcolor="#d4e8d4"),
            angularaxis=dict(tickfont=dict(size=10))
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=30, r=30),
        height=240,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def normalize_val(val, vmin, vmax):
    if pd.isna(val) or vmax == vmin:
        return 0
    return round((val - vmin) / (vmax - vmin), 3)


# ============================================================
# 3. SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="sb-logo-icon">📊</div>
        <div class="sb-logo-title">Dashboard<br>Rekomendasi Produk</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Navigasi</div>', unsafe_allow_html=True)
    mode = st.radio(
        "",
        ["🗺️ Analisis Wilayah", "📦 Analisis Produk"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── FILTER BERDASARKAN MODE ──
    if mode == "🗺️ Analisis Wilayah":
        st.markdown('<div class="sb-section">Filter Wilayah</div>', unsafe_allow_html=True)
        daerah_list = sorted(df1["Nama Daerah"].dropna().unique().tolist())
        default_idx = daerah_list.index("NASIONAL") if "NASIONAL" in daerah_list else 0
        selected_daerah = st.selectbox("Nama Daerah", daerah_list, index=default_idx)

        # Hitung metrik
        df1_filtered = df1[df1["Nama Daerah"] == selected_daerah]
        df_rec = df2.copy() if selected_daerah == "NASIONAL" else \
                 df2[df2["Provinsi"].astype(str).str.upper().str.strip()
                     == selected_daerah.upper().strip()].copy()
        df_rec = df_rec[df_rec["Rekomendasi"].notna()].copy()
        df_rec["Rekomendasi"] = pd.to_numeric(df_rec["Rekomendasi"], errors="coerce").astype("Int64")

        if not df1_filtered.empty:
            row_m = df1_filtered.iloc[0]
            eci_val  = row_m["ECI"]
            icor_val = row_m["ICOR"]
            idsd_val = row_m["IDSD"]
            eci_rank  = rank_ec_dict.get(selected_daerah, None) if selected_daerah != "NASIONAL" else None
            icor_rank = rank_ic_dict.get(selected_daerah, None) if selected_daerah != "NASIONAL" else None
        else:
            eci_val = icor_val = idsd_val = np.nan
            eci_rank = icor_rank = None

        total_rek = df_rec["Rekomendasi"].dropna().nunique()
        n_chapter = df_rec.merge(
            df3_ref[["HS4","Chapter"]], left_on="Rekomendasi", right_on="HS4", how="left"
        )["Chapter"].dropna().nunique()

        st.markdown('<div class="sb-section">Indikator Utama</div>', unsafe_allow_html=True)

        def sc(label, value, rank_str=None, badge=None):
            rank_html = f'<div class="sc-rank">{rank_str}</div>' if rank_str else ""
            badge_html = f'<div class="sc-badge">{badge}</div>' if badge else ""
            st.markdown(f"""
            <div class="sc-card">
                <div class="sc-label">{label}</div>
                <div class="sc-value">{value}</div>
                {rank_html}{badge_html}
            </div>""", unsafe_allow_html=True)

        sc("ECI",
           f"{eci_val:.2f}" if not pd.isna(eci_val) else "N/A",
           "Rank nasional",
           f"#{eci_rank} dari {len(df1_prov)} Provinsi" if eci_rank else None)
        sc("ICOR",
           f"{icor_val:.2f}" if not pd.isna(icor_val) else "N/A",
           "Rank nasional",
           f"#{icor_rank} dari {len(df1_prov)} Provinsi" if icor_rank else None)
        sc("IDSD",
           f"{idsd_val:.2f}" if not pd.isna(idsd_val) else "N/A",
           "Skor komposit 12 pilar")
        sc("Produk Rekomendasi",
           str(total_rek),
           "Produk HS4 unik",
           f"{n_chapter} Chapter")

    else:
        st.markdown('<div class="sb-section">Filter Produk</div>', unsafe_allow_html=True)

        filter_by = st.radio(
            "Pilih berdasarkan:",
            ["HS2 (Kelompok Produk)", "Chapter"],
            key="filter_by_produk"
        )

        df2_rek = df2[df2["Rekomendasi"].notna()].copy()
        df2_rek["Rekomendasi"] = pd.to_numeric(df2_rek["Rekomendasi"], errors="coerce").astype("Int64")

        if filter_by == "HS2 (Kelompok Produk)":
            hs2_options = sorted([str(x) for x in df3_ref.dropna(subset=["HS2"])["HS2"].unique()])
            hs2_label_map = {}
            for hs2 in hs2_options:
                subset = df3_ref[df3_ref["HS2"] == hs2]
                if not subset.empty:
                    desc = subset.iloc[0]["Description"]
                    hs2_label_map[hs2] = f"{hs2} – {desc[:38]}..." if len(str(desc)) > 38 else f"{hs2} – {desc}"
                else:
                    hs2_label_map[hs2] = hs2
            hs2_display = [hs2_label_map[h] for h in hs2_options]
            hs2_sel_disp = st.selectbox("Kelompok HS2:", hs2_display)
            hs2_sel = hs2_options[hs2_display.index(hs2_sel_disp)]
            hs4_in_group = df3_ref[df3_ref["HS2"] == hs2_sel]["HS4"].dropna().astype(int).tolist()
            hs4_available = sorted([int(x) for x in
                                    df2_rek[df2_rek["Rekomendasi"].isin(hs4_in_group)]["Rekomendasi"].dropna().unique()])
        else:
            chapter_options = sorted(df3_ref["Chapter"].dropna().unique().tolist())
            sel_chapter = st.selectbox("Chapter:", chapter_options)
            hs4_in_ch = df3_ref[df3_ref["Chapter"] == sel_chapter]["HS4"].dropna().astype(int).tolist()
            hs4_available = sorted([int(x) for x in
                                    df2_rek[df2_rek["Rekomendasi"].isin(hs4_in_ch)]["Rekomendasi"].dropna().unique()])

        if not hs4_available:
            st.warning("Tidak ada produk untuk pilihan ini.")
            produk_selected = None
        else:
            produk_label_map = {
                hs4: f"{hs4} – {hs4_to_desc.get(hs4,'N/A')[:42]}..."
                     if len(str(hs4_to_desc.get(hs4,''))) > 42
                     else f"{hs4} – {hs4_to_desc.get(hs4,'N/A')}"
                for hs4 in hs4_available
            }
            produk_display   = list(produk_label_map.values())
            produk_sel_disp  = st.selectbox("Produk (HS4):", produk_display)
            produk_selected  = hs4_available[produk_display.index(produk_sel_disp)]

        # Scorecard Analisis Produk
        if produk_selected:
            df2_match = df2_rek[df2_rek["Rekomendasi"] == produk_selected]
            prov_count  = df2_match["Provinsi"].dropna().nunique()
            produk_desc = hs4_to_desc.get(produk_selected, "N/A")
            produk_ch   = hs4_to_chapter.get(produk_selected, "N/A")

            st.markdown('<div class="sb-section">Info Produk</div>', unsafe_allow_html=True)

            def sc2(label, value, note=None):
                note_html = f'<div class="sc-rank">{note}</div>' if note else ""
                st.markdown(f"""
                <div class="sc-card">
                    <div class="sc-label">{label}</div>
                    <div class="sc-value">{value}</div>
                    {note_html}
                </div>""", unsafe_allow_html=True)

            sc2("Kode HS4", str(produk_selected),
                str(produk_desc)[:50] + "..." if len(str(produk_desc)) > 50 else str(produk_desc))
            sc2("Provinsi Rekomendasi", str(prov_count), "merekomendasikan produk ini")
            sc2("Chapter", str(produk_ch)[:30] if produk_ch else "N/A")


# ============================================================
# 4. KONTEN UTAMA
# ============================================================

# ── MODE: ANALISIS WILAYAH ──────────────────────────────────
if mode == "🗺️ Analisis Wilayah":

    # Page header
    rank_txt = f"Rank ECI #{eci_rank}" if eci_rank else ""
    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-title">📍 {selected_daerah}</div>
            <div class="page-sub">Economic Complexity · ICOR · IDSD Score</div>
        </div>
        <div>
            <span class="page-chip">📅 2024</span>&nbsp;
            <span class="page-chip">🗺️ {len(df1_prov)} Provinsi</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Card 1: Tiga Barchart ──
    with st.container():
        st.markdown('<div class="main-card"><div class="card-title">📊 Perbandingan Indikator per Provinsi</div>', unsafe_allow_html=True)
        col_eci, col_icor, col_idsd = st.columns(3)

        with col_eci:
            st.caption("**ECI per Provinsi**")
            sort_eci = st.selectbox("Urutkan ECI:", ["Terbesar di atas","Terkecil di atas","Abjad"], key="sort_eci")
            df_ecibar = df1_prov[['Nama Daerah','ECI']].dropna(subset=['ECI'])
            if sort_eci == "Terbesar di atas":    df_ecibar = df_ecibar.sort_values('ECI', ascending=False)
            elif sort_eci == "Terkecil di atas":  df_ecibar = df_ecibar.sort_values('ECI', ascending=True)
            else:                                  df_ecibar = df_ecibar.sort_values('Nama Daerah')
            hl = None if selected_daerah == "NASIONAL" else selected_daerah
            st.plotly_chart(make_bar_chart(df_ecibar, 'ECI', 'Nama Daerah', highlight=hl, x_title='ECI'),
                            use_container_width=True, key="eci_bar")

        with col_icor:
            st.caption("**ICOR per Provinsi**")
            sort_icor = st.selectbox("Urutkan ICOR:", ["Terkecil di atas","Terbesar di atas","Abjad"], key="sort_icor")
            df_icorbar = df1_prov[['Nama Daerah','ICOR']].dropna(subset=['ICOR'])
            if sort_icor == "Terbesar di atas":   df_icorbar = df_icorbar.sort_values('ICOR', ascending=False)
            elif sort_icor == "Terkecil di atas": df_icorbar = df_icorbar.sort_values('ICOR', ascending=True)
            else:                                  df_icorbar = df_icorbar.sort_values('Nama Daerah')
            st.plotly_chart(make_bar_chart(df_icorbar, 'ICOR', 'Nama Daerah', highlight=hl, x_title='ICOR'),
                            use_container_width=True, key="icor_bar")

        with col_idsd:
            st.caption("**IDSD per Pilar**")
            pilar_y     = [f"Pilar {i}" for i in range(1,13)]
            pilar_inner = ["Institusi","Infrastruktur","Adopsi TIK","Stabilitas Ekonomi",
                           "Kesehatan","Keterampilan","Pasar Produk","Pasar Tenaga Kerja",
                           "Sistem Keuangan","Ukuran Pasar","Dinamika Bisnis","Kapabilitas Inovasi"]
            if not df1_filtered.empty:
                rata_pilar = df1_filtered[pilar_cols].mean().values if len(df1_filtered) > 1 \
                             else [df1_filtered.iloc[0][c] for c in pilar_cols]
                df_pilar = pd.DataFrame({"Pilar": pilar_y, "Nilai": rata_pilar, "Nama": pilar_inner})
                sort_pilar = st.selectbox("Urutkan IDSD:", ["Urutan Pilar","Nilai Terbesar","Nilai Terkecil"], key="sort_pilar")
                if sort_pilar == "Nilai Terbesar":  df_pilar = df_pilar.sort_values("Nilai", ascending=False)
                elif sort_pilar == "Nilai Terkecil": df_pilar = df_pilar.sort_values("Nilai", ascending=True)

                fig_pilar = go.Figure()
                fig_pilar.add_trace(go.Bar(
                    y=df_pilar["Pilar"], x=df_pilar["Nilai"],
                    text=df_pilar["Nama"],
                    textposition='inside', insidetextanchor='start',
                    marker_color="#4caf73", orientation='h'
                ))
                fig_pilar.update_yaxes(autorange="reversed")
                fig_pilar.update_layout(
                    xaxis_title="Nilai", showlegend=False,
                    margin=dict(l=0, r=10, t=10, b=10),
                    plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', height=480
                )
                st.plotly_chart(fig_pilar, use_container_width=True, key="idsd_pilar")
            else:
                st.info("Pilih daerah untuk melihat data IDSD.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Card 2: Tabel Rekomendasi & Donut ──
    with st.container():
        st.markdown('<div class="main-card"><div class="card-title">📦 Rekomendasi Produk</div>', unsafe_allow_html=True)

        if df_rec.empty:
            st.info("Tidak ada rekomendasi untuk wilayah terpilih.")
        else:
            df3_lookup = df3.copy()
            df3_lookup["HS4"] = pd.to_numeric(df3_lookup["HS4"], errors="coerce").astype("Int64")

            produk_series = pd.concat([df_rec["Produk 1"].astype(str), df_rec["Produk 2"].astype(str)])
            degree_df = produk_series.value_counts().reset_index()
            degree_df.columns = ["HS4","Jumlah Koneksi"]
            degree_df["HS4"] = degree_df["HS4"].astype(str)

            tabel_full = (
                df_rec[["Rekomendasi"]].drop_duplicates()
                .merge(df3_lookup[["HS4","Description","Chapter"]], left_on="Rekomendasi", right_on="HS4", how="left")
                [["Rekomendasi","Description","Chapter"]]
                .rename(columns={"Rekomendasi":"Produk Rekomendasi"})
            )
            tabel_full["Produk Rekomendasi"] = tabel_full["Produk Rekomendasi"].astype(str)
            tabel_full = tabel_full.merge(degree_df, left_on="Produk Rekomendasi", right_on="HS4", how="left").drop(columns=["HS4"])
            tabel_full["Jumlah Koneksi"] = tabel_full["Jumlah Koneksi"].fillna(0).astype(int)
            tabel_full = tabel_full.sort_values("Produk Rekomendasi").drop_duplicates(subset=["Produk Rekomendasi"])

            chapter_list = sorted(tabel_full["Chapter"].fillna("Unknown").unique())
            sel_ch = st.selectbox("Filter Chapter:", ["Semua Chapter"] + chapter_list, key="filter_chapter_w")
            tabel_disp = tabel_full if sel_ch == "Semua Chapter" else \
                         tabel_full[tabel_full["Chapter"].fillna("Unknown") == sel_ch]

            col_tbl, col_donut = st.columns([1.2, 0.8])

            with col_tbl:
                st.markdown(f"""
                <div class="rec-header">
                    <span style="font-size:13px;font-weight:600;color:#1a4d2e;">Tabel Rekomendasi</span>
                    <span class="rec-count">{len(tabel_disp)} produk · {selected_daerah}</span>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(
                    tabel_disp[["Produk Rekomendasi","Description","Chapter","Jumlah Koneksi"]],
                    use_container_width=True, hide_index=True, height=350
                )

            with col_donut:
                st.markdown('<div style="font-size:13px;font-weight:600;color:#1a4d2e;margin-bottom:8px;">Distribusi Chapter</div>', unsafe_allow_html=True)
                if not tabel_disp.empty:
                    ch_counts = tabel_disp["Chapter"].fillna("Unknown").value_counts()
                    if len(ch_counts) > 8:
                        top = ch_counts.head(8)
                        donut_data = pd.concat([top, pd.Series({"Lainnya": ch_counts.iloc[8:].sum()})])
                    else:
                        donut_data = ch_counts
                    colors_donut = ["#4caf73","#1a4d2e","#97c459","#1d9e75","#2e7d32",
                                    "#a5d6a7","#66bb6a","#388e3c","#81c784","#43a047"]
                    fig_donut = go.Figure()
                    fig_donut.add_trace(go.Pie(
                        labels=donut_data.index, values=donut_data.values,
                        hole=0.58,
                        marker=dict(colors=colors_donut[:len(donut_data)]),
                        textinfo="percent",
                        hovertemplate="<b>%{label}</b><br>Produk: %{value}<br>%{percent}<extra></extra>",
                        pull=[0.04]*len(donut_data), sort=True
                    ))
                    fig_donut.update_layout(
                        annotations=[dict(text=f"{donut_data.sum()}<br><span style='font-size:11px'>Produk</span>",
                                          x=0.5, y=0.5, font_size=18, showarrow=False)],
                        legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
                        height=360, margin=dict(t=10, b=60, l=10, r=10),
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_donut, use_container_width=True, key="donut_w")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Card 3: Network Diagram ──
    with st.container():
        st.markdown('<div class="main-card"><div class="card-title">🕸️ Network Diagram Produk Rekomendasi</div>', unsafe_allow_html=True)

        df_net = df2.copy() if selected_daerah == "NASIONAL" else \
                 df2[df2["Provinsi"].astype(str).str.upper().str.strip()
                     == selected_daerah.upper().strip()].copy()
        df_net = df_net[df_net["Rekomendasi"].notna()].copy()

        if df_net.empty:
            st.info("Tidak ada data untuk network diagram.")
        else:
            node_chapter = {}
            for _, row in df_net.iterrows():
                p1, ch1 = str(row["Produk 1"]), row.get("Chapter 1", None)
                if p1 not in node_chapter and pd.notna(ch1): node_chapter[p1] = str(ch1)
            for _, row in df_net.iterrows():
                p2, ch2 = str(row["Produk 2"]), row.get("Chapter 2", None)
                if p2 not in node_chapter and pd.notna(ch2): node_chapter[p2] = str(ch2)
            all_nodes = set(df_net["Produk 1"].unique()) | set(df_net["Produk 2"].unique())
            for node in all_nodes:
                if str(node) not in node_chapter: node_chapter[str(node)] = "Unknown"

            unique_chapters = sorted(set(node_chapter.values()))
            palette = px.colors.qualitative.Plotly + px.colors.qualitative.Set1 + px.colors.qualitative.Set2
            while len(palette) < len(unique_chapters): palette += palette
            ch_color_map = dict(zip(unique_chapters, palette[:len(unique_chapters)]))

            net = Network(height="650px", width="100%", bgcolor="#f8fdf8", font_color="#1a4d2e")
            net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=250,
                           spring_strength=0.05, damping=0.09)

            for node in all_nodes:
                ns   = str(node)
                ch   = node_chapter.get(ns, "Unknown")
                warna = ch_color_map.get(ch, "#cccccc")
                desc  = df3[df3["HS4"] == node]["Description"]
                lbl   = desc.values[0] if not desc.empty else ns
                net.add_node(ns, label=ns, title=f"{lbl} | Chapter: {ch}",
                             color=warna, size=25, shape="dot",
                             font={"size": 22, "face": "arial"})

            def map_edge_color(rule_str):
                if pd.isna(rule_str): return None
                s = str(rule_str).strip().replace(" ","").replace(",",".")
                if s.startswith(">0.6"):                     return "#e53935"
                elif s.startswith(">0.55") and "0.6" in s:  return "#fbc02d"
                elif s.startswith(">0.5")  and "0.55" in s: return "#43a047"
                else:                                        return "#bdbdbd"

            edge_count = 0
            for _, row in df_net.iterrows():
                ec = map_edge_color(row.get("Rule Strength", None))
                if ec is None: continue
                net.add_edge(str(row["Produk 1"]), str(row["Produk 2"]),
                             title=f"Rule Strength: {str(row.get('Rule Strength','')).strip()}",
                             color=ec)
                edge_count += 1

            net.save_graph("network_temp.html")
            with open("network_temp.html", "r", encoding="utf-8") as f:
                html_net = f.read()

            col_info1, col_info2, col_info3 = st.columns(3)
            col_info1.metric("Jumlah Node", len(all_nodes))
            col_info2.metric("Jumlah Edge", edge_count)
            col_info3.metric("Jumlah Chapter", len(unique_chapters))

            # Legenda warna edge
            st.markdown("""
            <div style="display:flex;gap:16px;margin:8px 0 10px;flex-wrap:wrap">
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#e53935;border-radius:50%;vertical-align:middle;margin-right:4px"></span>Rule Strength &gt; 0.6
                </span>
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#fbc02d;border-radius:50%;vertical-align:middle;margin-right:4px"></span>Rule Strength 0.55–0.6
                </span>
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#43a047;border-radius:50%;vertical-align:middle;margin-right:4px"></span>Rule Strength 0.5–0.55
                </span>
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#bdbdbd;border-radius:50%;vertical-align:middle;margin-right:4px"></span>Lainnya
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.components.v1.html(html_net, height=650, scrolling=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ── MODE: ANALISIS PRODUK ───────────────────────────────────
else:
    if produk_selected is None:
        st.info("Silakan pilih produk dari sidebar untuk melihat analisis.")
        st.stop()

    produk_desc    = hs4_to_desc.get(produk_selected, "N/A")
    produk_chapter = hs4_to_chapter.get(produk_selected, "N/A")

    df2_rek2 = df2.copy()
    df2_rek2["Rekomendasi"] = pd.to_numeric(df2_rek2["Rekomendasi"], errors="coerce").astype("Int64")
    prov_list = sorted([str(p).strip() for p in
                        df2_rek2[df2_rek2["Rekomendasi"] == produk_selected]["Provinsi"].dropna().unique()])

    # Page header
    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-title">📦 Analisis Produk Rekomendasi</div>
            <div class="page-sub">Persebaran provinsi berdasarkan produk HS4</div>
        </div>
        <span class="page-chip">📅 2024</span>
    </div>
    """, unsafe_allow_html=True)

    # Banner produk
    st.markdown(f"""
    <div class="produk-banner">
        <div class="produk-banner-icon">📦</div>
        <div>
            <h3>{produk_selected} — {produk_desc}</h3>
            <p>Chapter: {produk_chapter}</p>
            <span class="produk-chip">📍 {len(prov_list)} Provinsi</span>
            <span class="produk-chip">{produk_chapter}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not prov_list:
        st.warning("Tidak ada provinsi yang merekomendasikan produk ini.")
        st.stop()

    # ── Card 1: Tiga Barchart ECI/ICOR/IDSD untuk prov-prov rekomendasi ──
    with st.container():
        st.markdown('<div class="main-card"><div class="card-title">📊 Perbandingan Indikator Provinsi Rekomendasi</div>', unsafe_allow_html=True)

        df_prov_match = df1_prov[
            df1_prov["Nama Daerah"].astype(str).str.upper().str.strip()
            .isin([p.upper().strip() for p in prov_list])
        ].copy()

        col_e, col_i, col_d = st.columns(3)

        with col_e:
            st.caption("**ECI**")
            sort_e = st.selectbox("Urutkan:", ["Terbesar di atas","Terkecil di atas","Abjad"], key="sort_eci_p")
            df_e = df_prov_match[['Nama Daerah','ECI']].dropna(subset=['ECI'])
            if sort_e == "Terbesar di atas":   df_e = df_e.sort_values('ECI', ascending=False)
            elif sort_e == "Terkecil di atas": df_e = df_e.sort_values('ECI', ascending=True)
            else:                               df_e = df_e.sort_values('Nama Daerah')
            st.plotly_chart(make_bar_chart(df_e, 'ECI', 'Nama Daerah', highlight=None,
                                           color_active="#4caf73", color_default="#4caf73", x_title='ECI'),
                            use_container_width=True, key="eci_bar_p")

        with col_i:
            st.caption("**ICOR**")
            sort_i = st.selectbox("Urutkan:", ["Terkecil di atas","Terbesar di atas","Abjad"], key="sort_icor_p")
            df_ic = df_prov_match[['Nama Daerah','ICOR']].dropna(subset=['ICOR'])
            if sort_i == "Terbesar di atas":   df_ic = df_ic.sort_values('ICOR', ascending=False)
            elif sort_i == "Terkecil di atas": df_ic = df_ic.sort_values('ICOR', ascending=True)
            else:                               df_ic = df_ic.sort_values('Nama Daerah')
            st.plotly_chart(make_bar_chart(df_ic, 'ICOR', 'Nama Daerah', highlight=None,
                                           color_active="#4caf73", color_default="#4caf73", x_title='ICOR'),
                            use_container_width=True, key="icor_bar_p")

        with col_d:
            st.caption("**IDSD**")
            sort_d = st.selectbox("Urutkan:", ["Terbesar di atas","Terkecil di atas","Abjad"], key="sort_idsd_p")
            df_id = df_prov_match[['Nama Daerah','IDSD']].dropna(subset=['IDSD'])
            if sort_d == "Terbesar di atas":   df_id = df_id.sort_values('IDSD', ascending=False)
            elif sort_d == "Terkecil di atas": df_id = df_id.sort_values('IDSD', ascending=True)
            else:                               df_id = df_id.sort_values('Nama Daerah')
            st.plotly_chart(make_bar_chart(df_id, 'IDSD', 'Nama Daerah', highlight=None,
                                           color_active="#4caf73", color_default="#4caf73", x_title='IDSD'),
                            use_container_width=True, key="idsd_bar_p")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Card 2: Kartu Provinsi + Radar ──
    with st.container():
        st.markdown(f'<div class="main-card"><div class="card-title">📍 Kartu Provinsi Rekomendasi — {len(prov_list)} Provinsi</div>', unsafe_allow_html=True)

        eci_min  = df1_prov["ECI"].min();  eci_max  = df1_prov["ECI"].max()
        icor_min = df1_prov["ICOR"].min(); icor_max = df1_prov["ICOR"].max()
        idsd_min = df1_prov["IDSD"].min(); idsd_max = df1_prov["IDSD"].max()

        rows = [prov_list[i:i+3] for i in range(0, len(prov_list), 3)]
        for row_provs in rows:
            cols = st.columns(3)
            for ci, prov in enumerate(row_provs):
                with cols[ci]:
                    df1m = df1_prov[
                        df1_prov["Nama Daerah"].astype(str).str.upper().str.strip()
                        == prov.upper().strip()
                    ]
                    if df1m.empty:
                        st.markdown(f"""
                        <div class="prov-card">
                            <h4>📍 {prov}</h4>
                            <p style="color:#888;font-size:12px;">Data tidak tersedia.</p>
                        </div>""", unsafe_allow_html=True)
                        continue

                    rd = df1m.iloc[0]
                    ev = rd["ECI"];  iv = rd["ICOR"]; dv = rd["IDSD"]
                    en = normalize_val(ev, eci_min, eci_max)
                    in_ = 1 - normalize_val(iv, icor_min, icor_max)
                    dn = normalize_val(dv, idsd_min, idsd_max)
                    er = rank_ec_dict.get(rd["Nama Daerah"], "-")
                    ir = rank_ic_dict.get(rd["Nama Daerah"], "-")

                    ed = f"{ev:.2f}" if not pd.isna(ev) else "N/A"
                    id_ = f"{iv:.2f}" if not pd.isna(iv) else "N/A"
                    dd = f"{dv:.2f}" if not pd.isna(dv) else "N/A"

                    st.markdown(f"""
                    <div class="prov-card">
                        <h4>📍 {prov}</h4>
                        <div class="prov-metric"><span class="pm-label">ECI</span>
                            <span class="pm-val">{ed}<span class="prov-badge">#{er}</span></span></div>
                        <div class="prov-metric"><span class="pm-label">ICOR</span>
                            <span class="pm-val">{id_}<span class="prov-badge">#{ir}</span></span></div>
                        <div class="prov-metric"><span class="pm-label">IDSD</span>
                            <span class="pm-val">{dd}</span></div>
                    </div>""", unsafe_allow_html=True)

                    categories = ["ECI", "ICOR\n(inversi)", "IDSD"]
                    st.plotly_chart(
                        make_radar([en, in_, dn], categories),
                        use_container_width=True,
                        key=f"radar_{prov}_{produk_selected}"
                    )

            for empty_c in range(len(row_provs), 3):
                cols[empty_c].empty()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Card 3: Network Diagram ──
    with st.container():
        st.markdown('<div class="main-card"><div class="card-title">🕸️ Network Diagram Produk Rekomendasi</div>', unsafe_allow_html=True)

        # Ambil semua baris di df2 yang melibatkan produk ini (sebagai Produk 1, Produk 2, atau Rekomendasi)
        df_net_p = df2.copy()
        df_net_p["Rekomendasi"] = pd.to_numeric(df_net_p["Rekomendasi"], errors="coerce").astype("Int64")

        # Filter: baris yang berhubungan dengan produk_selected di kolom Rekomendasi
        df_net_p = df_net_p[df_net_p["Rekomendasi"] == produk_selected].copy()

        if df_net_p.empty:
            # Fallback: filter di Produk 1 atau Produk 2
            df_net_p = df2[
                (df2["Produk 1"].astype(str) == str(produk_selected)) |
                (df2["Produk 2"].astype(str) == str(produk_selected))
            ].copy()

        if df_net_p.empty:
            st.info("Tidak ada data network untuk produk ini.")
        else:
            node_chapter2 = {}
            for _, row in df_net_p.iterrows():
                p1, ch1 = str(row["Produk 1"]), row.get("Chapter 1", None)
                if p1 not in node_chapter2 and pd.notna(ch1): node_chapter2[p1] = str(ch1)
            for _, row in df_net_p.iterrows():
                p2, ch2 = str(row["Produk 2"]), row.get("Chapter 2", None)
                if p2 not in node_chapter2 and pd.notna(ch2): node_chapter2[p2] = str(ch2)
            all_nodes2 = set(df_net_p["Produk 1"].unique()) | set(df_net_p["Produk 2"].unique())
            for node in all_nodes2:
                if str(node) not in node_chapter2: node_chapter2[str(node)] = "Unknown"

            unique_ch2 = sorted(set(node_chapter2.values()))
            palette2   = px.colors.qualitative.Plotly + px.colors.qualitative.Set1 + px.colors.qualitative.Set2
            while len(palette2) < len(unique_ch2): palette2 += palette2
            ch_color2  = dict(zip(unique_ch2, palette2[:len(unique_ch2)]))

            net2 = Network(height="620px", width="100%", bgcolor="#f8fdf8", font_color="#1a4d2e")
            net2.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=220,
                            spring_strength=0.05, damping=0.09)

            for node in all_nodes2:
                ns    = str(node)
                ch    = node_chapter2.get(ns, "Unknown")
                warna = ch_color2.get(ch, "#cccccc")
                # Highlight produk utama
                if str(node) == str(produk_selected):
                    warna = "#1a4d2e"
                desc2 = df3[df3["HS4"] == node]["Description"]
                lbl2  = desc2.values[0] if not desc2.empty else ns
                size  = 40 if str(node) == str(produk_selected) else 25
                net2.add_node(ns, label=ns, title=f"{lbl2} | Chapter: {ch}",
                              color=warna, size=size, shape="dot",
                              font={"size": 22, "face": "arial"})

            def map_edge_color2(rule_str):
                if pd.isna(rule_str): return None
                s = str(rule_str).strip().replace(" ","").replace(",",".")
                if s.startswith(">0.6"):                     return "#e53935"
                elif s.startswith(">0.55") and "0.6" in s:  return "#fbc02d"
                elif s.startswith(">0.5")  and "0.55" in s: return "#43a047"
                else:                                        return "#bdbdbd"

            edge_count2 = 0
            for _, row in df_net_p.iterrows():
                ec2 = map_edge_color2(row.get("Rule Strength", None))
                if ec2 is None: continue
                net2.add_edge(str(row["Produk 1"]), str(row["Produk 2"]),
                              title=f"Rule Strength: {str(row.get('Rule Strength','')).strip()}",
                              color=ec2)
                edge_count2 += 1

            net2.save_graph("network_temp2.html")
            with open("network_temp2.html", "r", encoding="utf-8") as f:
                html_net2 = f.read()

            col_n1, col_n2, col_n3 = st.columns(3)
            col_n1.metric("Jumlah Node", len(all_nodes2))
            col_n2.metric("Jumlah Edge", edge_count2)
            col_n3.metric("Produk Utama", str(produk_selected))

            st.markdown("""
            <div style="display:flex;gap:16px;margin:8px 0 10px;flex-wrap:wrap">
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#1a4d2e;border-radius:50%;vertical-align:middle;margin-right:4px"></span>Produk Utama (dipilih)
                </span>
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#e53935;border-radius:50%;vertical-align:middle;margin-right:4px"></span>Rule Strength &gt; 0.6
                </span>
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#fbc02d;border-radius:50%;vertical-align:middle;margin-right:4px"></span>0.55–0.6
                </span>
                <span style="font-size:11px;color:#555;">
                    <span style="display:inline-block;width:12px;height:12px;background:#43a047;border-radius:50%;vertical-align:middle;margin-right:4px"></span>0.5–0.55
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.components.v1.html(html_net2, height=620, scrolling=True)

        st.markdown('</div>', unsafe_allow_html=True)
