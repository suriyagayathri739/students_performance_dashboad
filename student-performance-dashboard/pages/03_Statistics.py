"""Statistics page: insights and performance analysis."""
import streamlit as st
import plotly.express as px
from utils.helper import *

st.set_page_config(page_title="Statistics", page_icon="📈", layout="wide")
apply_css()
st.title("📈 Statistics & Performance Insights")
df = load_clean()

# ---------- Descriptive stats ----------
st.header("Descriptive statistics")
st.dataframe(df[SUBJECTS + ["Attendance", "Total Marks", "Average"]].describe().round(2), width="stretch")

# ---------- Subject-wise ----------
st.header("Subject-wise average")
avg = df[SUBJECTS].mean().round(2)
fig = px.bar(x=avg.index, y=avg.values, text=avg.values, labels={"x": "Subject", "y": "Class average"})
fig.update_traces(marker_color=[GOLD if v == avg.max() else RED if v == avg.min() else GREEN for v in avg.values])
st.plotly_chart(style_fig(fig, "Subject averages (gold = highest, red = lowest)", 350), width="stretch")
c = st.columns(2)
with c[0]: card("📈 Highest scoring subject", avg.idxmax(), f"Average {avg.max()}")
with c[1]: card("📉 Lowest scoring subject", avg.idxmin(), f"Average {avg.min()}")

# ---------- Top / Bottom ----------
st.header("Top 5 and Bottom 5 performers")
a, b = st.columns(2)
top5, bot5 = df.head(5), df.tail(5).sort_values("Average")
fig = px.bar(top5, x="Average", y="Student", orientation="h", text="Average", color_discrete_sequence=[GREEN])
fig.update_layout(yaxis=dict(autorange="reversed"), xaxis_range=[0, 105])
a.plotly_chart(style_fig(fig, "🏆 Top 5", 330), width="stretch")
fig = px.bar(bot5, x="Average", y="Student", orientation="h", text="Average", color_discrete_sequence=[RED])
fig.update_layout(xaxis_range=[0, 105])
b.plotly_chart(style_fig(fig, "⚠️ Bottom 5", 330), width="stretch")

# ---------- Correlation ----------
st.header("Correlation: Attendance vs Marks")
corr = df["Attendance"].corr(df["Average"])
strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
c = st.columns(2)
with c[0]: card("Correlation (Attendance, Average)", f"{corr:.2f}", f"{strength} positive relationship" if corr > 0 else f"{strength} negative")
with c[1]: card("Students with perfect attendance (100%)", int((df["Attendance"] == 100).sum()))
corr_s = df[SUBJECTS].corrwith(df["Attendance"]).round(2)
fig = px.bar(x=corr_s.index, y=corr_s.values, text=corr_s.values,
             labels={"x": "Subject", "y": "Correlation with attendance"}, color_discrete_sequence=[GREEN])
st.plotly_chart(style_fig(fig, "Attendance correlation with each subject", 330), width="stretch")

# ---------- Lists ----------
st.header("Special lists")
a, b = st.columns(2)
a.subheader("🎯 Perfect attendance (100%)")
a.dataframe(df[df["Attendance"] == 100][["Student", "Attendance", "Average", "Rank"]], width="stretch")
b.subheader("🛠️ Students requiring improvement")
limit = b.slider("Average below", 50, 90, 75)
need = df[(df["Average"] < limit) | (df["Attendance"] < 90)]
b.caption(f"Average below {limit} OR attendance below 90%")
b.dataframe(need[["Student", "Average", "Attendance", "Grade", "Rank"]], width="stretch")

st.header("Grade distribution")
g = df["Grade"].value_counts().reindex(["A+", "A", "B", "C", "D"]).fillna(0)
fig = px.bar(x=g.index, y=g.values, text=g.values, labels={"x": "Grade", "y": "Students"}, color_discrete_sequence=[GREEN])
st.plotly_chart(style_fig(fig, "Number of students per grade", 330), width="stretch")

st.header("Auto-generated insights")
top, low = df.iloc[0], df.iloc[-1]
st.markdown(f"""
- 🏆 **{top['Student']}** is the class topper with an average of **{top['Average']}**.
- ⚠️ **{low['Student']}** has the lowest average (**{low['Average']}**) and needs support.
- 📚 **{avg.idxmax()}** is the strongest subject, **{avg.idxmin()}** the weakest.
- 🔗 Attendance and marks have a **{strength}** correlation (**{corr:.2f}**): students who attend more tend to score higher.
- 🛠️ **{len(need)}** students need improvement under the current rule.
""")
