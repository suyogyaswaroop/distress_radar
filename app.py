import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from score_engine import score_multiple

# --- Page Config ---
st.set_page_config(
    page_title="Distress Radar",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Design Tokens ---
NAVY       = "#0d1117"
CARD_BG    = "#161b22"
BORDER     = "#21262d"
CYAN       = "#00d4ff"
GREEN      = "#00cc88"
AMBER      = "#f0a500"
RED        = "#ff4b4b"
TEXT_PRI   = "#e6edf3"
TEXT_SEC   = "#8b949e"
MONO       = "'JetBrains Mono', 'Courier New', monospace"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {NAVY};
    color: {TEXT_PRI};
}}

.stApp {{ background-color: {NAVY}; }}

/* Hide default streamlit elements */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 2rem 2.5rem 2rem 2.5rem; max-width: 1400px; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: {CARD_BG};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] .stTextArea textarea {{
    background-color: {NAVY};
    color: {TEXT_PRI};
    border: 1px solid {BORDER};
    font-family: {MONO};
    font-size: 12px;
}}

/* Metric cards */
.metric-card {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}}
.metric-value {{
    font-family: {MONO};
    font-size: 2rem;
    font-weight: 600;
    line-height: 1.1;
}}
.metric-label {{
    font-size: 0.72rem;
    color: {TEXT_SEC};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}}
.safe-val   {{ color: {GREEN}; }}
.grey-val   {{ color: {AMBER}; }}
.distress-val {{ color: {RED}; }}
.neutral-val  {{ color: {CYAN}; }}

/* Section headers */
.section-header {{
    font-size: 0.7rem;
    font-weight: 600;
    color: {TEXT_SEC};
    text-transform: uppercase;
    letter-spacing: 0.12em;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
    margin-top: 1.5rem;
}}

/* Zone pill badges */
.badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: {MONO};
    letter-spacing: 0.05em;
}}
.badge-safe     {{ background: rgba(0,204,136,0.15); color: {GREEN}; border: 1px solid rgba(0,204,136,0.3); }}
.badge-grey     {{ background: rgba(240,165,0,0.15);  color: {AMBER}; border: 1px solid rgba(240,165,0,0.3); }}
.badge-distress {{ background: rgba(255,75,75,0.15);  color: {RED};   border: 1px solid rgba(255,75,75,0.3); }}

/* Flag items */
.flag-item {{
    padding: 0.6rem 1rem;
    border-radius: 6px;
    margin-bottom: 0.4rem;
    font-size: 0.85rem;
    color: #e6edf3;
    font-weight: 500;
}}
.flag-red    {{ background: rgba(255,75,75,0.15);  border-left: 3px solid {RED};   color: #ffb3b3; }}
.flag-yellow {{ background: rgba(240,165,0,0.15);  border-left: 3px solid {AMBER}; color: #ffd580; }}
.flag-green  {{ background: rgba(0,204,136,0.15);  border-left: 3px solid {GREEN}; color: #80ffcc; }}

/* Divider */
.divider {{ border: none; border-top: 1px solid {BORDER}; margin: 1.5rem 0; }}

/* Outlier note */
.outlier-note {{
    font-size: 0.75rem;
    color: {TEXT_SEC};
    font-style: italic;
    margin-top: 0.3rem;
}}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-family:{MONO}; font-size:1.3rem; font-weight:700; color:{TEXT_PRI}; padding: 0.5rem 0 1rem 0; letter-spacing:0.05em;'>DISTRESS RADAR</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:0.7rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;'>NSE Tickers</div>", unsafe_allow_html=True)

    default_tickers = [
        "RELIANCE.NS", "TCS.NS", "HINDUNILVR.NS",
        "INFY.NS", "WIPRO.NS", "TATASTEEL.NS",
        "JPASSOCIAT.NS"
    ]

    ticker_input = st.text_area(
        label="tickers",
        value="\n".join(default_tickers),
        height=210,
        label_visibility="collapsed"
    )

    if "analysis_run" not in st.session_state:
        st.session_state.analysis_run = False

    run_button = st.button("▶  RUN ANALYSIS", type="primary", use_container_width=True)
    if run_button:
        st.session_state.analysis_run = True

    st.markdown("<hr style='border-color:#21262d; margin: 1.2rem 0;'>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-size:0.7rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.8rem;'>Zone Thresholds</div>
    <div style='font-family:{MONO}; font-size:0.82rem; line-height:2;'>
        <span style='color:{GREEN}'>●</span> <span style='color:{TEXT_PRI}'>SAFE</span>
        <span style='color:{TEXT_SEC}; float:right'>Z &gt; 2.99</span><br>
        <span style='color:{AMBER}'>●</span> <span style='color:{TEXT_PRI}'>GREY</span>
        <span style='color:{TEXT_SEC}; float:right'>1.81 – 2.99</span><br>
        <span style='color:{RED}'>●</span> <span style='color:{TEXT_PRI}'>DISTRESS</span>
        <span style='color:{TEXT_SEC}; float:right'>Z &lt; 1.81</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#21262d; margin: 1.2rem 0;'>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-size:0.7rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.6rem;'>Model</div>
    <div style='font-size:0.78rem; color:{TEXT_SEC}; line-height:1.6;'>
        Altman Z-Score (1968) — 5-ratio bankruptcy predictor.
        Adapted for Indian listed companies.<br><br>
        <span style='color:{AMBER}'>⚠</span> Exclude banks, NBFCs,
        and asset-light IT firms for reliable readings.
    </div>
    """, unsafe_allow_html=True)


# ── MAIN ──────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-bottom: 0.2rem;'>
    <span style='font-family:{MONO}; font-size:2.8rem; font-weight:700; color:{TEXT_PRI}; letter-spacing:0.04em;'>Distress Radar</span>
    <span style='font-family:{MONO}; font-size:2.8rem; color:#ffffff;'> ◈</span>
</div>
<div style='font-size:0.85rem; color:{TEXT_SEC}; margin-bottom:1.5rem;'>
    Financial distress early-warning system for Indian listed companies - Powered by Altman Z-Score
</div>
<hr style='border:none; border-top:1px solid {BORDER}; margin-bottom:1.5rem;'>
""", unsafe_allow_html=True)

# ── IDLE STATE ────────────────────────────────────────────
if not st.session_state.analysis_run:
    st.markdown(f"""
    <div style='background:{CARD_BG}; border:1px solid {BORDER}; border-radius:10px; padding:2.5rem; max-width:680px;'>
        <div style='font-family:{MONO}; font-size:0.7rem; color:{TEXT_PRI}; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:1rem;'>How it works</div>
        <div style='font-size:0.9rem; color:{TEXT_SEC}; line-height:1.9;'>
            <b style='color:{TEXT_PRI}'>01 &nbsp;</b> Enter NSE ticker symbols in the sidebar<br>
            <b style='color:{TEXT_PRI}'>02 &nbsp;</b> Model fetches live financials from Yahoo Finance<br>
            <b style='color:{TEXT_PRI}'>03 &nbsp;</b> Altman Z-Score computed for each company<br>
            <b style='color:{TEXT_PRI}'>04 &nbsp;</b> Companies classified into Safe / Grey / Distress zones<br>
            <b style='color:{TEXT_PRI}'>05 &nbsp;</b> Drill into any company for component-level breakdown
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── RUN ANALYSIS ──────────────────────────────────────────
tickers = [t.strip() for t in ticker_input.split("\n") if t.strip()]

with st.spinner("Loading data..."):
    try:
        df = score_multiple(tickers)
        if df.empty or df['Z_Score'].isna().all():
            raise ValueError("Live fetch failed")
        data_source = "live"
    except Exception:
        df = pd.read_csv("distress_report.csv")
        data_source = "cached"

if data_source == "cached":
    st.info("Showing pre-loaded data — live fetch is temporarily rate-limited by Yahoo Finance on this server. Run locally for live data.")

if df.empty:
    st.error("No data returned. Check ticker symbols and try again.")
    st.stop()

df_clean = df.dropna(subset=['Z_Score'])
df_clean = df_clean[~df_clean['Z_Score'].isin([float('inf'), float('-inf')])]

if df_clean.empty:
    st.error("Scoring failed for all tickers. Try different symbols.")
    st.stop()

total    = len(df_clean)
safe     = len(df_clean[df_clean['Zone'] == 'Safe'])
grey     = len(df_clean[df_clean['Zone'] == 'Grey'])
distress = len(df_clean[df_clean['Zone'] == 'Distress'])

# ── METRIC CARDS ─────────────────────────────────────────
st.markdown(f"<div class='section-header'>Portfolio Overview</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value neutral-val'>{total}</div>
        <div class='metric-label'>Companies Analysed</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value safe-val'>{safe}</div>
        <div class='metric-label'>Safe Zone</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value grey-val'>{grey}</div>
        <div class='metric-label'>Grey Zone</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value distress-val'>{distress}</div>
        <div class='metric-label'>Distress Zone</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── CHARTS ───────────────────────────────────────────────
st.markdown(f"<div class='section-header'>Z-Score Distribution</div>", unsafe_allow_html=True)

# Cap outliers for display
DISPLAY_CAP = 15
df_visual = df_clean.copy()
has_outliers = (df_visual['Z_Score'] > DISPLAY_CAP).any()
df_visual['Z_Display'] = df_visual['Z_Score'].clip(upper=DISPLAY_CAP)
df_visual = df_visual.sort_values('Z_Display', ascending=True)

color_map = {'Safe': GREEN, 'Grey': AMBER, 'Distress': RED}

left, right = st.columns([1.6, 1])

with left:
    fig = go.Figure()

    for zone, color in color_map.items():
        mask = df_visual['Zone'] == zone
        fig.add_trace(go.Bar(
            y=df_visual[mask]['Company'],
            x=df_visual[mask]['Z_Display'],
            name=zone,
            orientation='h',
            marker_color=color,
            marker_line_width=0,
            hovertemplate='<b>%{y}</b><br>Z-Score: %{customdata:.3f}<br>Zone: ' + zone + '<extra></extra>',
            customdata=df_clean[df_clean['Zone'] == zone]['Z_Score']
        ))

    fig.add_vline(x=2.99, line_dash="dot", line_color=GREEN,
                  line_width=1, annotation_text="2.99",
                  annotation_font_color=GREEN, annotation_font_size=10)
    fig.add_vline(x=1.81, line_dash="dot", line_color=AMBER,
                  line_width=1, annotation_text="1.81",
                  annotation_font_color=AMBER, annotation_font_size=10)

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_PRI, family='Inter'),
        barmode='overlay',
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=11, color='#ffffff'),
            bgcolor='rgba(0,0,0,0)'
        ),
        xaxis=dict(
            title=f"Z-Score{' (capped at 15)' if has_outliers else ''}",
            gridcolor=BORDER, gridwidth=1,
            title_font=dict(size=11, color=TEXT_SEC),
            tickfont=dict(family=MONO, size=10)
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0)',
            tickfont=dict(size=11)
        ),
        margin=dict(l=10, r=20, t=30, b=10),
        height=360,
        bargap=0.25
    )

    st.plotly_chart(fig, use_container_width=True)

    if has_outliers:
        st.markdown(f"<div class='outlier-note'>* Asset-light companies (e.g. IT sector) produce inflated Z-Scores due to high revenue/asset ratios. Bars capped at 15 for visual clarity; hover for actual score.</div>", unsafe_allow_html=True)

with right:
    zone_counts = df_clean['Zone'].value_counts().reset_index()
    zone_counts.columns = ['Zone', 'Count']

    fig2 = go.Figure(go.Pie(
        labels=zone_counts['Zone'],
        values=zone_counts['Count'],
        hole=0.55,
        marker=dict(
            colors=[color_map.get(z, CYAN) for z in zone_counts['Zone']],
            line=dict(color=NAVY, width=3)
        ),
        textfont=dict(family=MONO, size=11),
        hovertemplate='<b>%{label}</b><br>%{value} companies (%{percent})<extra></extra>'
    ))

    fig2.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>companies</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=TEXT_PRI, family=MONO)
    )

    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_PRI, family='Inter'),
        margin=dict(l=0, r=0, t=30, b=10),
        height=360
    )

    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── SCORECARD TABLE ───────────────────────────────────────
st.markdown(f"<div class='section-header'>Full Scorecard</div>", unsafe_allow_html=True)

display_cols = ['Company', 'Sector', 'Z_Score', 'Zone',
                'X1_Liquidity', 'X2_Profitability',
                'X3_Efficiency', 'X4_Leverage', 'X5_Asset_Use', 'Market_Cap_Cr']

df_display = df_clean[display_cols].copy()
df_display = df_display.rename(columns={
    'X1_Liquidity': 'X1 Liq',
    'X2_Profitability': 'X2 Prof',
    'X3_Efficiency': 'X3 Eff',
    'X4_Leverage': 'X4 Lev',
    'X5_Asset_Use': 'X5 Asset',
    'Market_Cap_Cr': 'Mkt Cap (₹Cr)'
})

def style_table(row):
    color = GREEN if row['Zone'] == 'Safe' else (AMBER if row['Zone'] == 'Grey' else RED)
    return [
        f'color: {color}; font-weight: 700;' if col == 'Zone'
        else f'color: #000000; font-weight: 600;'
        for col in row.index
    ]

st.dataframe(
    df_display.style
        .apply(style_table, axis=1)
        .format({'Z_Score': '{:.3f}', 'X1 Liq': '{:.3f}', 'X2 Prof': '{:.3f}',
                 'X3 Eff': '{:.3f}', 'X4 Lev': '{:.3f}', 'X5 Asset': '{:.3f}',
                 'Mkt Cap (₹Cr)': '{:,.0f}'}),
    use_container_width=True,
    hide_index=True,
    height=(len(df_display) * 35) + 38
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── DEEP DIVE ─────────────────────────────────────────────
st.markdown(f"<div class='section-header'>Company Deep Dive</div>", unsafe_allow_html=True)

selected = st.selectbox(
    "Select company",
    df_clean['Company'].tolist(),
    index=0,
    key=f"company_selector_{len(df_clean)}",
    label_visibility="collapsed"
)

selected_company = str(selected)
row = df_clean[df_clean['Company'] == selected_company].iloc[0]
zone_color = GREEN if row['Zone'] == 'Safe' else (AMBER if row['Zone'] == 'Grey' else RED)
badge_class = f"badge-{row['Zone'].lower()}"

st.markdown(f"""
<div style='display:flex; gap:1rem; align-items:center; margin-bottom:1.2rem; flex-wrap:wrap;'>
    <div style='font-family:{MONO}; font-size:1.1rem; font-weight:600; color:#ffffff;'>{selected_company}</div>
    <span class='badge {badge_class}'>{row['Zone'].upper()}</span>
    <span style='font-size:0.82rem; color:#ffffff;'>{row['Sector']}</span>
    <span style='font-family:{MONO}; font-size:1rem; font-weight:700; color:#ffffff; margin-left:auto;'>Z = <span style="color:{zone_color}">{row['Z_Score']:.3f}</span></span>
</div>
""", unsafe_allow_html=True)

# Component breakdown
components = pd.DataFrame({
    'Component': ['X1', 'X2', 'X3', 'X4', 'X5'],
    'Name': ['Liquidity', 'Profitability', 'Efficiency', 'Leverage', 'Asset Use'],
    'Weight': [1.2, 1.4, 3.3, 0.6, 1.0],
    'Raw Value': [row['X1_Liquidity'], row['X2_Profitability'],
                  row['X3_Efficiency'], row['X4_Leverage'], row['X5_Asset_Use']],
    'What it measures': [
        'Working capital relative to total assets — short-term liquidity buffer',
        'Retained earnings relative to assets — history of accumulated profit',
        'EBIT relative to assets — operating efficiency of the asset base',
        'Market cap relative to total liabilities — market vs debt cushion',
        'Revenue relative to assets — how hard assets are being worked'
    ]
})
components['Contribution'] = (components['Raw Value'] * components['Weight']).round(3)
components['Raw Value'] = components['Raw Value'].round(3)

st.dataframe(components, use_container_width=True, hide_index=True, height=215)

# Signal flags
st.markdown(f"<div style='font-size:0.7rem; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:0.1em; margin: 1rem 0 0.6rem 0;'>Signal Flags</div>", unsafe_allow_html=True)

flags = []
if row['X1_Liquidity'] < 0:
    flags.append(('red', 'Negative working capital — short-term liquidity risk'))
if row['X2_Profitability'] < 0:
    flags.append(('red', 'Negative retained earnings — sustained history of losses'))
if row['X3_Efficiency'] < 0.05:
    flags.append(('yellow', 'Low operating efficiency — assets not generating adequate returns'))
if row['X4_Leverage'] < 0.5:
    flags.append(('red', 'High leverage — market value well below total debt levels'))
if row['X5_Asset_Use'] < 0.3:
    flags.append(('yellow', 'Low asset utilisation — revenue thin relative to asset base'))

if flags:
    for level, msg in flags:
        css = 'flag-red' if level == 'red' else 'flag-yellow'
        icon = '🔴' if level == 'red' else '🟡'
        st.markdown(f"<div class='flag-item {css}'>{icon} {msg}</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='flag-item flag-green'>🟢 No major distress signals detected across all five components</div>", unsafe_allow_html=True)
