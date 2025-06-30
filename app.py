import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="HR Attrition Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Load Data ---
# Function to load data with caching to improve performance
@st.cache_data
def load_data(file_path):
    """Loads the dataset from the given file path."""
    try:
        df = pd.read_csv(file_path)
        # Convert Attrition to binary (1 for Yes, 0 for No) for easier analysis
        df['Attrition_Binary'] = df['Attrition'].apply(lambda x: 1 if x == 'Yes' else 0)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure 'EA.csv' is in the same directory.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        st.stop()

# Specify the path to your CSV file
csv_file_path = 'EA.csv'
df = load_data(csv_file_path)

# Check if data loaded successfully
if df is None:
    st.stop()

# --- Title and Introduction ---
st.title("📊 HR Attrition Insights Dashboard")
st.markdown("""
Welcome to the HR Attrition Insights Dashboard. This platform is designed for Head HR, Director HR, and other key stakeholders
to gain a comprehensive understanding of employee attrition within the organization.
Explore various factors influencing attrition through interactive charts, graphs, and tables to support data-driven decision-making.
""")

st.markdown("---")

# --- Sidebar Filters ---
st.sidebar.header("Global Filters")

# Attrition filter
selected_attrition = st.sidebar.multiselect(
    "Filter by Attrition Status",
    options=df['Attrition'].unique(),
    default=df['Attrition'].unique()
)

# Department filter
selected_department = st.sidebar.multiselect(
    "Filter by Department",
    options=df['Department'].unique(),
    default=df['Department'].unique()
)

# Job Role filter
selected_job_role = st.sidebar.multiselect(
    "Filter by Job Role",
    options=df['JobRole'].unique(),
    default=df['JobRole'].unique()
)

# Education Field filter
selected_education_field = st.sidebar.multiselect(
    "Filter by Education Field",
    options=df['EducationField'].unique(),
    default=df['EducationField'].unique()
)

# Monthly Income Slider
min_income, max_income = int(df['MonthlyIncome'].min()), int(df['MonthlyIncome'].max())
income_range = st.sidebar.slider(
    "Filter by Monthly Income",
    min_value=min_income,
    max_value=max_income,
    value=(min_income, max_income)
)

# Age Slider
min_age, max_age = int(df['Age'].min()), int(df['Age'].max())
age_range = st.sidebar.slider(
    "Filter by Age",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

# Apply filters
filtered_df = df[
    (df['Attrition'].isin(selected_attrition)) &
    (df['Department'].isin(selected_department)) &
    (df['JobRole'].isin(selected_job_role)) &
    (df['EducationField'].isin(selected_education_field)) &
    (df['MonthlyIncome'] >= income_range[0]) &
    (df['MonthlyIncome'] <= income_range[1]) &
    (df['Age'] >= age_range[0]) &
    (df['Age'] <= age_range[1])
]

# Check if the filtered DataFrame is empty
if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()


# --- Dashboard Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Demographics", "Job Metrics", "Satisfaction & Performance", "Raw Data"])

with tab1:
    st.header("Overall Attrition Insights")

    # Row for KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Total Employees")
        st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>{len(filtered_df):,}</h1>", unsafe_allow_html=True)
        st.markdown("This metric shows the total number of employees in the filtered dataset, providing a baseline for analysis.")

    with col2:
        attrition_count = filtered_df[filtered_df['Attrition'] == 'Yes'].shape[0]
        st.markdown("### Attrition Count")
        st.markdown(f"<h1 style='text-align: center; color: #FF6347;'>{attrition_count:,}</h1>", unsafe_allow_html=True)
        st.markdown("This indicates the absolute number of employees who have left the organization based on the applied filters.")

    with col3:
        total_employees = len(filtered_df)
        if total_employees > 0:
            attrition_rate = (attrition_count / total_employees) * 100
            st.markdown("### Attrition Rate (%)")
            st.markdown(f"<h1 style='text-align: center; color: #FF6347;'>{attrition_rate:.2f}%</h1>", unsafe_allow_html=True)
            st.markdown("The attrition rate provides a critical percentage of employees leaving, offering a normalized view for comparison.")
        else:
            st.markdown("### Attrition Rate (%)")
            st.markdown("<h1 style='text-align: center; color: #FF6347;'>N/A</h1>", unsafe_allow_html=True)
            st.markdown("The attrition rate cannot be calculated as there are no employees in the filtered dataset.")

    st.markdown("---")

    # 1. Attrition Distribution
    st.subheader("1. Attrition Distribution")
    st.markdown("This pie chart illustrates the proportion of employees who have left (attrition 'Yes') versus those who remain (attrition 'No'). It provides an immediate visual summary of the overall attrition status.")
    attrition_counts = filtered_df['Attrition'].value_counts().reset_index()
    attrition_counts.columns = ['Attrition', 'Count']
    fig1 = px.pie(attrition_counts, values='Count', names='Attrition', title='Employee Attrition Distribution',
                  color_discrete_map={'Yes':'#FF6347', 'No':'#4CAF50'})
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")

    # 2. Attrition by Department
    st.subheader("2. Attrition by Department")
    st.markdown("This bar chart shows how attrition varies across different departments. It helps identify departments with higher attrition rates, indicating potential areas for HR intervention.")
    attrition_by_department = filtered_df.groupby('Department')['Attrition_Binary'].mean().reset_index()
    attrition_by_department['Attrition_Rate'] = attrition_by_department['Attrition_Binary'] * 100
    fig2 = px.bar(attrition_by_department, x='Department', y='Attrition_Rate',
                  title='Attrition Rate by Department',
                  labels={'Attrition_Rate': 'Attrition Rate (%)'},
                  color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Reds)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")

    # 3. Attrition by Job Role
    st.subheader("3. Attrition by Job Role")
    st.markdown("This visualization breaks down attrition by specific job roles. Understanding attrition at this granular level can highlight roles that might be experiencing unique challenges or dissatisfaction.")
    attrition_by_jobrole = filtered_df.groupby('JobRole')['Attrition_Binary'].mean().reset_index()
    attrition_by_jobrole['Attrition_Rate'] = attrition_by_jobrole['Attrition_Binary'] * 100
    fig3 = px.bar(attrition_by_jobrole.sort_values('Attrition_Rate', ascending=False), x='JobRole', y='Attrition_Rate',
                  title='Attrition Rate by Job Role',
                  labels={'Attrition_Rate': 'Attrition Rate (%)'},
                  color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Reds)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("---")


with tab2:
    st.header("Demographic Analysis")

    # 4. Age Distribution
    st.subheader("4. Age Distribution (Overall and by Attrition)")
    st.markdown("These histograms illustrate the distribution of employee ages, both across the entire workforce and specifically for those who have left the company. It helps identify if certain age groups are more prone to attrition.")
    fig4_1 = px.histogram(filtered_df, x='Age', nbins=20, title='Overall Age Distribution',
                          color_discrete_sequence=['#4CAF50'])
    st.plotly_chart(fig4_1, use_container_width=True)

    fig4_2 = px.histogram(filtered_df, x='Age', color='Attrition', nbins=20,
                          title='Age Distribution by Attrition Status',
                          color_discrete_map={'Yes':'#FF6347', 'No':'#4CAF50'})
    st.plotly_chart(fig4_2, use_container_width=True)
    st.markdown("---")

    # 5. Attrition by Gender
    st.subheader("5. Attrition by Gender")
    st.markdown("This chart compares attrition rates between male and female employees. It can reveal if there are gender-specific patterns in employee retention.")
    attrition_by_gender = filtered_df.groupby('Gender')['Attrition_Binary'].mean().reset_index()
    attrition_by_gender['Attrition_Rate'] = attrition_by_gender['Attrition_Binary'] * 100
    fig5 = px.bar(attrition_by_gender, x='Gender', y='Attrition_Rate', title='Attrition Rate by Gender',
                  labels={'Attrition_Rate': 'Attrition Rate (%)'},
                  color='Gender', color_discrete_map={'Male':'#6A5ACD', 'Female':'#FF69B4'})
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("---")

    # 6. Attrition by Marital Status
    st.subheader("6. Attrition by Marital Status")
    st.markdown("This bar chart examines attrition rates based on an employee's marital status. Different life stages associated with marital status might influence an employee's decision to leave.")
    attrition_by_marital = filtered_df.groupby('MaritalStatus')['Attrition_Binary'].mean().reset_index()
    attrition_by_marital['Attrition_Rate'] = attrition_by_marital['Attrition_Binary'] * 100
    fig6 = px.bar(attrition_by_marital.sort_values('Attrition_Rate', ascending=False), x='MaritalStatus', y='Attrition_Rate',
                  title='Attrition Rate by Marital Status',
                  labels={'Attrition_Rate': 'Attrition Rate (%)'},
                  color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Blues)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown("---")

    # 7. Attrition by Education Field
    st.subheader("7. Attrition by Education Field")
    st.markdown("This chart analyzes attrition rates across different fields of education. It can help understand if specific educational backgrounds correlate with higher or lower retention.")
    attrition_by_edu_field = filtered_df.groupby('EducationField')['Attrition_Binary'].mean().reset_index()
    attrition_by_edu_field['Attrition_Rate'] = attrition_by_edu_field['Attrition_Binary'] * 100
    fig7 = px.bar(attrition_by_edu_field.sort_values('Attrition_Rate', ascending=False), x='EducationField', y='Attrition_Rate',
                  title='Attrition Rate by Education Field',
                  labels={'Attrition_Rate': 'Attrition Rate (%)'},
                  color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Greens)
    st.plotly_chart(fig7, use_container_width=True)
    st.markdown("---")

    # 8. Attrition by Education Level
    st.subheader("8. Attrition by Education Level")
    st.markdown("This bar chart visualizes attrition based on the employee's education level (1 to 5). It helps determine if higher or lower education levels impact an employee's likelihood to leave.")
    attrition_by_education = filtered_df.groupby('Education')['Attrition_Binary'].mean().reset_index()
    attrition_by_education['Attrition_Rate'] = attrition_by_education['Attrition_Binary'] * 100
    fig8 = px.bar(attrition_by_education.sort_values('Education'), x='Education', y='Attrition_Rate',
                  title='Attrition Rate by Education Level',
                  labels={'Education': 'Education Level (1=Below College, 5=Doctor)', 'Attrition_Rate': 'Attrition Rate (%)'},
                  color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Purp)
    st.plotly_chart(fig8, use_container_width=True)
    st.markdown("---")

with tab3:
    st.header("Job-Related Metrics Analysis")

    # 9. Monthly Income Distribution
    st.subheader("9. Monthly Income Distribution (Overall and by Attrition)")
    st.markdown("These histograms display the distribution of monthly income for all employees and specifically for those who left. It helps identify if income level is a significant factor in attrition.")
    fig9_1 = px.histogram(filtered_df, x='MonthlyIncome', nbins=30, title='Overall Monthly Income Distribution',
                          color_discrete_sequence=['#F08080'])
    st.plotly_chart(fig9_1, use_container_width=True)

    fig9_2 = px.histogram(filtered_df, x='MonthlyIncome', color='Attrition', nbins=30,
                          title='Monthly Income Distribution by Attrition Status',
                          color_discrete_map={'Yes':'#FF6347', 'No':'#4CAF50'})
    st.plotly_chart(fig9_2, use_container_width=True)
    st.markdown("---")

    # 10. Attrition by Job Level
    st.subheader("10. Attrition by Job Level")
    st.markdown("This bar chart examines attrition rates across different job levels (1 to 5). It can reveal if certain seniority levels are more prone to attrition.")
    attrition_by_joblevel = filtered_df.groupby('JobLevel')['Attrition_Binary'].mean().reset_index()
    attrition_by_joblevel['Attrition_Rate'] = attrition_by_joblevel['Attrition_Binary'] * 100
    fig10 = px.bar(attrition_by_joblevel.sort_values('JobLevel'), x='JobLevel', y='Attrition_Rate',
                   title='Attrition Rate by Job Level',
                   labels={'JobLevel': 'Job Level (1=Entry, 5=Executive)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Oranges)
    st.plotly_chart(fig10, use_container_width=True)
    st.markdown("---")

    # 11. Attrition by Business Travel
    st.subheader("11. Attrition by Business Travel Frequency")
    st.markdown("This chart analyzes attrition based on the frequency of business travel. High travel requirements can sometimes contribute to dissatisfaction and, consequently, attrition.")
    attrition_by_travel = filtered_df.groupby('BusinessTravel')['Attrition_Binary'].mean().reset_index()
    attrition_by_travel['Attrition_Rate'] = attrition_by_travel['Attrition_Binary'] * 100
    fig11 = px.bar(attrition_by_travel.sort_values('Attrition_Rate', ascending=False), x='BusinessTravel', y='Attrition_Rate',
                   title='Attrition Rate by Business Travel Frequency',
                   labels={'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Viridis)
    st.plotly_chart(fig11, use_container_width=True)
    st.markdown("---")

    # 12. Attrition by Overtime
    st.subheader("12. Attrition by Overtime")
    st.markdown("This chart explores the relationship between working overtime and attrition. Employees frequently working overtime might experience burnout, leading to a higher likelihood of leaving.")
    attrition_by_overtime = filtered_df.groupby('OverTime')['Attrition_Binary'].mean().reset_index()
    attrition_by_overtime['Attrition_Rate'] = attrition_by_overtime['Attrition_Binary'] * 100
    fig12 = px.bar(attrition_by_overtime, x='OverTime', y='Attrition_Rate', title='Attrition Rate by Overtime',
                   labels={'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig12, use_container_width=True)
    st.markdown("---")

    # 13. Monthly Income vs. Years at Company
    st.subheader("13. Monthly Income vs. Years at Company (Colored by Attrition)")
    st.markdown("This scatter plot visualizes the relationship between monthly income and years spent at the company, with points colored by attrition status. It can highlight if low income or short tenure are linked to attrition.")
    fig13 = px.scatter(filtered_df, x='YearsAtCompany', y='MonthlyIncome', color='Attrition',
                       title='Monthly Income vs. Years at Company by Attrition',
                       labels={'YearsAtCompany': 'Years at Company', 'MonthlyIncome': 'Monthly Income'},
                       color_discrete_map={'Yes':'#FF6347', 'No':'#4CAF50'})
    st.plotly_chart(fig13, use_container_width=True)
    st.markdown("---")

    # 14. Attrition by Years At Company (Binned)
    st.subheader("14. Attrition by Years At Company")
    st.markdown("This chart groups employees by their years at the company and shows the attrition rate for each tenure group. It helps identify if early-career employees or long-tenured employees are more likely to leave.")
    # Create bins for YearsAtCompany
    bins = [0, 1, 3, 5, 10, 15, 20, 30, 40]
    labels = ['<1', '1-3', '3-5', '5-10', '10-15', '15-20', '20-30', '30+']
    filtered_df['YearsAtCompany_Binned'] = pd.cut(filtered_df['YearsAtCompany'], bins=bins, labels=labels, right=False)
    attrition_by_years_company = filtered_df.groupby('YearsAtCompany_Binned')['Attrition_Binary'].mean().reset_index()
    attrition_by_years_company['Attrition_Rate'] = attrition_by_years_company['Attrition_Binary'] * 100
    fig14 = px.bar(attrition_by_years_company.sort_values('YearsAtCompany_Binned'), x='YearsAtCompany_Binned', y='Attrition_Rate',
                   title='Attrition Rate by Years At Company',
                   labels={'YearsAtCompany_Binned': 'Years At Company (Binned)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Thermal)
    st.plotly_chart(fig14, use_container_width=True)
    st.markdown("---")

    # 15. Attrition by Years In Current Role
    st.subheader("15. Attrition by Years In Current Role")
    st.markdown("This chart analyzes how attrition rates change based on how long an employee has been in their current role. Stagnation in a role can sometimes lead to employees seeking opportunities elsewhere.")
    attrition_by_years_current_role = filtered_df.groupby('YearsInCurrentRole')['Attrition_Binary'].mean().reset_index()
    attrition_by_years_current_role['Attrition_Rate'] = attrition_by_years_current_role['Attrition_Binary'] * 100
    fig15 = px.bar(attrition_by_years_current_role.sort_values('YearsInCurrentRole'), x='YearsInCurrentRole', y='Attrition_Rate',
                   title='Attrition Rate by Years In Current Role',
                   labels={'YearsInCurrentRole': 'Years In Current Role', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Electric)
    st.plotly_chart(fig15, use_container_width=True)
    st.markdown("---")

    # 16. Attrition by Number of Companies Worked
    st.subheader("16. Attrition by Number of Companies Worked")
    st.markdown("This bar chart explores attrition based on the number of previous companies an employee has worked for. It might indicate if individuals with a history of frequent job changes are more likely to leave.")
    attrition_by_num_companies = filtered_df.groupby('NumCompaniesWorked')['Attrition_Binary'].mean().reset_index()
    attrition_by_num_companies['Attrition_Rate'] = attrition_by_num_companies['Attrition_Binary'] * 100
    fig16 = px.bar(attrition_by_num_companies.sort_values('NumCompaniesWorked'), x='NumCompaniesWorked', y='Attrition_Rate',
                   title='Attrition Rate by Number of Companies Worked',
                   labels={'NumCompaniesWorked': 'Number of Companies Worked', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Dense)
    st.plotly_chart(fig16, use_container_width=True)
    st.markdown("---")

    # 17. Attrition by Years Since Last Promotion
    st.subheader("17. Attrition by Years Since Last Promotion")
    st.markdown("This chart investigates attrition rates concerning the time elapsed since an employee's last promotion. A longer gap might suggest a lack of career progression, potentially contributing to attrition.")
    attrition_by_promotion = filtered_df.groupby('YearsSinceLastPromotion')['Attrition_Binary'].mean().reset_index()
    attrition_by_promotion['Attrition_Rate'] = attrition_by_promotion['Attrition_Binary'] * 100
    fig17 = px.bar(attrition_by_promotion.sort_values('YearsSinceLastPromotion'), x='YearsSinceLastPromotion', y='Attrition_Rate',
                   title='Attrition Rate by Years Since Last Promotion',
                   labels={'YearsSinceLastPromotion': 'Years Since Last Promotion', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Rainbow)
    st.plotly_chart(fig17, use_container_width=True)
    st.markdown("---")


with tab4:
    st.header("Satisfaction and Performance Analysis")

    # 18. Attrition by Environment Satisfaction
    st.subheader("18. Attrition by Environment Satisfaction")
    st.markdown("This bar chart shows attrition rates based on employees' satisfaction with their work environment. A poor environment can significantly impact an employee's decision to stay.")
    attrition_by_env_sat = filtered_df.groupby('EnvironmentSatisfaction')['Attrition_Binary'].mean().reset_index()
    attrition_by_env_sat['Attrition_Rate'] = attrition_by_env_sat['Attrition_Binary'] * 100
    fig18 = px.bar(attrition_by_env_sat.sort_values('EnvironmentSatisfaction'), x='EnvironmentSatisfaction', y='Attrition_Rate',
                   title='Attrition Rate by Environment Satisfaction',
                   labels={'EnvironmentSatisfaction': 'Environment Satisfaction (1=Low, 4=High)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Plotly3)
    st.plotly_chart(fig18, use_container_width=True)
    st.markdown("---")

    # 19. Attrition by Job Satisfaction
    st.subheader("19. Attrition by Job Satisfaction")
    st.markdown("This chart analyzes attrition rates based on employee job satisfaction levels. It's a direct indicator of how contentment with job duties affects retention.")
    attrition_by_job_sat = filtered_df.groupby('JobSatisfaction')['Attrition_Binary'].mean().reset_index()
    attrition_by_job_sat['Attrition_Rate'] = attrition_by_job_sat['Attrition_Binary'] * 100
    fig19 = px.bar(attrition_by_job_sat.sort_values('JobSatisfaction'), x='JobSatisfaction', y='Attrition_Rate',
                   title='Attrition Rate by Job Satisfaction',
                   labels={'JobSatisfaction': 'Job Satisfaction (1=Low, 4=High)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Teal)
    st.plotly_chart(fig19, use_container_width=True)
    st.markdown("---")

    # 20. Attrition by Relationship Satisfaction
    st.subheader("20. Attrition by Relationship Satisfaction")
    st.markdown("This bar chart illustrates attrition rates based on an employee's satisfaction with their relationships at work. Healthy workplace relationships often contribute to higher retention.")
    attrition_by_rel_sat = filtered_df.groupby('RelationshipSatisfaction')['Attrition_Binary'].mean().reset_index()
    attrition_by_rel_sat['Attrition_Rate'] = attrition_by_rel_sat['Attrition_Binary'] * 100
    fig20 = px.bar(attrition_by_rel_sat.sort_values('RelationshipSatisfaction'), x='RelationshipSatisfaction', y='Attrition_Rate',
                   title='Attrition Rate by Relationship Satisfaction',
                   labels={'RelationshipSatisfaction': 'Relationship Satisfaction (1=Low, 4=High)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Aggrnyl)
    st.plotly_chart(fig20, use_container_width=True)
    st.markdown("---")

    # 21. Attrition by Work Life Balance
    st.subheader("21. Attrition by Work Life Balance")
    st.markdown("This chart shows attrition rates against different levels of work-life balance. Poor work-life balance is a common reason for employees seeking new opportunities.")
    attrition_by_wlb = filtered_df.groupby('WorkLifeBalance')['Attrition_Binary'].mean().reset_index()
    attrition_by_wlb['Attrition_Rate'] = attrition_by_wlb['Attrition_Binary'] * 100
    fig21 = px.bar(attrition_by_wlb.sort_values('WorkLifeBalance'), x='WorkLifeBalance', y='Attrition_Rate',
                   title='Attrition Rate by Work Life Balance',
                   labels={'WorkLifeBalance': 'Work Life Balance (1=Bad, 4=Best)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Pubu)
    st.plotly_chart(fig21, use_container_width=True)
    st.markdown("---")

    # 22. Attrition by Performance Rating
    st.subheader("22. Attrition by Performance Rating")
    st.markdown("This bar chart investigates attrition based on an employee's performance rating. It can help understand if top or low performers are more likely to leave.")
    attrition_by_perf = filtered_df.groupby('PerformanceRating')['Attrition_Binary'].mean().reset_index()
    attrition_by_perf['Attrition_Rate'] = attrition_by_perf['Attrition_Binary'] * 100
    fig22 = px.bar(attrition_by_perf.sort_values('PerformanceRating'), x='PerformanceRating', y='Attrition_Rate',
                   title='Attrition Rate by Performance Rating',
                   labels={'PerformanceRating': 'Performance Rating (3=Excellent, 4=Outstanding)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.Sunset)
    st.plotly_chart(fig22, use_container_width=True)
    st.markdown("---")

    # 23. Attrition by Job Involvement
    st.subheader("23. Attrition by Job Involvement")
    st.markdown("This chart explores attrition based on job involvement levels. Employees with low involvement might feel disengaged, increasing their propensity to leave.")
    attrition_by_job_involvement = filtered_df.groupby('JobInvolvement')['Attrition_Binary'].mean().reset_index()
    attrition_by_job_involvement['Attrition_Rate'] = attrition_by_job_involvement['Attrition_Binary'] * 100
    fig23 = px.bar(attrition_by_job_involvement.sort_values('JobInvolvement'), x='JobInvolvement', y='Attrition_Rate',
                   title='Attrition Rate by Job Involvement',
                   labels={'JobInvolvement': 'Job Involvement (1=Low, 4=High)', 'Attrition_Rate': 'Attrition Rate (%)'},
                   color='Attrition_Rate', color_continuous_scale=px.colors.sequential.YlOrRd)
    st.plotly_chart(fig23, use_container_width=True)
    st.markdown("---")

    # 24. Average Monthly Income by Education and Attrition
    st.subheader("24. Average Monthly Income by Education and Attrition")
    st.markdown("This grouped bar chart displays the average monthly income for different education levels, separated by attrition status. It helps identify if income expectations differ based on education, influencing attrition.")
    avg_income_edu_attrition = filtered_df.groupby(['Education', 'Attrition'])['MonthlyIncome'].mean().reset_index()
    fig24 = px.bar(avg_income_edu_attrition, x='Education', y='MonthlyIncome', color='Attrition',
                   barmode='group', title='Average Monthly Income by Education and Attrition',
                   labels={'MonthlyIncome': 'Average Monthly Income', 'Education': 'Education Level'},
                   color_discrete_map={'Yes': '#FF6347', 'No': '#4CAF50'})
    st.plotly_chart(fig24, use_container_width=True)
    st.markdown("---")


with tab5:
    st.header("Raw Data")
    st.markdown("This tab displays the raw data from the filtered dataset. You can use the global filters on the left sidebar to narrow down the data displayed here.")
    st.dataframe(filtered_df)

st.sidebar.markdown("---")
st.sidebar.info("Adjust the filters above to explore different segments of the HR data.")

st.markdown("---")
st.markdown("Dashboard created with ❤️ using Streamlit")
