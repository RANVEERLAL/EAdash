import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="HR Attrition Dashboard", layout="wide")
st.title("📊 Employee Attrition Insights Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("EA.csv")

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filter Employees")
dept = st.sidebar.multiselect("Select Department", df['Department'].unique())
job = st.sidebar.multiselect("Select Job Role", df['JobRole'].unique())
age = st.sidebar.slider("Age Range", int(df['Age'].min()), int(df['Age'].max()), (25, 45))

filtered_df = df[
    (df['Age'].between(age[0], age[1])) &
    (df['Department'].isin(dept) if dept else True) &
    (df['JobRole'].isin(job) if job else True)
]

tabs = st.tabs(["Overview", "Demographics", "Job & Performance", "Income & Compensation", "Correlations"])

with tabs[0]:
    st.header("Overall View")
    st.write("### 1. Attrition Distribution")
    st.plotly_chart(px.pie(df, names='Attrition'), use_container_width=True)

    st.write("### 2. Attrition by Department")
    st.plotly_chart(px.histogram(df, x="Department", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 3. Attrition by Gender")
    st.plotly_chart(px.histogram(df, x="Gender", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 4. Attrition by Marital Status")
    st.plotly_chart(px.histogram(df, x="MaritalStatus", color="Attrition", barmode="group"), use_container_width=True)

with tabs[1]:
    st.header("Demographic Insights")
    st.write("### 5. Age Distribution by Attrition")
    st.plotly_chart(px.histogram(filtered_df, x="Age", color="Attrition", nbins=30), use_container_width=True)

    st.write("### 6. Education Field vs Attrition")
    st.plotly_chart(px.histogram(df, x="EducationField", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 7. Distance From Home")
    st.plotly_chart(px.box(df, x="Attrition", y="DistanceFromHome", color="Attrition"), use_container_width=True)

    st.write("### 8. Environment Satisfaction")
    st.plotly_chart(px.histogram(df, x="EnvironmentSatisfaction", color="Attrition", barmode="group"), use_container_width=True)

with tabs[2]:
    st.header("Job Level & Performance")
    st.write("### 9. Job Role vs Attrition")
    st.plotly_chart(px.histogram(df, x="JobRole", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 10. Overtime vs Attrition")
    st.plotly_chart(px.histogram(df, x="OverTime", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 11. Performance Rating")
    st.plotly_chart(px.histogram(df, x="PerformanceRating", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 12. Job Involvement")
    st.plotly_chart(px.histogram(df, x="JobInvolvement", color="Attrition", barmode="group"), use_container_width=True)

with tabs[3]:
    st.header("Compensation Trends")
    st.write("### 13. Monthly Income Distribution")
    st.plotly_chart(px.box(df, x="Attrition", y="MonthlyIncome", color="Attrition"), use_container_width=True)

    st.write("### 14. Stock Option Level")
    st.plotly_chart(px.histogram(df, x="StockOptionLevel", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 15. Total Working Years")
    st.plotly_chart(px.box(df, x="Attrition", y="TotalWorkingYears", color="Attrition"), use_container_width=True)

    st.write("### 16. Years at Company")
    st.plotly_chart(px.box(df, x="Attrition", y="YearsAtCompany", color="Attrition"), use_container_width=True)

with tabs[4]:
    st.header("Advanced Correlation & Analysis")
    st.write("### 17. Correlation Heatmap")
    numeric_cols = df.select_dtypes(include=['int64']).drop(columns=['EmployeeCount', 'StandardHours']).corr()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(numeric_cols, cmap='coolwarm', annot=True, ax=ax)
    st.pyplot(fig)

    st.write("### 18. Work Life Balance")
    st.plotly_chart(px.histogram(df, x="WorkLifeBalance", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 19. Training Times Last Year")
    st.plotly_chart(px.histogram(df, x="TrainingTimesLastYear", color="Attrition", barmode="group"), use_container_width=True)

    st.write("### 20. Interactive Data Table")
    st.dataframe(filtered_df)
