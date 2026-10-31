"""Visualizations page: many charts using Plotly, Matplotlib, Seaborn and Altair."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from utils.helper import *

st.set_page_config(page_title="Visualizations", page_icon="📊", layout="wide")
apply_css()
st.title("📊 Visualizations")
df = load_clean()

# ---------- Controls ----------
c = st.columns(3)
subject = c[0].selectbox("Choose subject", SUBJECTS)
sort_order = c[1].radio("Sort bars", ["High → Low", "Low → High", "A → Z"], horizontal=True)
students = c[2].multiselect("Filter students (empty = all)", df["Student"].tolist())
d = df[df["Student"].isin(students)] if students else df

if sort_order == "High → Low": d = d.sort_values(subject, ascending=False)
elif sort_order == "Low → High": d = d.sort_values(subject)
else: d = d.sort_values("Student")

st.caption("Hover on charts for details. Zoom: drag. Pan / reset: use the toolbar on top-right of each chart.")

# ---------- Plotly ----------
st.header("Plotly charts")
a, b = st.columns(2)

fig = px.bar(d, x="Student", y=subject, text=subject, color=subject, color_continuous_scale=GREENS)
fig.update_layout(xaxis_title="Student", yaxis_title=f"{subject} marks")
a.plotly_chart(style_fig(fig, f"Bar Chart: {subject} marks"), width="stretch")

fig = go.Figure()
for s in SUBJECTS:
    fig.add_scatter(x=d["Student"], y=d[s], mode="lines+markers", name=s)
fig.update_layout(xaxis_title="Student", yaxis_title="Marks")
b.plotly_chart(style_fig(fig, "Line Chart: all subjects"), width="stretch")

a, b = st.columns(2)
grades = d["Grade"].value_counts().reset_index()
grades.columns = ["Grade", "Students"]
fig = px.pie(grades, names="Grade", values="Students", hole=0.4, color_discrete_sequence=GREENS[::-1])
a.plotly_chart(style_fig(fig, "Pie (Donut) Chart: Grade distribution"), width="stretch")

fig = px.scatter(d, x="Attendance", y="Average", text="Student", trendline="ols", hover_data=["Rank"])
fig.update_traces(marker=dict(size=11, color=GREEN), textposition="top center", selector=dict(mode="markers+text"))
fig.update_layout(xaxis_title="Attendance (%)", yaxis_title="Average marks")
b.plotly_chart(style_fig(fig, "Scatter Plot: Attendance vs Average (with trend line)"), width="stretch")

a, b = st.columns(2)
fig = px.scatter(d, x="Attendance", y=subject, size="Total Marks", color="Average", hover_name="Student",
                 color_continuous_scale=GREENS, size_max=35)
fig.update_layout(xaxis_title="Attendance (%)", yaxis_title=f"{subject} marks")
a.plotly_chart(style_fig(fig, "Bubble Chart (size = total marks)"), width="stretch")

fig = px.histogram(d, x="Average", nbins=8, color_discrete_sequence=[GREEN])
fig.update_layout(xaxis_title="Average marks", yaxis_title="Number of students")
b.plotly_chart(style_fig(fig, "Histogram: Average marks"), width="stretch")

a, b = st.columns(2)
fig = px.box(d.melt(value_vars=SUBJECTS, var_name="Subject", value_name="Marks"), x="Subject", y="Marks",
             color="Subject", points="all", color_discrete_sequence=GREENS[::-1])
a.plotly_chart(style_fig(fig, "Box Plot: marks by subject"), width="stretch")

fig = px.area(d, x="Student", y=SUBJECTS, color_discrete_sequence=GREENS[2:])
fig.update_layout(xaxis_title="Student", yaxis_title="Marks")
b.plotly_chart(style_fig(fig, "Area Chart: marks by student"), width="stretch")

a, b = st.columns(2)
fig = px.treemap(d, path=["Grade", "Student"], values="Total Marks", color="Average", color_continuous_scale=GREENS)
a.plotly_chart(style_fig(fig, "Treemap: Grade → Student"), width="stretch")
fig = px.sunburst(d, path=["Grade", "Student"], values="Total Marks", color="Average", color_continuous_scale=GREENS)
b.plotly_chart(style_fig(fig, "Sunburst: Grade → Student"), width="stretch")

st.subheader("Radar Chart: compare students")
picks = st.multiselect("Students for radar", df["Student"].tolist(), default=df["Student"].head(3).tolist())
fig = go.Figure()
for n in picks:
    r = df[df["Student"] == n].iloc[0]
    fig.add_trace(go.Scatterpolar(r=[r[s] for s in SUBJECTS] + [r[SUBJECTS[0]]], theta=SUBJECTS + [SUBJECTS[0]],
                                  fill="toself", name=n, opacity=0.6))
fig.update_layout(polar=dict(bgcolor=PANEL, radialaxis=dict(range=[50, 100])))
st.plotly_chart(style_fig(fig, "Radar Chart", 450), width="stretch")

# ---------- Seaborn / Matplotlib ----------
st.header("Seaborn & Matplotlib charts")
plt.rcParams.update({"text.color": TEXT, "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT})
a, b = st.columns(2)

fig, ax = plt.subplots(figsize=(6, 5), facecolor=BLACK)
ax.set_facecolor(PANEL)
sns.heatmap(df[SUBJECTS + ["Attendance"]].corr(), annot=True, fmt=".2f", cmap="Greens", ax=ax, linewidths=1,
            linecolor=BLACK)
ax.set_title("Seaborn Heatmap: Correlation", color=GREEN)
a.pyplot(fig)

fig, ax = plt.subplots(figsize=(6, 5), facecolor=BLACK)
ax.set_facecolor(PANEL)
sns.heatmap(df.set_index("Student")[SUBJECTS], annot=True, fmt=".0f", cmap="Greens", ax=ax, cbar=False)
ax.set_title("Seaborn Heatmap: Marks of every student", color=GREEN)
b.pyplot(fig)

a, b = st.columns(2)
fig, ax = plt.subplots(figsize=(6, 4), facecolor=BLACK)
ax.set_facecolor(PANEL)
avg = df[SUBJECTS].mean().round(1)
bars = ax.bar(avg.index, avg.values, color=[GREEN if v == avg.max() else MID_GREEN for v in avg.values])
ax.bar_label(bars, color=TEXT)
ax.set_title("Matplotlib Bar: Subject-wise class average", color=GREEN)
ax.set_xlabel("Subject"); ax.set_ylabel("Average marks"); ax.set_ylim(0, 100)
a.pyplot(fig)

fig, ax = plt.subplots(figsize=(6, 4), facecolor=BLACK)
ax.set_facecolor(PANEL)
sns.violinplot(data=df[SUBJECTS], color=MID_GREEN, ax=ax)
ax.set_title("Seaborn Violin: mark distribution", color=GREEN)
ax.set_xlabel("Subject"); ax.set_ylabel("Marks")
b.pyplot(fig)

# ---------- Altair ----------
st.header("Altair chart")
chart = (alt.Chart(df).mark_circle(size=140, color=GREEN)
         .encode(x=alt.X("Attendance:Q", scale=alt.Scale(zero=False)), y=alt.Y("Average:Q", scale=alt.Scale(zero=False)),
                 tooltip=["Student", "Average", "Attendance", "Rank", "Grade"])
         .properties(title="Altair Scatter: hover, zoom and pan", height=400)
         .interactive())
st.altair_chart(chart, width="stretch")
