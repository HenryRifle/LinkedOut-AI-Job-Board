import streamlit as st
import pandas as pd
import plotly.express as px
from user_login import login_user, logout_user
import plotly.graph_objects as go


st.set_page_config(layout="wide")


if not login_user():
    st.stop()


if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()



#Importing the datasets
occupations_df_23 = pd.read_excel('project_data\\2023-33\\occupation.xlsx', sheet_name = 2, header = 1)
occupations_df_19 = pd.read_excel('project_data\\2019-29\\occupation.xlsx', sheet_name=2, header = 1)
occupations_df_23 = occupations_df_23[occupations_df_23['Occupation type'] != 'Summary']
occupations_df_19 = occupations_df_19[occupations_df_19['Occupation type'] != 'Summary']
occupations_df_23 = occupations_df_23.rename(columns={"2023 National Employment Matrix code" : "Occupation"})
occupations_df_19 = occupations_df_19.rename(columns={"2019 National Employment Matrix code" : "Occupation"})
occupations_df = pd.merge(occupations_df_23,occupations_df_19, on='Occupation', how='left')

education_df = pd.read_excel('project_data\\2023-33\\education.xlsx', sheet_name = 3, header = 1)
education_df.rename({'2023 National Employment Matrix title':'Occupation'})


industry_df = pd.read_excel('project_data\\2023-33\\industry.xlsx', sheet_name=11, header=1)

# Drop unnecessary columns
industry_df = industry_df.drop(columns=["Industry type", "Output, 2023[1][2]", "Output, 2033[1][2]", "Compound annual rate of change, output, 2023–33"])

# Rename columns for clarity
industry_df = industry_df.rename(columns={
    "Employment, 2023": "2023 Employment",
    "Employment, 2033": "2033 Employment",
    "2023 National Employment Matrix title": "Industry",
    "2023 National Employment Matrix code": "Code",
    "Employment change, numeric, 2023–33": "Prediction Numeric Change",
    "Employment change, percent, 2023–33": "Prediction Percent Change",
    "Compound annual rate of change, employment, 2023–33": "Prediction Annual Rate of Change"
})

# Clean up data
industry_df = industry_df.drop_duplicates(subset='Industry', keep='first')  # gets rid of dups
industry_df = industry_df.drop(industry_df.tail(5).index)  # drops the footnotes




base_tabs = st.tabs(["Industry Insights", "Occupation Insights"])



# INDUSTRY DASHBOARD
with base_tabs[0]:
    # Create Streamlit sidebar multiselect
    st.title("Employment Change by Industry (2023-2033)")

    selected_industries = st.multiselect(
        "Select Industries",
        options=industry_df['Industry'].unique(),
        default=industry_df['Industry'].unique()[:10]  # Default to first 10 for better visibility
    )

    # Create figure
    fig = go.Figure()

    # Filter and sort data
    filtered_df = industry_df[industry_df['Industry'].isin(selected_industries)].sort_values('2023 Employment', ascending=True)

    # Add lines connecting 2023 and 2033 points
    for idx, row in filtered_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['2023 Employment'], row['2033 Employment']],
            y=[row['Industry'], row['Industry']],
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add 2023 points
    fig.add_trace(go.Scatter(
        x=filtered_df['2023 Employment'],
        y=filtered_df['Industry'],
        mode='markers',
        name='2023',
        marker=dict(
            symbol='circle',
            size=12,
            color='#377eb8'
        ),
        hovertemplate="<b>%{y}</b><br>" +
                    "2023 Employment: %{x:,.0f} thousand<extra></extra>"
    ))

    # Add 2033 points
    fig.add_trace(go.Scatter(
        x=filtered_df['2033 Employment'],
        y=filtered_df['Industry'],
        mode='markers',
        name='2033',
        marker=dict(
            symbol='circle',
            size=12,
            color='#e41a1c'
        ),
        hovertemplate="<b>%{y}</b><br>" +
                    "2033 Employment: %{x:,.0f} thousand<extra></extra>"
    ))

    # Add change annotations
    for idx, row in filtered_df.iterrows():
        change = row['2033 Employment'] - row['2023 Employment']
        change_pct = (change / row['2023 Employment']) * 100
        fig.add_annotation(
            x=max(row['2023 Employment'], row['2033 Employment']) + filtered_df['2033 Employment'].max() * 0.02,
            y=row['Industry'],
            text=f"{'+' if change > 0 else ''}{change:,.0f} ({change_pct:+.1f}%)",
            showarrow=False,
            font=dict(
                size=10,
                color='green' if change > 0 else 'red'
            ),
            xanchor='left'
        )

    # Update layout
    fig.update_layout(
        height=max(600, len(selected_industries) * 40),
        width=1000,
        title="Employment Change by Industry (2023-2033)",
        xaxis_title="Employment Numbers (thousands)",
        yaxis_title="Industry",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template="plotly_white",
        xaxis=dict(
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='lightgray'
        ),
        margin=dict(r=150)  # Add right margin for annotations
    )

    # Add descriptive text
    st.write("""
    Interactive chart showing employment changes by industry between 2023 and 2033.
    - Blue dots represent 2023 employment
    - Red dots represent projected 2033 employment
    - Gray lines connect the same industry across years
    - Numbers on the right show absolute and percentage changes
    """)
    st.plotly_chart(fig, use_container_width=True)

    # Optionally, add a data table showing the numeric changes
    if st.checkbox("Show detailed data"):
        change_data = filtered_df[[
            'Industry', 
            '2023 Employment', 
            '2033 Employment', 
            'Prediction Numeric Change', 
            'Prediction Percent Change'
        ]]
        st.dataframe(change_data)





# OCCUPATION DASHBOARD
with base_tabs[1]:
    # Header
    st.title("Education, Employment, and Occupation Insights (2023–2033)")
    st.subheader("Interactive Dashboard for Exploring Workforce Trends and Future Projections")
    selected_occupation = st.selectbox("Select an Occupation:", occupations_df["2023 National Employment Matrix title"].unique().tolist())

    # Tabs for Navigation
    tabs = st.tabs(["Home", "Education Trends", "Employment Projections", "Occupation Insights", "User Recommendations", "Download Data"])

    # Home Tab
    with tabs[0]:
        occupation_data = occupations_df[occupations_df["2023 National Employment Matrix title"] == selected_occupation]
        st.header("Key Metrics")
        col1, col2 = st.columns(2)

        formatted_total_employment = f"{occupation_data['Employment, 2023'].values[0]*1000:,}"
        formatted_projected_employment = f"{occupation_data['Employment, 2033'].values[0]*1000:,}"
        formatted_percentage_growth = f"{occupation_data['Employment change, percent, 2023–33'].values[0]}%"
        formatted_average_salary = f"${occupation_data['Median annual wage, dollars, 2023[1]'].values[0]:,.0f}"

        with col1:
            st.metric("Total Employment (2023)", formatted_total_employment)
            st.metric("Projected Employment (2033)", formatted_projected_employment)
        with col2:
            st.metric("Percentage Growth", formatted_percentage_growth)
            st.metric("Average Salary", formatted_average_salary)



    # Education Trends Tab
    with tabs[1]:
        st.header(f"Education Trends for {selected_occupation}")

        #Get education data
        education_data = education_df[education_df['2023 National Employment Matrix code'] == occupation_data['Occupation'].astype(str).values[0]]

        education_levels = education_data.melt(id_vars=['2023 National Employment Matrix title'], value_vars=education_data.columns[1:], 
                                                var_name='Education Level', value_name='Percentage')

        fig = px.pie(education_levels, 
                    names='Education Level', 
                    values='Percentage', 
                    title=f'Education Level Distribution')

        st.plotly_chart(fig)

    # Employment Projections Tab
    with tabs[2]:
        st.header("Employment Projections")

        st.metric("Percentage Growth 2023-33", f"{occupation_data['Employment change, percent, 2023–33'].values[0]} %")

        #Create dataframe for employment growth
        employment_data = pd.DataFrame({
        "Year": ["2019", "2023", "2029", "2033"],
        "Employment": [
            occupation_data["Employment, 2019"].values[0],
            occupation_data["Employment, 2023"].values[0], 
            occupation_data["Employment, 2029"].values[0],
            occupation_data["Employment, 2033"].values[0]
        ]
    })

        #Line chart
        fig = px.line(
            employment_data,
            x="Year",
            y="Employment",
            markers=True,
            title=f"Employment Change for {selected_occupation} (2019-2033)",
            labels={"Employment": "Number of Employees", "Year": "Year"}
        )

        st.plotly_chart(fig)

    # Occupation Insights Tab
    with tabs[3]:
        st.header("Occupation Insights")
        # Add plots and interactivity here

    # User Recommendations Tab
    with tabs[4]:
        st.header("User Recommendations")
        # Add recommendation plots here

    # Download Data Tab
    with tabs[5]:
        st.header("Download Data")
        # Add download options here
