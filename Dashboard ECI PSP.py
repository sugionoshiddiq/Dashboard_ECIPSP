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
    page_title="Dashboard Multi Indikator Ekonomi",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ── SEMBUNYIKAN & KUNCI SIDEBAR ── */
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"] > div:first-child { resize: none !important; }
    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }

    /* ── BACKGROUND ── */
    .main { background-color: #b3e5fc; }
    body  { background-color: #b3e5fc; }


    /* ── CARD ── */
    .card {
        background-color: #e8f5e9;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .card h3 {
        color: #2e7d32;
        font-weight: bold;
        margin-top: 0;
    }

    /* ── PLOTLY ── */
    .js-plotly-plot .plotly { background-color: transparent !important; }

    /* ── SIDEBAR METRIC ── */
    .sidebar-metric {
        background-color: #e8f5e9;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .sidebar-metric .label {
        font-size: 18px;
        color: #555;
        margin-bottom: 5px;
    }
    .sidebar-metric .value {
        font-size: 28px;
        font-weight: bold;
        color: #2e7d32;
    }

    /* ── PROV CARD ── */
    .prov-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.10);
        border-left: 5px solid #43a047;
    }
    .prov-card h4 {
        color: #2e7d32;
        margin-top: 0;
        margin-bottom: 8px;
        font-size: 16px;
        font-weight: bold;
    }
    .produk-badge {
        display: inline-block;
        background-color: #e8f5e9;
        border-radius: 8px;
        padding: 4px 10px;
        font-size: 13px;
        color: #2e7d32;
        margin-bottom: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------
df1 = pd.read_excel("Data Utama.xlsx")
df2 = pd.read_excel("Data Proximity.xlsx")
df3 = pd.read_excel("HS4_Reference.xlsx")

# ------------------------------------------------------------
# NORMALISASI NAMA KOLOM DI DF2
# ------------------------------------------------------------
df2.columns = [str(col).strip() for col in df2.columns]

def normalize_column(df, keywords, target_name):
    for col in df.columns:
        if any(keyword in col.lower() for keyword in keywords):
            df.rename(columns={col: target_name}, inplace=True)
            return True
    return False

if not normalize_column(df2, ["provinsi"], "Provinsi"):
    st.error("Kolom 'Provinsi' tidak ditemukan. Kolom yang ada: " + ", ".join(df2.columns))
    st.stop()

if not normalize_column(df2, ["produk 1", "produk1"], "Produk 1"):
    st.error("Kolom 'Produk 1' tidak ditemukan. Kolom yang ada: " + ", ".join(df2.columns))
    st.stop()

if not normalize_column(df2, ["produk 2", "produk2"], "Produk 2"):
    st.error("Kolom 'Produk 2' tidak ditemukan. Kolom yang ada: " + ", ".join(df2.columns))
    st.stop()

normalize_column(df2, ["chapter 1", "chapter1"], "Chapter 1")
normalize_column(df2, ["chapter 2", "chapter2"], "Chapter 2")
normalize_column(df2, ["rekomendasi"], "Rekomendasi")

for col in ["Provinsi", "Produk 1", "Produk 2", "Rekomendasi"]:
    if col not in df2.columns:
        st.error(f"Kolom '{col}' tidak ada. Kolom yang tersedia: {', '.join(df2.columns)}")
        st.stop()

# ------------------------------------------------------------
# KONVERSI DATA NUMERIK
# ------------------------------------------------------------
pilar_cols = [
    "Pilar 1 (Institusi)", "Pilar 2 (Infrastruktur)", "Pilar 3 (Adopsi TIK)",
    "Pilar 4 (Stabilitas Ekonomi)", "Pilar 5 (Kesehatan)", "Pilar 6 (Keterampilan)",
    "Pilar 7 (Pasar Produk)", "Pilar 8 (Pasar Tenaga Kerja)", "Pilar 9 (Sistem Keuangan)",
    "Pilar 10 (Ukuran Pasar)", "Pilar 11 (Dinamika Bisnis)", "Pilar 12 (Kapabilitas Inovasi)"
]

kolom_numerik_df1 = ["ICOR", "ECI", "IDSD"] + pilar_cols
for col in kolom_numerik_df1:
    if col in df1.columns:
        df1[col] = pd.to_numeric(df1[col], errors='coerce')

if "Proximity" in df2.columns:
    df2["Proximity"] = pd.to_numeric(df2["Proximity"], errors='coerce')

# ------------------------------------------------------------
# PERSIAPAN DATA PROVINSI (TANPA NASIONAL)
# ------------------------------------------------------------
df1_prov = df1[df1["Nama Daerah"] != "NASIONAL"].copy()
df1_prov['rank_ECI']  = df1_prov['ECI'].rank(ascending=False, method='min').astype('Int64')
df1_prov['rank_ICOR'] = df1_prov['ICOR'].rank(ascending=True,  method='min').astype('Int64')

rank_ec_dict = df1_prov.set_index('Nama Daerah')['rank_ECI'].to_dict()
rank_ic_dict = df1_prov.set_index('Nama Daerah')['rank_ICOR'].to_dict()

# ------------------------------------------------------------
# PERSIAPAN REFERENSI HS4 (df3)
# ------------------------------------------------------------
df3_ref = df3.copy()
df3_ref["HS4"] = pd.to_numeric(df3_ref["HS4"], errors="coerce").astype("Int64")
df3_ref["HS2"] = df3_ref["HS4"].astype(str).str.zfill(4).str[:2]
hs4_to_desc    = df3_ref.set_index("HS4")["Description"].to_dict()
hs4_to_chapter = df3_ref.set_index("HS4")["Chapter"].to_dict()
hs2_labels = (
    df3_ref.dropna(subset=["HS2"])
    .groupby("HS2").first().reset_index()[["HS2", "Description", "Chapter"]]
)

# ------------------------------------------------------------
# 3. SIDEBAR — MODE SELECTION
# ------------------------------------------------------------
st.sidebar.header("Mode Analisis")

mode = st.sidebar.radio(
    "Pilih Mode",
    ["🗺️ Analisis Wilayah", "📦 Analisis Produk"],
    index=0
)

st.sidebar.markdown("---")

# ============================================================
# MODE: ANALISIS PRODUK
# ============================================================
if mode == "📦 Analisis Produk":

    st.sidebar.subheader("Filter Produk")

    filter_by = st.sidebar.radio(
        "Pilih Produk Berdasarkan:",
        ["HS2 (Kelompok Produk)", "Chapter"],
        key="filter_by_produk"
    )

    if filter_by == "HS2 (Kelompok Produk)":
        hs2_options = sorted([str(x) for x in df3_ref.dropna(subset=["HS2"])["HS2"].unique()])
        hs2_label_map = {}
        for hs2 in hs2_options:
            subset = df3_ref[df3_ref["HS2"] == hs2]
            if not subset.empty:
                desc = subset.iloc[0]["Description"]
                hs2_label_map[hs2] = f"{hs2} – {desc[:40]}..." if len(str(desc)) > 40 else f"{hs2} – {desc}"
            else:
                hs2_label_map[hs2] = hs2

        hs2_display = [hs2_label_map[h] for h in hs2_options]
        hs2_selected_display = st.sidebar.selectbox("Pilih Kelompok HS2:", hs2_display)
        hs2_selected = hs2_options[hs2_display.index(hs2_selected_display)]
        hs4_in_group = df3_ref[df3_ref["HS2"] == hs2_selected]["HS4"].dropna().astype(int).tolist()

        df2_rek = df2[df2["Rekomendasi"].notna()].copy()
        df2_rek["Rekomendasi"] = pd.to_numeric(df2_rek["Rekomendasi"], errors="coerce").astype("Int64")
        hs4_available = sorted([int(x) for x in
                                df2_rek[df2_rek["Rekomendasi"].isin(hs4_in_group)]["Rekomendasi"].dropna().unique()])

        if len(hs4_available) == 0:
            st.sidebar.warning("Tidak ada produk HS4 dari kelompok ini yang direkomendasikan.")
            produk_selected = None
        else:
            produk_label_map = {
                hs4: f"{hs4} – {hs4_to_desc.get(hs4, 'N/A')[:45]}..."
                     if len(str(hs4_to_desc.get(hs4, ''))) > 45
                     else f"{hs4} – {hs4_to_desc.get(hs4, 'N/A')}"
                for hs4 in hs4_available
            }
            produk_display = list(produk_label_map.values())
            produk_selected_display = st.sidebar.selectbox("Pilih Produk (HS4):", produk_display)
            produk_selected = hs4_available[produk_display.index(produk_selected_display)]

    else:
        chapter_options = sorted(df3_ref["Chapter"].dropna().unique().tolist())
        selected_chapter = st.sidebar.selectbox("Pilih Chapter:", chapter_options)
        hs4_in_chapter = df3_ref[df3_ref["Chapter"] == selected_chapter]["HS4"].dropna().astype(int).tolist()

        df2_rek = df2[df2["Rekomendasi"].notna()].copy()
        df2_rek["Rekomendasi"] = pd.to_numeric(df2_rek["Rekomendasi"], errors="coerce").astype("Int64")
        hs4_available = sorted([int(x) for x in
                                df2_rek[df2_rek["Rekomendasi"].isin(hs4_in_chapter)]["Rekomendasi"].dropna().unique()])

        if len(hs4_available) == 0:
            st.sidebar.warning("Tidak ada produk dari chapter ini yang direkomendasikan.")
            produk_selected = None
        else:
            produk_label_map = {
                hs4: f"{hs4} – {hs4_to_desc.get(hs4, 'N/A')[:45]}..."
                     if len(str(hs4_to_desc.get(hs4, ''))) > 45
                     else f"{hs4} – {hs4_to_desc.get(hs4, 'N/A')}"
                for hs4 in hs4_available
            }
            produk_display = list(produk_label_map.values())
            produk_selected_display = st.sidebar.selectbox("Pilih Produk (HS4):", produk_display)
            produk_selected = hs4_available[produk_display.index(produk_selected_display)]

    # ============================================================
    # TAMPILAN UTAMA: ANALISIS PRODUK
    # ============================================================
    st.title("📦 Analisis Produk Rekomendasi")

    if produk_selected is None:
        st.info("Silakan pilih produk dari sidebar untuk melihat analisis.")
    else:
        produk_desc    = hs4_to_desc.get(produk_selected, "N/A")
        produk_chapter = hs4_to_chapter.get(produk_selected, "N/A")

        st.markdown(f"""
        <div class="card">
            <h3>🔍 Produk Terpilih</h3>
            <p style="font-size:18px; margin:4px 0;"><b>Kode HS4:</b> {produk_selected}</p>
            <p style="font-size:18px; margin:4px 0;"><b>Deskripsi:</b> {produk_desc}</p>
            <p style="font-size:16px; margin:4px 0; color:#555;"><b>Chapter:</b> {produk_chapter}</p>
        </div>
        """, unsafe_allow_html=True)

        df2_rek2 = df2.copy()
        df2_rek2["Rekomendasi"] = pd.to_numeric(df2_rek2["Rekomendasi"], errors="coerce").astype("Int64")
        prov_list = sorted([str(p).strip() for p in
                            df2_rek2[df2_rek2["Rekomendasi"] == produk_selected]["Provinsi"].dropna().unique()])

        if len(prov_list) == 0:
            st.warning("Tidak ada provinsi yang merekomendasikan produk ini.")
        else:
            st.markdown(f"""
            <div style="background:#e3f2fd; border-radius:12px; padding:12px 20px; margin-bottom:20px;">
                <span style="font-size:17px; color:#1565c0;">
                    <b>{len(prov_list)} Provinsi</b> merekomendasikan produk ini
                </span>
            </div>
            """, unsafe_allow_html=True)

            eci_min  = df1_prov["ECI"].min();  eci_max  = df1_prov["ECI"].max()
            icor_min = df1_prov["ICOR"].min(); icor_max = df1_prov["ICOR"].max()
            idsd_min = df1_prov["IDSD"].min(); idsd_max = df1_prov["IDSD"].max()

            def normalize(val, vmin, vmax):
                if pd.isna(val) or vmax == vmin: return 0
                return round((val - vmin) / (vmax - vmin), 3)

            rows = [prov_list[i:i+3] for i in range(0, len(prov_list), 3)]
            for row_provs in rows:
                cols = st.columns(3)
                for col_idx, prov in enumerate(row_provs):
                    with cols[col_idx]:
                        df1_match = df1_prov[
                            df1_prov["Nama Daerah"].astype(str).str.upper().str.strip()
                            == prov.upper().strip()
                        ]
                        if df1_match.empty:
                            st.markdown(f"""
                            <div class="prov-card">
                                <h4>📍 {prov}</h4>
                                <p style="color:#888; font-size:13px;">Data ECI/ICOR/IDSD tidak tersedia.</p>
                            </div>
                            """, unsafe_allow_html=True)
                            continue

                        row_data = df1_match.iloc[0]
                        eci_val  = row_data["ECI"]
                        icor_val = row_data["ICOR"]
                        idsd_val = row_data["IDSD"]
                        eci_norm  = normalize(eci_val, eci_min, eci_max)
                        icor_norm = 1 - normalize(icor_val, icor_min, icor_max)
                        idsd_norm = normalize(idsd_val, idsd_min, idsd_max)
                        eci_rank  = rank_ec_dict.get(row_data["Nama Daerah"], "-")
                        icor_rank = rank_ic_dict.get(row_data["Nama Daerah"], "-")

                        categories = ["ECI", "ICOR\n(inversi)", "IDSD"]
                        values     = [eci_norm, icor_norm, idsd_norm]

                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(
                            r=values + [values[0]],
                            theta=categories + [categories[0]],
                            fill='toself',
                            fillcolor='rgba(67,160,71,0.25)',
                            line=dict(color='#43a047', width=2),
                            name=prov,
                            hovertemplate="<b>%{theta}</b><br>Nilai Ternormalisasi: %{r:.2f}<extra></extra>"
                        ))
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(visible=True, range=[0,1],
                                                tickfont=dict(size=9), gridcolor="#ccc"),
                                angularaxis=dict(tickfont=dict(size=11))
                            ),
                            showlegend=False,
                            margin=dict(t=20, b=20, l=30, r=30),
                            height=260,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )

                        eci_disp  = f"{eci_val:.2f}"  if not pd.isna(eci_val)  else "N/A"
                        icor_disp = f"{icor_val:.2f}" if not pd.isna(icor_val) else "N/A"
                        idsd_disp = f"{idsd_val:.2f}" if not pd.isna(idsd_val) else "N/A"

                        st.markdown(f"""
                        <div class="prov-card">
                            <h4>📍 {prov}</h4>
                            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:6px;">
                                <span class="produk-badge">ECI: {eci_disp} (Rank #{eci_rank})</span>
                                <span class="produk-badge">ICOR: {icor_disp} (Rank #{icor_rank})</span>
                                <span class="produk-badge">IDSD: {idsd_disp}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.plotly_chart(fig_radar, use_container_width=True,
                                        key=f"radar_{prov}_{produk_selected}")

                for empty_col in range(len(row_provs), 3):
                    cols[empty_col].empty()


# ============================================================
# MODE: ANALISIS WILAYAH
# ============================================================
else:
    st.sidebar.header("Filter Wilayah")

    daerah_list   = sorted(df1["Nama Daerah"].dropna().unique().tolist())
    default_daerah = "NASIONAL" if "NASIONAL" in daerah_list else daerah_list[0]
    selected_daerah = st.sidebar.selectbox(
        "Pilih Nama Daerah",
        options=daerah_list,
        index=daerah_list.index(default_daerah)
    )

    if selected_daerah == "NASIONAL":
        df1_filtered = df1[df1["Nama Daerah"] == "NASIONAL"]
        df_rec = df2.copy()
    else:
        df1_filtered = df1[df1["Nama Daerah"] == selected_daerah]
        df_rec = df2[
            df2["Provinsi"].astype(str).str.upper().str.strip()
            == selected_daerah.upper().strip()
        ].copy()

    df_rec = df_rec[df_rec["Rekomendasi"].notna()].copy()
    df_rec["Rekomendasi"] = pd.to_numeric(df_rec["Rekomendasi"], errors="coerce").astype("Int64")

    if not df1_filtered.empty:
        row_metrik = df1_filtered.iloc[0]
        eci_val  = row_metrik["ECI"]
        icor_val = row_metrik["ICOR"]
        idsd_val = row_metrik["IDSD"]
        eci_rank  = rank_ec_dict.get(selected_daerah, None) if selected_daerah != "NASIONAL" else None
        icor_rank = rank_ic_dict.get(selected_daerah, None) if selected_daerah != "NASIONAL" else None
    else:
        eci_val = icor_val = idsd_val = np.nan
        eci_rank = icor_rank = None

    total_produk_rekomendasi = df_rec["Rekomendasi"].dropna().nunique()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Indikator Utama")

    def score_card(label, value, rank=None):
        rank_str = f" (Rank #{rank})" if rank is not None else ""
        st.sidebar.markdown(f"""
        <div class="sidebar-metric">
            <div class="label">{label}</div>
            <div class="value">{value}{rank_str}</div>
        </div>
        """, unsafe_allow_html=True)

    score_card("ECI",  f"{eci_val:.2f}"  if not pd.isna(eci_val)  else "N/A", rank=eci_rank)
    score_card("ICOR", f"{icor_val:.2f}" if not pd.isna(icor_val) else "N/A", rank=icor_rank)
    score_card("IDSD", f"{idsd_val:.2f}" if not pd.isna(idsd_val) else "N/A")
    score_card("Total Produk Rekomendasi", str(total_produk_rekomendasi))

    if selected_daerah == "NASIONAL":
        prov_terpilih = df2["Provinsi"].unique()
    else:
        prov_terpilih = [p for p in df2["Provinsi"].unique()
                         if p.strip().upper() == selected_daerah.strip().upper()]

    # ---------- LAYOUT UTAMA ----------
    st.title("Dashboard Multi Indikator Ekonomi")

    # ---------- Card 1: Tiga Barchart Sejajar ----------
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col_eci, col_icor, col_idsd = st.columns([1, 1, 1])

        with col_eci:
            st.subheader("ECI per Provinsi")
            sort_ecibar_option = st.selectbox(
                "Urutkan ECI berdasarkan:",
                ["Terbesar di atas", "Terkecil di atas", "Abjad"],
                key="sort_ecibar"
            )
            df_ecibar = df1_prov[['Nama Daerah', 'ECI']].dropna(subset=['ECI'])
            if sort_ecibar_option == "Terbesar di atas":
                df_ecibar = df_ecibar.sort_values('ECI', ascending=False)
            elif sort_ecibar_option == "Terkecil di atas":
                df_ecibar = df_ecibar.sort_values('ECI', ascending=True)
            else:
                df_ecibar = df_ecibar.sort_values('Nama Daerah', ascending=True)

            if selected_daerah == "NASIONAL":
                colors_eci    = ['skyblue'] * len(df_ecibar)
                opacities_eci = [1.0] * len(df_ecibar)
            else:
                target = selected_daerah.strip().upper()
                colors_eci, opacities_eci = [], []
                for prov in df_ecibar['Nama Daerah']:
                    if prov.strip().upper() == target:
                        colors_eci.append('skyblue'); opacities_eci.append(1.0)
                    else:
                        colors_eci.append('lightgray'); opacities_eci.append(0.4)

            fig_ecibar = go.Figure()
            fig_ecibar.add_trace(go.Bar(
                y=df_ecibar['Nama Daerah'], x=df_ecibar['ECI'],
                orientation='h',
                marker=dict(color=colors_eci, opacity=opacities_eci),
                text=df_ecibar['ECI'].apply(lambda x: f'{x:.2f}'),
                textposition='outside', hoverinfo='y+x'
            ))
            fig_ecibar.update_yaxes(autorange="reversed")
            fig_ecibar.update_layout(
                xaxis_title='ECI',
                yaxis=dict(title='Provinsi', tickfont=dict(size=9)),
                height=500, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='white'
            )
            st.plotly_chart(fig_ecibar, use_container_width=True)

        with col_icor:
            st.subheader("ICOR per Provinsi")
            sort_icorbar_option = st.selectbox(
                "Urutkan ICOR berdasarkan:",
                ["Terbesar di atas", "Terkecil di atas", "Abjad"],
                key="sort_icorbar"
            )
            df_icorbar = df1_prov[['Nama Daerah', 'ICOR']].dropna(subset=['ICOR'])
            if sort_icorbar_option == "Terbesar di atas":
                df_icorbar = df_icorbar.sort_values('ICOR', ascending=False)
            elif sort_icorbar_option == "Terkecil di atas":
                df_icorbar = df_icorbar.sort_values('ICOR', ascending=True)
            else:
                df_icorbar = df_icorbar.sort_values('Nama Daerah', ascending=True)

            if selected_daerah == "NASIONAL":
                colors_icor    = ['skyblue'] * len(df_icorbar)
                opacities_icor = [1.0] * len(df_icorbar)
            else:
                target = selected_daerah.strip().upper()
                colors_icor, opacities_icor = [], []
                for prov in df_icorbar['Nama Daerah']:
                    if prov.strip().upper() == target:
                        colors_icor.append('skyblue'); opacities_icor.append(1.0)
                    else:
                        colors_icor.append('lightgray'); opacities_icor.append(0.4)

            fig_icorbar = go.Figure()
            fig_icorbar.add_trace(go.Bar(
                y=df_icorbar['Nama Daerah'], x=df_icorbar['ICOR'],
                orientation='h',
                marker=dict(color=colors_icor, opacity=opacities_icor),
                text=df_icorbar['ICOR'].apply(lambda x: f'{x:.2f}'),
                textposition='outside', hoverinfo='y+x'
            ))
            fig_icorbar.update_yaxes(autorange="reversed")
            fig_icorbar.update_layout(
                xaxis_title='ICOR',
                yaxis=dict(title='Provinsi', tickfont=dict(size=9)),
                height=500, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='white'
            )
            st.plotly_chart(fig_icorbar, use_container_width=True)

        with col_idsd:
            st.subheader("Nilai IDSD per Pilar")
            pilar_y = [f"Pilar {i}" for i in range(1, 13)]
            pilar_inner = [
                "Institusi", "Infrastruktur", "Adopsi TIK", "Stabilitas Ekonomi",
                "Kesehatan", "Keterampilan", "Pasar Produk", "Pasar Tenaga Kerja",
                "Sistem Keuangan", "Ukuran Pasar", "Dinamika Bisnis", "Kapabilitas Inovasi"
            ]

            if not df1_filtered.empty:
                rata_pilar = df1_filtered[pilar_cols].mean().values if len(df1_filtered) > 1 \
                             else [df1_filtered.iloc[0][c] for c in pilar_cols]
                df_bar = pd.DataFrame({"Pilar": pilar_y, "Nilai": rata_pilar, "Nama": pilar_inner})
                sort_option = st.selectbox(
                    "Urutkan berdasarkan:",
                    ["Urutan Pilar", "Nilai Terbesar di atas", "Nilai Terkecil di atas"],
                    key="sort_pilar"
                )
                if sort_option == "Nilai Terbesar di atas":
                    df_bar = df_bar.sort_values("Nilai", ascending=False)
                elif sort_option == "Nilai Terkecil di atas":
                    df_bar = df_bar.sort_values("Nilai", ascending=True)

                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    y=df_bar["Pilar"], x=df_bar["Nilai"],
                    text=df_bar["Nama"],
                    textposition='inside', insidetextanchor='start',
                    name="Pilar", marker_color="skyblue", orientation='h'
                ))
                fig_bar.update_yaxes(autorange="reversed")
                fig_bar.update_layout(
                    xaxis_title="Nilai", yaxis_title="Pilar",
                    showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor='white', height=500
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("Pilih setidaknya satu daerah.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Card 2: Tabel Rekomendasi & Donut ----------
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if df_rec.empty:
            st.info("Tidak ada rekomendasi untuk wilayah terpilih.")
        else:
            df3_lookup = df3.copy()
            df3_lookup["HS4"] = pd.to_numeric(df3_lookup["HS4"], errors="coerce").astype("Int64")

            produk_series = pd.concat([df_rec["Produk 1"].astype(str), df_rec["Produk 2"].astype(str)])
            degree_df = produk_series.value_counts().reset_index()
            degree_df.columns = ["HS4", "Jumlah Koneksi"]
            degree_df["HS4"] = degree_df["HS4"].astype(str)

            tabel_rekomendasi_full = (
                df_rec[["Rekomendasi"]].drop_duplicates()
                .merge(df3_lookup[["HS4","Description","Chapter"]], left_on="Rekomendasi", right_on="HS4", how="left")
                [["Rekomendasi","Description","Chapter"]]
                .rename(columns={"Rekomendasi":"Produk Rekomendasi"})
            )
            tabel_rekomendasi_full["Produk Rekomendasi"] = tabel_rekomendasi_full["Produk Rekomendasi"].astype(str)
            tabel_rekomendasi_full = tabel_rekomendasi_full.merge(
                degree_df, left_on="Produk Rekomendasi", right_on="HS4", how="left"
            ).drop(columns=["HS4"])
            tabel_rekomendasi_full["Jumlah Koneksi"] = tabel_rekomendasi_full["Jumlah Koneksi"].fillna(0).astype(int)
            tabel_rekomendasi_full = (tabel_rekomendasi_full
                                      .sort_values("Produk Rekomendasi")
                                      .drop_duplicates(subset=["Produk Rekomendasi"]))

            chapter_list = sorted(tabel_rekomendasi_full["Chapter"].fillna("Unknown").unique())
            selected_chapter = st.selectbox("Filter Chapter", ["Semua Chapter"] + chapter_list, key="filter_chapter")

            tabel_rekomendasi = tabel_rekomendasi_full if selected_chapter == "Semua Chapter" else \
                                tabel_rekomendasi_full[tabel_rekomendasi_full["Chapter"].fillna("Unknown") == selected_chapter]

            row2_col1, row2_col2 = st.columns([1, 1])

            with row2_col1:
                st.subheader("Tabel Rekomendasi Produk")
                st.caption(f"Menampilkan {len(tabel_rekomendasi)} produk rekomendasi untuk: **{selected_daerah}**")
                st.dataframe(
                    tabel_rekomendasi[["Produk Rekomendasi","Description","Chapter","Jumlah Koneksi"]],
                    use_container_width=True, hide_index=True
                )

            with row2_col2:
                st.subheader("Distribusi Chapter Rekomendasi")
                if not tabel_rekomendasi.empty:
                    chapter_counts = tabel_rekomendasi["Chapter"].fillna("Unknown").value_counts()
                    if len(chapter_counts) > 8:
                        top = chapter_counts.head(8)
                        donut_data = pd.concat([top, pd.Series({"Others": chapter_counts.iloc[8:].sum()})])
                    else:
                        donut_data = chapter_counts

                    fig_donut = go.Figure()
                    fig_donut.add_trace(go.Pie(
                        labels=donut_data.index, values=donut_data.values,
                        hole=0.60, textinfo="percent",
                        hovertemplate="<b>%{label}</b><br>Jumlah Produk: %{value}<br>Persentase: %{percent}<extra></extra>",
                        pull=[0.05]*len(donut_data), sort=True
                    ))
                    fig_donut.update_layout(
                        annotations=[dict(text=f"{donut_data.sum()}<br>Produk", x=0.5, y=0.5,
                                          font_size=20, showarrow=False)],
                        legend=dict(orientation="h", y=-0.15),
                        height=500, margin=dict(t=40, b=80, l=40, r=40)
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)
                else:
                    st.info("Tidak ada data chapter.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Card 3: Network Diagram ----------
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Network Diagram Produk Rekomendasi")

        df_network = df2.copy() if selected_daerah == "NASIONAL" else \
                     df2[df2["Provinsi"].astype(str).str.upper().str.strip()
                         == selected_daerah.upper().strip()].copy()
        df_network = df_network[df_network["Rekomendasi"].notna()].copy()

        if df_network.empty:
            st.info("Tidak ada data untuk network diagram.")
        else:
            node_chapter = {}
            for _, row in df_network.iterrows():
                p1, ch1 = str(row["Produk 1"]), row.get("Chapter 1", None)
                if p1 not in node_chapter and pd.notna(ch1): node_chapter[p1] = str(ch1)
            for _, row in df_network.iterrows():
                p2, ch2 = str(row["Produk 2"]), row.get("Chapter 2", None)
                if p2 not in node_chapter and pd.notna(ch2): node_chapter[p2] = str(ch2)
            all_nodes = set(df_network["Produk 1"].unique()) | set(df_network["Produk 2"].unique())
            for node in all_nodes:
                if str(node) not in node_chapter: node_chapter[str(node)] = "Unknown"

            unique_chapters = sorted(set(node_chapter.values()))
            palette = px.colors.qualitative.Plotly + px.colors.qualitative.Set1 + px.colors.qualitative.Set2
            while len(palette) < len(unique_chapters): palette += palette
            chapter_color_map = dict(zip(unique_chapters, palette[:len(unique_chapters)]))

            net = Network(height="650px", width="100%", bgcolor="white", font_color="black")
            net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=250,
                           spring_strength=0.05, damping=0.09)

            for node in all_nodes:
                node_str = str(node)
                chapter  = node_chapter.get(node_str, "Unknown")
                warna    = chapter_color_map.get(chapter, "#cccccc")
                desc     = df3[df3["HS4"] == node]["Description"]
                label_desc = desc.values[0] if not desc.empty else node_str
                net.add_node(node_str, label=node_str, title=f"{label_desc} | Chapter: {chapter}",
                             color=warna, size=25, shape="dot",
                             font={"size": 24, "face": "arial", "strokeWidth": 2})

            def map_edge_color(rule_str):
                if pd.isna(rule_str): return None
                s = str(rule_str).strip().replace(" ","").replace(",",".")
                if s.startswith(">0.6"):                       return "red"
                elif s.startswith(">0.55") and "0.6" in s:    return "gold"
                elif s.startswith(">0.5")  and "0.55" in s:   return "green"
                else:                                          return "#cccccc"

            edge_count = 0
            for _, row in df_network.iterrows():
                ec = map_edge_color(row["Rule Strength"])
                if ec is None: continue
                net.add_edge(str(row["Produk 1"]), str(row["Produk 2"]),
                             title=f"Rule Strength: {str(row['Rule Strength']).strip()}", color=ec)
                edge_count += 1

            net.save_graph("network.html")
            with open("network.html", "r", encoding="utf-8") as f:
                html = f.read()
            st.components.v1.html(html, height=650, scrolling=True)
            st.caption(f"Jumlah node: {len(all_nodes)} | Jumlah edge: {edge_count}")

        st.markdown('</div>', unsafe_allow_html=True)