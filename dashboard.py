import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pyvis.network import Network
import tempfile
import os

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Ekspor Provinsi",
    page_icon="📊",
    layout="wide",
)

# ─── BRIGHT MODE CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* === BASE LIGHT THEME === */
    .stApp {
        background-color: #F8FAFC;
        zoom: 0.9;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] * {
        color: #1E293B !important;
    }

    /* Global text */
    h1, h2, h3, p, span, label, div {
        color: #0F172A;
    }
    .stMarkdown p {
        color: #334155;
    }

    /* Metric cards - light glassmorphism */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.05);
        border-color: #CBD5E1;
    }
    .metric-card h2 {
        color: #2563EB !important;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-card p {
        color: #475569 !important;
        margin: 8px 0 0;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }

    /* Section headers */
    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1E40AF !important;
        padding: 6px 0 6px 0;
        border-bottom: 3px solid #3B82F6;
        margin-bottom: 20px;
        display: inline-block;
    }

    /* Legend pills (sidebar) */
    .legend-pill {
        display: inline-block;
        border-radius: 40px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
        background-color: #F1F5F9;
        color: #0F172A !important;
    }

    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        overflow: hidden;
    }
    .dvn-scroller {
        background: #FFFFFF !important;
    }
    th {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    td {
        color: #1E293B !important;
    }

    /* Selectbox & widgets - clean light */
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #CBD5E1 !important;
        border-radius: 12px !important;
        color: #0F172A !important;
    }
    [data-baseweb="select"] span {
        color: #0F172A !important;
    }
    [data-testid="stSelectbox"] label {
        color: #334155 !important;
        font-weight: 500 !important;
    }

    /* Buttons and interactive */
    .stButton button {
        background-color: #3B82F6;
        color: white;
        border-radius: 40px;
        border: none;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: #2563EB;
    }

    /* Horizontal rule */
    hr {
        border-color: #E2E8F0;
        margin: 1rem 0;
    }

    /* Info box */
    .stAlert {
        background-color: #EFF6FF;
        border-left-color: #3B82F6;
    }
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADING ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "Data.xlsx")
    if not os.path.exists(data_path):
        data_path = "Data.xlsx"
    df = pd.read_excel(data_path)
    df["Product 1"]          = df["Product 1"].astype(str).str.zfill(4)
    df["Product 2"]          = df["Product 2"].astype(str).str.zfill(4)
    df["Produk Rekomendasi"] = df["Produk Rekomendasi"].astype(str).str.zfill(4)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ File **Data.xlsx** tidak ditemukan. Pastikan file sudah ada di direktori yang sama.")
    st.stop()
except Exception as e:
    st.error(f"❌ Gagal memuat data: {e}")
    st.stop()

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗂️ Filter Data")
    st.markdown("---")
    provinsi_list = sorted(df["Provinsi"].unique().tolist())
    selected_prov = st.selectbox("🏙️ Pilih Provinsi", provinsi_list)
    st.markdown("---")
    st.markdown("### 🔗 Keterangan Warna Edge")
    st.markdown("""
    <div>
        <span class="legend-pill" style="background:#FEE2E2; color:#B91C1C;"> ● Kuat (> 0.6)</span>
        <span class="legend-pill" style="background:#FEF9C3; color:#854D0E;"> ● Sedang (0.55–0.6)</span>
        <span class="legend-pill" style="background:#DCFCE7; color:#166534;"> ● Lemah (0.5–0.55)</span>
    </div>
    """, unsafe_allow_html=True)

# ─── FILTER DATA ────────────────────────────────────────────────────────────────
df_prov = df[df["Provinsi"] == selected_prov].copy()

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"# 📊 Dashboard Ekspor — {selected_prov}")
st.markdown("Visualisasi Economic Complexity Index (ECI), jaringan produk, dan rekomendasi ekspor.")
st.markdown("---")

# ─── METRIC CARDS ───────────────────────────────────────────────────────────────
eci_val      = df_prov["ECI"].iloc[0] if not df_prov.empty else 0
n_products   = df_prov[["Product 1", "Product 2"]].stack().nunique()
n_rekomen    = df_prov[df_prov["Produk Rekomendasi"] != "0000"]["Produk Rekomendasi"].nunique()
n_high_edge  = (df_prov["Rule Strength"] == "> 0.6").sum()

c1, c2, c3, c4 = st.columns(4)
for col, val, label in [
    (c1, f"{eci_val:,.2f}", "💰 ECI Provinsi"),
    (c2, n_products,        "📦 Jumlah Produk"),
    (c3, n_rekomen,         "✅ Produk Rekomendasi"),
    (c4, n_high_edge,       "🔗 Koneksi Kuat (>0.6)"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{val}</h2>
            <p>{label}</p>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── ECI BAR CHART (BRIGHT THEME) ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Economic Complexity Index (ECI) per Provinsi</div>',
            unsafe_allow_html=True)

eci_df = df.drop_duplicates("Provinsi")[["Provinsi", "ECI"]].sort_values("ECI", ascending=True)
colors = ["#3B82F6" if p == selected_prov else "#CBD5E1" for p in eci_df["Provinsi"]]

fig_eci = go.Figure(go.Bar(
    x=eci_df["ECI"],
    y=eci_df["Provinsi"],
    orientation="h",
    marker_color=colors,
    text=[f"{v:,.0f}" for v in eci_df["ECI"]],
    textposition="outside",
    textfont=dict(color="#0F172A", size=11),
    hovertemplate="<b>%{y}</b><br>ECI: %{x:,.2f}<extra></extra>",
))
fig_eci.update_layout(
    height=280,
    margin=dict(l=0, r=80, t=10, b=10),
    xaxis=dict(title="Nilai ECI", showgrid=True, gridcolor="#E2E8F0",
               zeroline=False, color="#334155", tickfont=dict(color="#334155")),
    yaxis=dict(title="", color="#334155", tickfont=dict(color="#334155")),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Inter, sans-serif", size=12, color="#0F172A"),
    hoverlabel=dict(bgcolor="#FFFFFF", font_size=12, font_family="Inter")
)
st.plotly_chart(fig_eci, use_container_width=True)

# ─── NETWORK + TABLE ─────────────────────────────────────────────────────────────
col_net, col_tbl = st.columns([3, 2], gap="large")

# ── NETWORK (LIGHT BACKGROUND) ──────────────────────────────────────────────────
with col_net:
    st.markdown('<div class="section-header">🕸️ Jaringan Hubungan Produk</div>',
                unsafe_allow_html=True)

    EDGE_COLOR = {
        "> 0.6":        "#EF4444",   # red
        "> 0.55 - 0.6": "#F59E0B",   # amber
        "> 0.5 - 0.55": "#10B981",   # emerald
    }

    # Light theme for pyvis
    net = Network(height="480px", width="100%", bgcolor="#FFFFFF", font_color="#1E293B")
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=120, spring_strength=0.04)

    nodes_added = set()
    for _, row in df_prov.iterrows():
        p1, p2 = str(row["Product 1"]), str(row["Product 2"])
        for p in [p1, p2]:
            if p not in nodes_added:
                net.add_node(
                    p, label=p,
                    color="#3B82F6", size=18,
                    font={"size": 13, "color": "#0F172A", "face": "Inter"},
                    borderWidth=2, borderWidthSelected=4,
                    shadow=True,
                )
                nodes_added.add(p)
        edge_col = EDGE_COLOR.get(str(row["Rule Strength"]), "#94A3B8")
        net.add_edge(
            p1, p2,
            color={"color": edge_col, "highlight": edge_col, "opacity": 0.9},
            width=3,
            title=f"Rule Strength: {row['Rule Strength']}",
            smooth={"type": "curvedCW", "roundness": 0.1},
        )

    net.set_options("""
    var options = {
      "nodes": { "shape": "dot" },
      "edges": { "smooth": { "enabled": true } },
      "physics": { "enabled": true,
        "barnesHut": { "gravitationalConstant": -8000, "springLength": 120 }
      },
      "interaction": { "hover": true, "tooltipDelay": 100 }
    }
    """)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", dir=tempfile.gettempdir())
    tmp_path = tmp.name
    tmp.close()
    net.save_graph(tmp_path)
    with open(tmp_path, encoding="utf-8") as f:
        html_content = f.read()
    try:
        os.unlink(tmp_path)
    except Exception:
        pass

    # Force light background
    html_content = html_content.replace(
        "<body>",
        '<body style="background:#FFFFFF;margin:0;padding:0;">'
    )
    st.components.v1.html(html_content, height=490, scrolling=False)

# ── TABLE (RECOMMENDATIONS) ─────────────────────────────────────────────────────
with col_tbl:
    st.markdown('<div class="section-header">📋 Rekomendasi Produk Ekspor</div>',
                unsafe_allow_html=True)

    tbl_df = df_prov[
        df_prov["Produk Rekomendasi"].notna() &
        (~df_prov["Produk Rekomendasi"].str.startswith("-")) &
        (df_prov["Produk Rekomendasi"] != "0000") &
        (df_prov["Section"].notna())
    ][["Section", "Produk Rekomendasi"]].drop_duplicates().reset_index(drop=True)

    def shorten_section(s):
        if pd.isna(s): return "-"
        parts = str(s).split(" - ", 1)
        return parts[1].strip() if len(parts) > 1 else str(s)

    tbl_df["Section HS"] = tbl_df["Section"].apply(shorten_section)
    tbl_df = tbl_df[["Section HS", "Produk Rekomendasi"]].rename(
        columns={"Produk Rekomendasi": "Produk"}
    )

    if tbl_df.empty:
        st.info("✨ Tidak ada rekomendasi produk untuk provinsi ini.")
    else:
        st.dataframe(
            tbl_df,
            use_container_width=True,
            hide_index=True,
            height=460,
            column_config={
                "Section HS": st.column_config.TextColumn("Sektor HS", width="medium"),
                "Produk":     st.column_config.TextColumn("Kode Produk", width="small"),
            },
        )

# ─── FOOTER ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#64748B;font-size:0.8rem;'>"
    "Dashboard Analisis Ekspor Provinsi · Data: SITC/HS Product Space</p>",
    unsafe_allow_html=True,
)
