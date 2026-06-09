import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data.startups import STARTUPS
from models.financials import full_analysis

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Startup Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0f14;
    color: #e8eaf0;
}
h1, h2, h3 { font-family: 'Syne', sans-serif; }

.metric-card {
    background: linear-gradient(135deg, #1a1d26 0%, #12151e 100%);
    border: 1px solid #2a2d3a;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #f0f2f8;
    line-height: 1;
}
.metric-sub {
    font-size: 12px;
    color: #6b7280;
    margin-top: 4px;
}
.score-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    font-weight: 500;
}
.positive { color: #34d399; }
.negative { color: #f87171; }
.neutral  { color: #fbbf24; }
.sidebar-header {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Pre-compute all analyses ─────────────────────────────────────────────────
analyses = {s["name"]: full_analysis(s) for s in STARTUPS}
startup_map = {s["name"]: s for s in STARTUPS}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Dashboard Controls")
    st.markdown("---")

    st.markdown('<div class="sidebar-header">Select Startup</div>', unsafe_allow_html=True)
    selected_name = st.radio(
        "",
        [s["name"] for s in STARTUPS],
        format_func=lambda n: f"{n}  •  {startup_map[n]['sector']}"
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-header">Compare View</div>', unsafe_allow_html=True)
    show_compare = st.toggle("Show All Startups", value=False)

    st.markdown("---")
    st.markdown('<div class="sidebar-header">Chart Type</div>', unsafe_allow_html=True)
    chart_type = st.selectbox("Revenue Chart", ["Area", "Bar", "Line"])

    st.markdown("---")
    st.caption("Built by Armita Patro · Financial Model & Market Feasibility Dashboard")

# ── Main ─────────────────────────────────────────────────────────────────────
selected = startup_map[selected_name]
a = analyses[selected_name]

# Header
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown(f"# {selected['name']}")
    st.markdown(f"**{selected['description']}** &nbsp;·&nbsp; `{selected['sector']}` &nbsp;·&nbsp; `{selected['stage']}`")
with col_badge:
    score = a["score"]
    score_color = "#34d399" if score >= 70 else "#fbbf24" if score >= 45 else "#f87171"
    st.markdown(f"""
    <div style='text-align:right; padding-top:16px;'>
        <div style='font-family:DM Mono,monospace;font-size:11px;color:#6b7280;letter-spacing:2px;'>INVEST SCORE</div>
        <div style='font-family:Syne,sans-serif;font-size:48px;font-weight:800;color:{score_color};line-height:1'>{score}</div>
        <div style='font-size:12px;color:#6b7280;'>/ 100</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── KPI Row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, sub="", positive=None):
    color = ""
    if positive is True: color = "positive"
    elif positive is False: color = "negative"
    else: color = "neutral"
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

npv_val = a["npv"]
kpi(k1, "NPV", f"₹{npv_val/100000:.1f}L" if abs(npv_val) < 10_000_000 else f"₹{npv_val/10000000:.2f}Cr",
    "Net Present Value", positive=npv_val > 0)

kpi(k2, "ROI", f"{a['roi']}%", "12-month return", positive=a['roi'] > 0)

be = a["breakeven_month"]
kpi(k3, "Break-even", f"Month {be}" if be else "Not yet", "Cumulative P&L", positive=be is not None and be <= 12)

kpi(k4, "Runway", f"{a['runway_months']} mo", "Before cash-out", positive=a['runway_months'] >= 12)

kpi(k5, "CAGR", f"{a['cagr']}%", "Revenue growth rate", positive=a['cagr'] > 15)

st.markdown("")

# ── Charts ───────────────────────────────────────────────────────────────────
chart_col, insight_col = st.columns([3, 1])

with chart_col:
    df = a["df"]
    plot_colors = {"Revenue": selected["color"], "Costs": "#f87171", "Net Profit": "#fbbf24"}

    fig = go.Figure()
    for col_name, color in plot_colors.items():
        if chart_type == "Area":
            fig.add_trace(go.Scatter(
                x=df["Month"], y=df[col_name], name=col_name,
                fill="tozeroy", line=dict(color=color, width=2),
                fillcolor=color.replace("#", "rgba(").rstrip(")") if False else color + "33"
            ))
        elif chart_type == "Bar":
            fig.add_trace(go.Bar(x=df["Month"], y=df[col_name], name=col_name, marker_color=color, opacity=0.85))
        else:
            fig.add_trace(go.Scatter(x=df["Month"], y=df[col_name], name=col_name, line=dict(color=color, width=2.5)))

    fig.update_layout(
        title=f"Revenue vs Costs — {selected['name']}",
        plot_bgcolor="#0d0f14", paper_bgcolor="#0d0f14",
        font=dict(family="DM Sans", color="#9ca3af"),
        legend=dict(bgcolor="#1a1d26", bordercolor="#2a2d3a"),
        xaxis=dict(gridcolor="#1e2130", zeroline=False),
        yaxis=dict(gridcolor="#1e2130", zeroline=False, tickprefix="₹"),
        height=360,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative P&L
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["Month"], y=df["Cumulative P&L"],
        fill="tozeroy",
        line=dict(color=selected["color"], width=2),
        name="Cumulative P&L"
    ))
    fig2.add_hline(y=0, line_dash="dot", line_color="#4b5563")
    fig2.update_layout(
        title="Cumulative P&L Trajectory",
        plot_bgcolor="#0d0f14", paper_bgcolor="#0d0f14",
        font=dict(family="DM Sans", color="#9ca3af"),
        xaxis=dict(gridcolor="#1e2130", zeroline=False),
        yaxis=dict(gridcolor="#1e2130", zeroline=False, tickprefix="₹"),
        height=280,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with insight_col:
    st.markdown("#### 📌 Key Insights")

    tam = a["tam_penetration"]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">TAM Opportunity</div>
        <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;color:#f0f2f8'>
            ₹{selected['financials']['market_size']/10000000:.0f}Cr
        </div>
        <div class="metric-sub">Total Addressable Market</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Revenue at Target Share</div>
        <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;color:{selected["color"]}'>
            ₹{tam/100000:.1f}L
        </div>
        <div class="metric-sub">{selected['financials']['target_market_share']*100:.1f}% penetration</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Burn Rate (avg)</div>
        <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;color:#f87171'>
            ₹{abs(a['burn_rate'])/1000:.0f}K/mo
        </div>
        <div class="metric-sub">During loss-making months</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Team Size</div>
        <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;color:#fbbf24'>
            {selected['team_size']} people
        </div>
        <div class="metric-sub">{selected['stage']} stage</div>
    </div>
    """, unsafe_allow_html=True)

# ── Monthly Data Table ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📋 Month-by-Month Breakdown")
display_df = a["df"].copy()
for col in ["Revenue", "Costs", "Net Profit", "Cumulative P&L"]:
    display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.0f}")
st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Compare All ──────────────────────────────────────────────────────────────
if show_compare:
    st.markdown("---")
    st.markdown("## 🔍 Startup Comparison")

    compare_data = []
    for s in STARTUPS:
        an = analyses[s["name"]]
        compare_data.append({
            "Startup": s["name"],
            "Sector": s["sector"],
            "Stage": s["stage"],
            "Invest Score": an["score"],
            "NPV (₹L)": round(an["npv"] / 100000, 1),
            "ROI (%)": an["roi"],
            "Break-even": f"M{an['breakeven_month']}" if an["breakeven_month"] else "—",
            "Runway (mo)": an["runway_months"],
            "CAGR (%)": an["cagr"],
        })

    cdf = pd.DataFrame(compare_data)
    st.dataframe(cdf, use_container_width=True, hide_index=True)

    # Radar / score bar
    fig3 = go.Figure()
    for s in STARTUPS:
        an = analyses[s["name"]]
        fig3.add_trace(go.Bar(
            name=s["name"],
            x=["Invest Score", "ROI", "CAGR", "Runway"],
            y=[an["score"], min(an["roi"], 100), min(an["cagr"], 100), min(an["runway_months"] * 8, 100)],
            marker_color=s["color"]
        ))

    fig3.update_layout(
        barmode="group",
        title="Comparative Performance (Normalised)",
        plot_bgcolor="#0d0f14", paper_bgcolor="#0d0f14",
        font=dict(family="DM Sans", color="#9ca3af"),
        xaxis=dict(gridcolor="#1e2130"),
        yaxis=dict(gridcolor="#1e2130", range=[0, 110]),
        height=380,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)
