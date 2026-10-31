"""Helper functions shared by all pages (simple, beginner friendly)."""
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------- Paths ----------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "student_performance.csv")
ASSETS = os.path.join(ROOT, "assets")

SUBJECTS = ["Python", "SQL", "Power BI", "AI"]

# ---------- Black + Dark Green theme ----------
BLACK = "#000000"
PANEL = "#0b1a10"
GREEN = "#00e676"        # bright accent
MID_GREEN = "#1b8f4e"
DARK_GREEN = "#0d5c2e"
TEXT = "#d9f7e3"
GOLD = "#ffd54f"         # only for highlighting the topper
RED = "#ff5252"
GREENS = ["#003d1a", "#0d5c2e", "#1b8f4e", "#00c853", "#00e676", "#69f0ae", "#b9f6ca"]


def style_fig(fig, title=None, height=420):
    """Apply the dark-green look to any plotly chart."""
    fig.update_layout(
        title=title, height=height,
        paper_bgcolor=BLACK, plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        colorway=GREENS[::-1],
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_xaxes(gridcolor="#12301d", zerolinecolor="#12301d")
    fig.update_yaxes(gridcolor="#12301d", zerolinecolor="#12301d")
    return fig


def apply_css():
    """Small CSS for cards and headings."""
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {BLACK}; }}
        h1, h2, h3 {{ color: {GREEN}; }}
        .card {{ background:{PANEL}; border:1px solid {DARK_GREEN}; border-left:5px solid {GREEN};
                 border-radius:10px; padding:14px 16px; margin-bottom:10px; }}
        .card .label {{ color:#8fd9ab; font-size:13px; }}
        .card .value {{ color:{GREEN}; font-size:28px; font-weight:700; }}
        .card .sub {{ color:#8fd9ab; font-size:12px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def card(label, value, sub=""):
    """Show one KPI card."""
    st.markdown(
        f'<div class="card"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


# ---------- Data loading and cleaning ----------
@st.cache_data
def load_raw():
    """Read the CSV exactly as it is."""
    return pd.read_csv(DATA_PATH)


def grade_from_avg(avg):
    if avg >= 90: return "A+"
    if avg >= 80: return "A"
    if avg >= 70: return "B"
    if avg >= 60: return "C"
    return "D"


def clean_data(raw):
    """Clean the data and add calculated columns.

    Rules used:
    1. Remove duplicate rows.
    2. A mark of 0 or a Null is treated as 'missing' (a real student does not score 0
       in every test, so 0 is most likely absent / data-entry error).
    3. Missing values are filled with the MEDIAN of that column (median is not
       affected by outliers).
    """
    df = raw.drop_duplicates().copy()
    num_cols = SUBJECTS + ["Attendance"]
    df[num_cols] = df[num_cols].replace(0, np.nan)
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())

    df["Total Marks"] = df[SUBJECTS].sum(axis=1)
    df["Average"] = df[SUBJECTS].mean(axis=1).round(2)
    df["Grade"] = df["Average"].apply(grade_from_avg)
    df["Rank"] = df["Average"].rank(ascending=False, method="min").astype(int)
    return df.sort_values("Rank").reset_index(drop=True)


@st.cache_data
def load_clean():
    return clean_data(load_raw())


def outliers_iqr(df, col):
    """Return rows that are outside 1.5 x IQR for a column."""
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    return df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]


# ---------- Student charts (used by app.py and the HTML export) ----------
def student_bar(df, name):
    row = df[df["Student"] == name].iloc[0]
    class_avg = df[SUBJECTS].mean()
    fig = go.Figure()
    fig.add_bar(x=SUBJECTS, y=[row[s] for s in SUBJECTS], name=name, marker_color=GREEN,
                text=[row[s] for s in SUBJECTS], textposition="outside")
    fig.add_bar(x=SUBJECTS, y=class_avg.round(1), name="Class Average", marker_color=DARK_GREEN)
    fig.update_layout(barmode="group", xaxis_title="Subject", yaxis_title="Marks", yaxis_range=[0, 110])
    return style_fig(fig, f"{name}: Marks vs Class Average", 380)


def student_radar(df, name):
    row = df[df["Student"] == name].iloc[0]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[row[s] for s in SUBJECTS] + [row[SUBJECTS[0]]],
                                  theta=SUBJECTS + [SUBJECTS[0]], fill="toself",
                                  name=name, line_color=GREEN))
    fig.add_trace(go.Scatterpolar(r=list(df[SUBJECTS].mean()) + [df[SUBJECTS[0]].mean()],
                                  theta=SUBJECTS + [SUBJECTS[0]], name="Class Average",
                                  line_color=MID_GREEN, line_dash="dash"))
    fig.update_layout(polar=dict(bgcolor=PANEL, radialaxis=dict(range=[50, 100], gridcolor="#12301d"),
                                 angularaxis=dict(gridcolor="#12301d")))
    return style_fig(fig, f"{name}: Skill Radar", 380)


def attendance_vs_avg(df, name):
    """Scatter of attendance vs average; selected student = big white ring, topper = gold star."""
    topper = df.iloc[0]["Student"]
    fig = px.scatter(df, x="Attendance", y="Average", hover_name="Student",
                     hover_data=["Rank", "Grade"], size_max=14)
    fig.update_traces(marker=dict(size=10, color=MID_GREEN))
    t = df[df["Student"] == topper]
    fig.add_trace(go.Scatter(x=t["Attendance"], y=t["Average"], mode="markers", name=f"Topper: {topper}",
                             marker=dict(size=20, color=GOLD, symbol="star")))
    s = df[df["Student"] == name]
    fig.add_trace(go.Scatter(x=s["Attendance"], y=s["Average"], mode="markers", name=f"Selected: {name}",
                             marker=dict(size=18, color=GREEN, line=dict(color="white", width=2))))
    fig.update_layout(xaxis_title="Attendance (%)", yaxis_title="Average Marks")
    return style_fig(fig, "Attendance vs Average Marks", 380)


def ranking_bar(df):
    """Ranking bar chart, topper in gold, lowest in red."""
    d = df.sort_values("Average")
    colors = [GREEN] * len(d)
    colors[-1] = GOLD
    colors[0] = RED
    fig = go.Figure(go.Bar(x=d["Average"], y=d["Student"], orientation="h", marker_color=colors,
                           text=d["Average"], textposition="outside"))
    fig.update_layout(xaxis_title="Average Marks", yaxis_title="Student", xaxis_range=[0, 105])
    return style_fig(fig, "Student Ranking (gold = topper, red = lowest)", 700)


def build_html_report(df, name):
    """Make one standalone HTML file with the dashboard for the selected student."""
    figs = [student_bar(df, name), student_radar(df, name), attendance_vs_avg(df, name), ranking_bar(df)]
    row = df[df["Student"] == name].iloc[0]
    top, low = df.iloc[0], df.iloc[-1]
    parts = "".join(
        f'<div class="box">{f.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False)}</div>'
        for i, f in enumerate(figs)
    )
    kpis = [("Total Students", len(df)), ("Average Attendance", f"{df['Attendance'].mean():.1f}%"),
            ("Class Average", f"{df['Average'].mean():.1f}"), ("Topper", f"{top['Student']} ({top['Average']})"),
            ("Lowest", f"{low['Student']} ({low['Average']})"),
            (f"{name}: Rank / Grade", f"#{row['Rank']} / {row['Grade']}")]
    cards = "".join(f'<div class="k"><small>{k}</small><b>{v}</b></div>' for k, v in kpis)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Student Performance Dashboard</title>
<style>body{{background:#000;color:{TEXT};font-family:Segoe UI,Arial;margin:20px}}
h1{{color:{GREEN}}}.row{{display:flex;flex-wrap:wrap;gap:10px}}
.k{{background:{PANEL};border-left:5px solid {GREEN};padding:10px 16px;border-radius:8px;min-width:170px}}
.k small{{display:block;color:#8fd9ab}}.k b{{color:{GREEN};font-size:22px}}
.box{{background:{BLACK};border:1px solid {DARK_GREEN};border-radius:10px;margin:12px 0;padding:6px}}</style>
</head><body><h1>🎓 Student Performance Dashboard</h1><div class="row">{cards}</div>{parts}</body></html>"""
