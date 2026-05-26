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

# ─── DARK MODE CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* === DARK BASE === */
    .stApp                        { background-color: #0F1117; zoom: 0.8; }
    [data-testid="stSidebar"]     { background-color: #1A1D27; border-right: 1px solid #2D3148; }
    [data-testid="stSidebar"] *   { color: #CBD5E0 !important; }

    /* Text */
    h1, h2, h3, p, span, label, div { color: #E2E8F0; }
    .stMarkdown p                 { color: #CBD5E0; }

    /* Metric cards */
    .metric-card {
        background: #1A1D27;
        border: 1px solid #2D3148;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    }
    .metric-card h2 { color: #63B3ED !important; margin: 0; font-size: 1.8rem; }
    .metric-card p  { color: #718096 !important; margin: 4px 0 0; font-size: 0.9rem; }

    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #90CDF4 !important;
        padding: 6px 0 4px;
        border-bottom: 2px solid #3182CE;
        margin-bottom: 16px;
    }

    /* Legend pills */
    .legend-pill {
        display: inline-block;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 8px;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] { background: #1A1D27; border-radius: 10px; }
    .dvn-scroller               { background: #1A1D27 !important; }

    /* Selectbox & widgets */
    [data-baseweb="select"] > div          { background-color: #1A1D27 !important; border-color: #2D3148 !important; color: #E2E8F0 !important; }
    [data-baseweb="select"] span           { color: #E2E8F0 !important; }
    [data-testid="stSelectbox"] label      { color: #CBD5E0 !important; }

    /* Horizontal rule */
    hr { border-color: #2D3148; }
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
    st.error("❌ File **Data.xlsx** tidak ditemukan. Pastikan file sudah di-push ke repository GitHub.")
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
        <span class="legend-pill" style="background:#3D0000;color:#FC8181;">● Merah &gt; 0.6</span><br><br>
        <span class="legend-pill" style="background:#3D2E00;color:#F6E05E;">● Kuning &gt; 0.55–0.6</span><br><br>
        <span class="legend-pill" style="background:#003D1A;color:#68D391;">● Hijau &gt; 0.5–0.55</span>
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
    (c4, n_high_edge,       "🔴 Koneksi Kuat (>0.6)"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{val}</h2>
            <p>{label}</p>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── ECI BAR CHART ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Economic Complexity Index (ECI) per Provinsi</div>',
            unsafe_allow_html=True)

eci_df = df.drop_duplicates("Provinsi")[["Provinsi", "ECI"]].sort_values("ECI", ascending=True)
colors = ["#63B3ED" if p == selected_prov else "#2C4A6E" for p in eci_df["Provinsi"]]

fig_eci = go.Figure(go.Bar(
    x=eci_df["ECI"],
    y=eci_df["Provinsi"],
    orientation="h",
    marker_color=colors,
    text=[f"{v:,.0f}" for v in eci_df["ECI"]],
    textposition="outside",
    textfont=dict(color="#CBD5E0"),
    hovertemplate="<b>%{y}</b><br>ECI: %{x:,.2f}<extra></extra>",
))
fig_eci.update_layout(
    height=280,
    margin=dict(l=0, r=80, t=10, b=10),
    xaxis=dict(title="ECI Value", showgrid=True, gridcolor="#2D3148",
               zeroline=False, color="#CBD5E0", tickfont=dict(color="#CBD5E0")),
    yaxis=dict(title="", color="#CBD5E0", tickfont=dict(color="#CBD5E0")),
    plot_bgcolor="#1A1D27",
    paper_bgcolor="#1A1D27",
    font=dict(family="Inter, sans-serif", size=12, color="#CBD5E0"),
)
st.plotly_chart(fig_eci, use_container_width=True)

# ─── NETWORK + TABLE ─────────────────────────────────────────────────────────────
col_net, col_tbl = st.columns([3, 2], gap="large")

# ── NETWORK ──────────────────────────────────────────────────────────────────────
with col_net:
    st.markdown('<div class="section-header">🕸️ Jaringan Hubungan Produk</div>',
                unsafe_allow_html=True)

    EDGE_COLOR = {
        "> 0.6":        "#FC8181",   # red
        "> 0.55 - 0.6": "#F6E05E",  # yellow
        "> 0.5 - 0.55": "#68D391",  # green
    }

    net = Network(height="480px", width="100%", bgcolor="#1A1D27", font_color="#E2E8F0")
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=120, spring_strength=0.04)

    nodes_added = set()
    for _, row in df_prov.iterrows():
        p1, p2 = str(row["Product 1"]), str(row["Product 2"])
        for p in [p1, p2]:
            if p not in nodes_added:
                net.add_node(
                    p, label=p,
                    color="#63B3ED", size=18,
                    font={"size": 13, "color": "#E2E8F0", "face": "Inter"},
                    borderWidth=2, borderWidthSelected=4,
                    shadow=True,
                )
                nodes_added.add(p)
        edge_col = EDGE_COLOR.get(str(row["Rule Strength"]), "#4A5568")
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

    # Dark background injection
    html_content = html_content.replace(
        "<body>",
        '<body style="background:#1A1D27;margin:0;padding:0;">'
    )
    st.components.v1.html(html_content, height=490, scrolling=False)

# ── TABLE ─────────────────────────────────────────────────────────────────────────
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
        st.info("Tidak ada rekomendasi produk untuk provinsi ini.")
    else:
        st.dataframe(
            tbl_df,
            use_container_width=True,
            hide_index=True,
            height=460,
            column_config={
                "Section HS": st.column_config.TextColumn("Section HS2",          width="medium"),
                "Produk":     st.column_config.TextColumn("Produk Rekomendasi",   width="small"),
            },
        )

# ─── FOOTER ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#4A5568;font-size:0.8rem;'>"
    "Dashboard Analisis Ekspor Provinsi · Data: SITC/HS Product Space</p>",
    unsafe_allow_html=True,
)
