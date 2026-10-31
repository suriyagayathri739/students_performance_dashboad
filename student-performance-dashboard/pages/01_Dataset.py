"""Dataset page: raw data, info, data cleaning module, filters, export."""
import io
import streamlit as st
import plotly.express as px
from utils.helper import *

st.set_page_config(page_title="Dataset", page_icon="📁", layout="wide")
apply_css()
st.title("📁 Dataset & Data Cleaning")

raw = load_raw()
df = load_clean()
cols = SUBJECTS + ["Attendance"]

tab1, tab2, tab3 = st.tabs(["Raw Data", "Cleaning Module", "Cleaned Data + Filters"])

# ---------- Raw data ----------
with tab1:
    st.subheader("Raw dataset (as read from the CSV)")
    st.dataframe(raw, width="stretch")
    buf = io.StringIO()
    raw.info(buf=buf)
    st.subheader("Dataset information")
    st.code(buf.getvalue())
    st.subheader("Descriptive statistics (raw)")
    st.dataframe(raw.describe().round(2), width="stretch")

# ---------- Cleaning ----------
with tab2:
    st.subheader("1. Missing value detection")
    missing = raw[cols].isnull().sum()
    fig = px.bar(x=missing.index, y=missing.values, text=missing.values,
                 labels={"x": "Column", "y": "Missing values"})
    st.plotly_chart(style_fig(fig, "Missing (Null) values per column", 330), width="stretch")
    st.dataframe(raw[raw[cols].isnull().any(axis=1)], width="stretch")

    st.subheader("2. Zero value detection")
    zeros = (raw[cols] == 0).sum()
    fig = px.bar(x=zeros.index, y=zeros.values, text=zeros.values,
                 labels={"x": "Column", "y": "Zero values"})
    st.plotly_chart(style_fig(fig, "Zero values per column", 330), width="stretch")
    st.dataframe(raw[(raw[cols] == 0).any(axis=1)], width="stretch")

    st.subheader("3. Missing / zero value handling")
    st.info("A mark of **0** is treated as invalid (absent / entry error) and, together with **Null**, "
            "is replaced by the **median** of that column. The median is used because it is not "
            "affected by extreme values.")
    st.write("Median used for filling:")
    st.dataframe(raw[cols].replace(0, float("nan")).median().to_frame("Median").T)

    st.subheader("4. Duplicate detection")
    dups = raw.duplicated().sum()
    st.write(f"Duplicate rows found: **{dups}**  |  Duplicate student names: **{raw['Student'].duplicated().sum()}**")
    st.write("✅ Duplicates removed (if any) in the cleaned data.")

    st.subheader("5. Outlier detection (IQR method)")
    fig = px.box(df.melt(value_vars=cols, var_name="Column", value_name="Value"),
                 x="Column", y="Value", points="all")
    st.plotly_chart(style_fig(fig, "Box plot of cleaned data (dots outside the box = outliers)", 400),
                    width="stretch")
    for col in cols:
        out = outliers_iqr(df, col)
        if len(out):
            st.write(f"**{col}** outliers: " + ", ".join(f"{r.Student} ({r[col]:.0f})" for _, r in out.iterrows()))
        else:
            st.write(f"**{col}**: no outliers")

    st.subheader("6. Data validation")
    checks = {
        "All marks between 0 and 100": bool(((df[SUBJECTS] >= 0) & (df[SUBJECTS] <= 100)).all().all()),
        "Attendance between 0 and 100": bool(df["Attendance"].between(0, 100).all()),
        "No missing values left": bool(df[cols].isnull().sum().sum() == 0),
        "No zero values left": bool((df[cols] == 0).sum().sum() == 0),
        "No duplicate students": bool(not df["Student"].duplicated().any()),
    }
    for k, v in checks.items():
        st.write(("✅ " if v else "❌ ") + k)

# ---------- Cleaned data + filter ----------
with tab3:
    st.subheader("Cleaned data with Average, Total Marks, Grade and Rank")
    c = st.columns(4)
    search = c[0].text_input("🔍 Search student name")
    mark_range = c[1].slider("Average marks", 0, 100, (0, 100))
    att_range = c[2].slider("Attendance %", 0, 100, (0, 100))
    sort_by = c[3].selectbox("Sort by", ["Rank", "Average", "Total Marks", "Attendance", "Student"])

    f = df[df["Student"].str.contains(search, case=False)]
    f = f[f["Average"].between(*mark_range) & f["Attendance"].between(*att_range)]
    f = f.sort_values(sort_by, ascending=(sort_by in ["Rank", "Student"]))
    st.write(f"Showing **{len(f)}** of {len(df)} students")
    st.dataframe(f, width="stretch")

    st.download_button("⬇️ Export processed data (CSV)", f.to_csv(index=False),
                       file_name="processed_student_performance.csv", mime="text/csv")
