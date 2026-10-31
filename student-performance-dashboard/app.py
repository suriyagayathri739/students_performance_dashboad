"""Home page: KPI overview + student dropdown dashboard."""
import os
import streamlit as st
from utils.helper import *

st.set_page_config(page_title="Student Performance Dashboard", page_icon="🎓", layout="wide")
apply_css()

df = load_clean()
top, low = df.iloc[0], df.iloc[-1]

st.title("🎓 Student Performance Dashboard")
st.caption("Use the sidebar to open the Dataset, Visualizations and Statistics pages.")

# ---------- KPI cards ----------
c = st.columns(4)
with c[0]: card("👥 Total Students", len(df))
with c[1]: card("📅 Average Attendance", f"{df['Attendance'].mean():.1f}%")
with c[2]: card("🏆 Highest Average", f"{top['Average']}", top["Student"])
with c[3]: card("⚠️ Lowest Average", f"{low['Average']}", low["Student"])
c = st.columns(3)
with c[0]: card("📊 Class Average", f"{df['Average'].mean():.1f}")
with c[1]: card("⭐ Students Above 85%", int((df["Average"] > 85).sum()))
with c[2]: card("🔻 Students Below 60%", int((df["Average"] < 60).sum()))

st.success(f"🏆 Class Topper: **{top['Student']}** with average **{top['Average']}** "
           f"(Total {top['Total Marks']:.0f}, Grade {top['Grade']})")

# ---------- Student selector ----------
st.header("🔎 Student Analysis")
name = st.selectbox("Select a student", df["Student"].tolist(), index=0)
row = df[df["Student"] == name].iloc[0]

c = st.columns(5)
with c[0]: card("Rank", f"#{row['Rank']}", f"of {len(df)}")
with c[1]: card("Average", row["Average"])
with c[2]: card("Total Marks", f"{row['Total Marks']:.0f}")
with c[3]: card("Grade", row["Grade"])
with c[4]: card("Attendance", f"{row['Attendance']:.0f}%")
if name == top["Student"]:
    st.warning("🏆 This student is the CLASS TOPPER!")

left, right = st.columns(2)
left.plotly_chart(student_bar(df, name), width="stretch")
right.plotly_chart(student_radar(df, name), width="stretch")

left, right = st.columns(2)
left.plotly_chart(attendance_vs_avg(df, name), width="stretch")
right.plotly_chart(ranking_bar(df), width="stretch")

# ---------- Compare students ----------
st.header("⚖️ Compare Students")
picks = st.multiselect("Pick students to compare", df["Student"].tolist(), default=[name, top["Student"]])
if picks:
    import plotly.express as px
    long = df[df["Student"].isin(picks)].melt(id_vars="Student", value_vars=SUBJECTS,
                                              var_name="Subject", value_name="Marks")
    fig = px.bar(long, x="Subject", y="Marks", color="Student", barmode="group")
    st.plotly_chart(style_fig(fig, "Subject-wise comparison", 400), width="stretch")

# ---------- Save as HTML ----------
st.header("💾 Save Dashboard as HTML")
html = build_html_report(df, name)
st.download_button("⬇️ Download dashboard (.html)", html, file_name=f"dashboard_{name}.html", mime="text/html")
if st.button("Also save a copy in the assets folder"):
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ASSETS, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(html)
    st.success("Saved to assets/dashboard.html")
