import streamlit as st
import pandas as pd
import plotly.express as px
from user_login import login_user, logout_user
import plotly.graph_objects as go
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path


st.set_page_config(layout="wide")


if not login_user():
    st.stop()


if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()



#Importing the datasets
occupations_df_23 = pd.read_excel('project_data/2023-33/occupation.xlsx', sheet_name = 2, header = 1)
occupations_df_19 = pd.read_excel('project_data/2019-29/occupation.xlsx', sheet_name = 2, header = 1)
occupations_df_23 = occupations_df_23[occupations_df_23['Occupation type'] != 'Summary']
occupations_df_19 = occupations_df_19[occupations_df_19['Occupation type'] != 'Summary']
occupations_df_23 = occupations_df_23.rename(columns={"2023 National Employment Matrix code" : "Occupation"})
occupations_df_19 = occupations_df_19.rename(columns={"2019 National Employment Matrix code" : "Occupation"})
occupations_df = pd.merge(occupations_df_23,occupations_df_19, on='Occupation', how='left')

education_df = pd.read_excel('project_data/2023-33/education.xlsx', sheet_name = 3, header = 1)
education_df.rename({'2023 National Employment Matrix title':'Occupation'})


skills_df = pd.read_excel('project_data/2023-33/skills.xlsx', sheet_name=2, header = 1)
skills_df = skills_df.drop(columns = ['Employment, 2023','Employment, 2033','Employment change, numeric, 2023–33','Employment change, percent, 2023–33'])
skills_df = skills_df.rename(columns = {"2023 National Employment Matrix title" : "Occupation","Typical education needed for entry" : "Education","Median annual wage, dollars, 2023[1]" : "Salary"})
skills_df['Education'] = skills_df['Education'].map({'-' : 0, 'No formal educational credential' : 0,'High school diploma or equivalent' : 1, 'Some college, no degree' : 1, 'Postsecondary nondegree award' : 1,'Associate\'s degree' : 2, 'Bachelor\'s degree' : 3, 'Master\'s degree' : 4, 'Doctoral or professional degree' : 5})

#Weights defining AI susceptibility for each skill
weights = {
    "Adaptability": 0.08,
    "Computers and information technology": 0.09,
    "Creativity and innovation": 0.09,
    "Critical and analytical thinking": 0.08,
    "Customer service": 0.06,
    "Detail oriented": 0.05,
    "Fine motor": 0.03,
    "Interpersonal": 0.08,
    "Leadership": 0.08,
    "Mathematics": 0.08,
    "Mechanical": 0.03,
    "Physical strength and stamina": 0.02,
    "Problem solving and decision making": 0.07,
    "Project management": 0.06,
    "Science": 0.06,
    "Speaking and listening": 0.02,
    "Writing and reading": 0.02,
}


skills_df["AI Susceptibility Score"] = skills_df[list(weights.keys())].mul(weights.values()).sum(axis=1)

def categorize(index):
    if index >= 3.5:
        return "Low"
    elif 3.0 <= index < 3.5:
        return "Medium"
    else:
        return "High"

skills_df["AI Susceptibility"] = skills_df["AI Susceptibility Score"].apply(categorize)

user_df = pd.read_excel('project_data/generated_data/users.xlsx')
current_user = user_df[user_df['Name'] == st.session_state.current_user]


industry_df = pd.read_excel('project_data/2023-33/industry.xlsx', sheet_name=11, header=1)

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

users_df = pd.read_excel('project_data/generated_data/users.xlsx', sheet_name=0)

user = st.session_state.current_user
user_df = users_df[users_df['Name'] == user]

skills_by_major_occupations_df = pd.read_excel('project_data/2023-33/skills.xlsx', sheet_name=1, header = 1)

skills_by_major_occupations_df = skills_by_major_occupations_df.rename(columns = {"2023 National Employment Matrix title" : "Occupation Category"})
skills_by_major_occupations_df = skills_by_major_occupations_df[skills_by_major_occupations_df["Occupation Category"] != "Total, all occupations"]
skills_by_major_occupations_df = skills_by_major_occupations_df[~skills_by_major_occupations_df.iloc[:, 0].str.contains("Footnotes|Note|Source", na=False)]

skills_by_major_occupations_df = skills_by_major_occupations_df.reset_index(drop=True)



labor_force_df = pd.read_excel('project_data/2019-29/labor-force.xlsx', sheet_name=None)
labor_force_trends_df = labor_force_df["Table 3.1"]

custom_headers = [
    'group','1999', '2009', '2019', '2029', 
    'change_1999_09', 'change_2009_19', 'change_2019_29',
    'percent_change_1999_09', 'percent_change_2009_19', 'percent_change_2019_29',
    'percent_distribution_1999', 'percent_distribution_2009', 'percent_distribution_2019', 'percent_distribution_2029',
    'annual_growth_rate_1999_09', 'annual_growth_rate_2009_19', 'annual_growth_rate_2019_29'
]


# Drop the first two rows
labor_force_trends_df = labor_force_trends_df[2:]

# Assign custom headers to the DataFrame
labor_force_trends_df.columns = custom_headers

# Reset the index for cleaner handling
labor_force_trends_df = labor_force_trends_df.reset_index(drop=True)
labor_force_trends_df = labor_force_trends_df[labor_force_trends_df['group'].notna()]  # Remove rows with NaN in 'group'
labor_force_trends_df = labor_force_trends_df[~labor_force_trends_df['group'].str.startswith('Footnotes', na=False)]
labor_force_trends_df = labor_force_trends_df[~labor_force_trends_df['group'].str.contains('Note|Source', na=False)]
labor_force_trends_df = labor_force_trends_df[~labor_force_trends_df['group'].str.contains('Age of baby-boomers| The "all other groups"', na=False)]

numeric_columns = [
    '1999', '2009', '2019', '2029', 'change_1999_09', 
    'change_2009_19', 'change_2019_29', 'percent_change_1999_09', 
    'percent_change_2009_19', 'percent_change_2019_29',
    'percent_distribution_1999', 'percent_distribution_2009', 
    'percent_distribution_2019', 'percent_distribution_2029',
    'annual_growth_rate_1999_09', 'annual_growth_rate_2009_19', 
    'annual_growth_rate_2019_29'
]
labor_force_trends_df[numeric_columns] = labor_force_trends_df[numeric_columns].apply(pd.to_numeric, errors='coerce')


prefixes = {
    'Total, 16 years and older':'Total',
    'Men, 16 years and older': 'Men',
    'Women, 16 years and older': 'Women'
}

# Create a list of age groups to modify
age_groups = [
    '16 to 24', '16 to 19', '20 to 24', 
    '25 to 54', '25 to 34', '35 to 44', 
    '45 to 54', '55 and older', 
    '55 to 64', '65 to 74', '75 and older'
]

sex_group = ['Men', 'Women']

# Add the prefixes based on their respective sections
current_prefix = None
for index, row in labor_force_trends_df.iterrows():
    group_value = row['group']
    if group_value in prefixes:  # If the row contains a prefix (e.g., "Men, 16 years and older")
        current_prefix = prefixes[group_value]
    elif group_value in age_groups and current_prefix:  # If the row contains an age group
        labor_force_trends_df.at[index, 'group'] = f"{current_prefix} {group_value}"

demographic_groups = {
    'White': 'White',
    'Black': 'Black',
    'All other groups':'All other groups',
    'Hispanic origin':'Hispanic',
    'Other than Hispanic origin': 'Non-Hispanic'
}

# Iterate through the DataFrame and update 'Men' and 'Women' rows
current_demo = None  # To track the current demographic group
for index, row in labor_force_trends_df.iterrows():
    group_value = row['group']
    
    # Check if the row matches or contains a demographic group
    matched_demo = next((prefix for key, prefix in demographic_groups.items() if key in group_value), None)
    if matched_demo:
        current_demo = matched_demo  # Update the current demographic group
    elif group_value.strip() in ['Men', 'Women'] and current_demo:  # If row is "Men" or "Women" under a demographic group
        labor_force_trends_df.at[index, 'group'] = f"{current_demo} {group_value.strip()}"  # Append demographic group to "Men" or "Women"



# Util Functions
def get_job_similarity(user_vector, job_vector):
    uservector = np.array(user_vector)

    similarity = cosine_similarity([uservector],[job_vector])

    return similarity*100



# Dashboard Starts
st.title("LinkedOut Dashboard")
base_tabs = st.tabs(["Industry Insights", "Occupation Insights"])



# INDUSTRY DASHBOARD
with base_tabs[0]:
    st.title("Industry Insights (2023-33)")

    tabs = st.tabs(["Employment Trends", "Top & Bottom Performing Industries", "Labor Force Trends"])


    with tabs[0]:
        # Create Streamlit sidebar multiselect
        st.header("Employment Change by Industry (2023-2033)")

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
        if st.checkbox("Show detailed data", key="industry_detailed_data"):
            change_data = filtered_df[[
                'Industry', 
                '2023 Employment', 
                '2033 Employment', 
                'Prediction Numeric Change', 
                'Prediction Percent Change'
            ]]
            st.dataframe(change_data, hide_index=True)

    with tabs[1]:
        st.subheader("Top and Bottom Performing Industries")

        # Convert 'Prediction Percent Change' to numeric
        industry_df['Prediction Percent Change'] = pd.to_numeric(industry_df['Prediction Percent Change'], errors='coerce')

        # Drop rows with NaN values in 'Prediction Percent Change'
        industry_df = industry_df.dropna(subset=['Prediction Percent Change'])

        # Get top and bottom 10 performers by percentage change
        top_10 = industry_df.nlargest(10, 'Prediction Percent Change')
        bottom_10 = industry_df.nsmallest(10, 'Prediction Percent Change')

        # Debugging: Check if top_10 and bottom_10 are empty
        if top_10.empty and bottom_10.empty:
            st.write("No data available for top and bottom performing industries.")
        else:
            # Create a combined dataframe for visualization
            performance_df = pd.concat([top_10, bottom_10])
            performance_df['Performance'] = ['Top 10' if x in top_10.index else 'Bottom 10' for x in performance_df.index]

            # Sort the DataFrame to have top performing industries first
            performance_df = performance_df.sort_values(by='Prediction Percent Change', ascending=False)

            # Melt the DataFrame for plotting
            melted_performance_df = performance_df.melt(id_vars=['Industry', 'Performance'], 
                                                          value_vars=['Prediction Percent Change'],
                                                          var_name='Metric', 
                                                          value_name='Value')

            # Create horizontal bar chart for top and bottom performing industries
            fig_performance = px.bar(
                melted_performance_df,
                y='Industry',  
                x='Value',     
                color='Performance',
                title='Top 10 and Bottom 10 Industries by Projected Growth Rate (2023-2033)',
                color_discrete_map={'Top 10': '#2ecc71', 'Bottom 10': '#e74c3c'},
                labels={'Value': 'Projected Growth Rate (%)', 'Industry': ''}
            )

            # Update layout
            fig_performance.update_layout(
                barmode='group',
                yaxis_title="Industry",  
                xaxis_title="Projected Growth Rate (%)",  
                legend_title="Performance",
                height=600,
                template="plotly_white"
            )

            # Add percentage labels on the bars
            fig_performance.update_traces(
                texttemplate='%{x:.1f}%',  
                textposition='outside'
            )

            st.plotly_chart(fig_performance, use_container_width=True)

    with tabs[2]:

        age_groups = [
        'Total 16 to 24', 'Total 16 to 19', 'Total 20 to 24', 
        'Total 25 to 54', 'Total 25 to 34', 'Total 35 to 44', 
        'Total 45 to 54', 'Total 55 and older', 
        'Total 55 to 64', 'Total 65 to 74', 'Total 75 and older'
        ]

        df_total = labor_force_trends_df[labor_force_trends_df['group'].isin(age_groups)]

        # Reshape the data for visualization
        df_total_melted = df_total.melt(
            id_vars='group', 
            value_vars=['1999', '2009', '2019', '2029'], 
            var_name='Year', 
            value_name='Labor Force'
        )

        # Plot the trends for "Total" groups
        fig = px.line(
            df_total_melted, 
            x='Year', 
            y='Labor Force', 
            color='group', 
            title='Labor Force Trends by Age Group Over Time (Total Population)',
            labels={'Labor Force': 'Labor Force (in thousands)', 'Year': 'Year', 'group': 'Age Group'},
            color_discrete_sequence=px.colors.qualitative.Bold  

        )

        # st.plotly_chart(fig)



        age_groups = [
        '16 to 24', '16 to 19', '20 to 24', 
        '25 to 54', '25 to 34', '35 to 44', 
        '45 to 54', '55 and older', 
        '55 to 64', '65 to 74', '75 and older'
        ]

        st.subheader('How the labor force is distributed across different age groups.')

        selected_age_group = st.selectbox(
        "Select an Age Group:",
        age_groups,
        )

        # Loop through each age group and create a plot comparing men and women
        men_group = f"Men {selected_age_group}"
        women_group = f"Women {selected_age_group}"
        df_age = labor_force_trends_df[labor_force_trends_df['group'].isin([men_group, women_group])]

        # Reshape the data for visualization
        df_age_melted = df_age.melt(
            id_vars='group', 
            value_vars=['1999', '2009', '2019', '2029'], 
            var_name='Year', 
            value_name='Labor Force'
        )

        # Plot the trends for the current age group
        fig1 = px.line(
            df_age_melted, 
            x='Year', 
            y='Labor Force', 
            color='group', 
            title=f'Labor Force Trends for {selected_age_group} (Men vs Women)',
            labels={'Labor Force': 'Labor Force (in thousands)', 'Year': 'Year', 'group': 'Gender'},
            color_discrete_sequence=px.colors.qualitative.Bold  
        )

        st.plotly_chart(fig1) 
        st.plotly_chart(fig) #Just to reorder interactive plot and plot of total population we are plotting the first fig here.


        demographics = [
            {'group1': 'White Men', 'group2': 'Black Men', 'title': 'Labor Force Trends: White Men vs Black Men'},
            {'group1': 'White Women', 'group2': 'Black Women', 'title': 'Labor Force Trends: White Women vs Black Women'}
        ]

        st.subheader("Labor Force Trends by Race and Gender")

        # User selects two demographics to compare
        all_demographics = ['White', 'White Men', 'White Women','Black', 'Black Men', 'Black Women', 'Hispanic origin', 'Hispanic Men', 'Hispanic Women', 'Other than Hispanic origin', 'All other groups Men', 'All other groups Women']
        group1 = st.selectbox("Select the first demographic:", all_demographics, index=0)
        group2 = st.selectbox("Select the second demographic:", all_demographics, index=3)

        if group1 != group2:
            # Filter data for the selected groups
            df_filtered = labor_force_trends_df[labor_force_trends_df['group'].isin([group1, group2])]

            # Reshape the data for visualization
            df_melted = df_filtered.melt(
                id_vars='group', 
                value_vars=['1999', '2009', '2019', '2029'], 
                var_name='Year', 
                value_name='Labor Force'
            )

            # Plot the trends for the selected groups
            fig2 = px.line(
                df_melted, 
                x='Year', 
                y='Labor Force', 
                color='group', 
                title=f"Labor Force Trends: {group1} vs {group2}",
                labels={'Labor Force': 'Labor Force (in thousands)', 'Year': 'Year', 'group': 'Demographic'},
                color_discrete_sequence=px.colors.qualitative.Bold  
            )

            st.plotly_chart(fig2)
        else:
            st.warning("Please select two different demographics to compare.")







  # moved top and bottom performing occupations to the occupation dashboard 



# OCCUPATION DASHBOARD
with base_tabs[1]:
    # Header
    st.title("💼 Occupation Insights (2023–2033)")
    st.subheader("📊 Interactive Dashboard for Exploring Workforce Trends and Future Projections")
    st.divider()  # Add a horizontal divider for better structure

    # Dropdown for selecting occupation
    selected_occupation = st.selectbox(
        "🔍 Select an Occupation:",
        occupations_df["2023 National Employment Matrix title"].unique().tolist(),
    )

    # Tabs for navigation
    tabs = st.tabs([
        "🏠 Home",
        "🎓 Education Trends",
        "📈 Employment Projections",
        "🛠️ Skill Insights",
        "🏆 Top and Bottom Performers (2023–2033)",
    ])

    # Home Tab
    with tabs[0]:
        # Filter data for the selected occupation
        occupation_data = occupations_df[occupations_df["2023 National Employment Matrix title"] == selected_occupation]

        st.header("📌 Key Metrics")
        st.write("Explore essential insights about the selected occupation below:")
        st.divider()

        # Split metrics into columns
        col1, col2 = st.columns(2)

        formatted_total_employment = f"{occupation_data['Employment, 2023'].values[0]*1000:,}"
        formatted_projected_employment = f"{occupation_data['Employment, 2033'].values[0]*1000:,}"
        formatted_percentage_growth = f"{occupation_data['Employment change, percent, 2023–33'].values[0]}%"
        formatted_average_salary = f"${occupation_data['Median annual wage, dollars, 2023[1]'].values[0]:,.0f}"

        with col1:
            st.metric("👷 Total Employment (2023)", formatted_total_employment)
            st.metric("📊 Projected Employment (2033)", formatted_projected_employment)
        with col2:
            st.metric("📈 Percentage Growth", formatted_percentage_growth)
            st.metric("💰 Average Salary", formatted_average_salary)

        # Add spacing for better layout
        st.divider()
        st.write("Use the tabs above to explore additional trends and data insights.")


    # Education Trends Tab
    with tabs[1]:
        st.header(f"Education Trends for {selected_occupation}")

        education_data_training = pd.read_excel('project_data/2023-33/education.xlsx', sheet_name=4, header = 1)

        # Get education data
        education_data = education_df[education_df['2023 National Employment Matrix code'] == occupation_data['Occupation'].astype(str).values[0]]

        education_levels = education_data.melt(id_vars=['2023 National Employment Matrix title'], value_vars=education_data.columns[1:], 
                                                var_name='Education Level', value_name='Percentage')
        education_level_1 = education_data_training[education_data_training['2023 National Employment Matrix code'] == occupation_data['Occupation'].astype(str).values[0]]

        fig = px.pie(education_levels,
                    names='Education Level', 
                    values='Percentage', 
                    title=f'Education Level Distribution')

        st.plotly_chart(fig)

        st.subheader('Average Work Experience Level: ' + education_level_1['Work experience in a related occupation'].values[0])



    # Employment Projections Tab
    with tabs[2]:
        st.header("Employment Projections")

        st.metric("Percentage Growth 2023-33", f"{occupation_data['Employment change, percent, 2023–33'].values[0]} %")

        # Create dataframe for employment growth
        employment_data = pd.DataFrame({
            "Year": ["2019", "2023", "2033"],
            "Employment": [
                occupation_data["Employment, 2019"].values[0],
                occupation_data["Employment, 2023"].values[0], 
                occupation_data["Employment, 2033"].values[0]
            ]
        })

        # Line chart
        fig = px.line(
            employment_data,
            x="Year",
            y="Employment",
            markers=True,
            title=f"Employment Change for {selected_occupation} (2019-2033)",
            labels={"Employment": "Number of Employees", "Year": "Year"}
        )

        st.plotly_chart(fig)
    
    with tabs[3]:
        user_skills = current_user.drop(columns=['Name', 'Education', 'Added Skills', 'Current Occupation']).values[0]
        skills_selected_data = skills_df[skills_df['2023 National Employment Matrix code'] == occupation_data['Occupation'].astype(str).values[0]]
        skills_selected_data = skills_selected_data.drop(columns=['Occupation', '2023 National Employment Matrix code', 'Education', 'Salary', 'AI Susceptibility Score', 'AI Susceptibility'])
        occupation_skills = skills_selected_data[list(weights.keys())].values[0]

        skill_comparison = pd.DataFrame({
        "Skill": list(weights.keys()),
        "Your Skill Level": user_skills,
        "Required Skill Level": occupation_skills
        })

        sorted_skills = skill_comparison.sort_values(by='Required Skill Level', ascending=False)
        
        top_skills = sorted_skills.head(4)

        st.subheader('Most Required Skills for this Occupation:')
        for i in top_skills['Skill']:
            st.write('• '+i)

        st.subheader("Skill Comparison")
        st.write('You can compare what skills you are good at vs what you can improve on to be proficient in the selected profession.')

        skill_comparison["Difference"] = skill_comparison["Required Skill Level"] - skill_comparison["Your Skill Level"]
        st.subheader("Skills to Improve", divider='orange')
        skills_to_improve = skill_comparison[skill_comparison["Difference"] > 0]
        if not skills_to_improve.empty:
            st.table(skills_to_improve.assign(hack='').set_index('hack'))
        else:
            st.success("You are proficient in all required skills for this occupation!")

        st.subheader("Skills You Are Adequate In", divider='green')
        adequate_skills = skill_comparison[skill_comparison["Difference"] <= 0]
        if not adequate_skills.empty:
            st.table(adequate_skills.assign(hack='').set_index('hack'))
        else:
            st.success(f'According to our formula, this occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.')

        df = skills_by_major_occupations_df.drop(['2023 National Employment Matrix code', 'Employment, 2023', 'Employment, 2033', 'Employment change, numeric, 2023–33', 'Employment change, percent, 2023–33'], axis = 1)

        major_occupations = df['Occupation Category']

        df = df.drop(['Occupation Category'], axis = 1)

        fig = px.imshow(
        df,
        labels=dict(x="Skill", y="Industry"),
        x=df.columns,
        y=major_occupations,
        color_continuous_scale="Blues",
        aspect="auto"
        )

        fig.update_layout(
            title = "Skill Importance Heatmap by Major Occupation Groups",
            xaxis = dict(
                title = "Skills",
                tickangle = 45,
                tickfont = dict(size =10),
            ),
            yaxis = dict(
                title = "Industries",
                tickfont = dict(size=10),
            ),
            height = 800, 
            width = 1200, 
        )
                
        st.plotly_chart(fig)
    with tabs[4]:
        st.header("Top 10 Best and Worst Performing Occupations (2023-2033)")

        # Convert the percent change column to numeric
        occupations_df['Employment change, percent, 2023–33'] = pd.to_numeric(
            occupations_df['Employment change, percent, 2023–33'],
            errors='coerce'
        )

        # Get top and bottom 10 performers by percentage change
        top_10_occupations = occupations_df.nlargest(10, 'Employment change, percent, 2023–33')
        bottom_10_occupations = occupations_df.nsmallest(10, 'Employment change, percent, 2023–33')

        # Create a combined dataframe for visualization
        performance_occupations_df = pd.concat([top_10_occupations, bottom_10_occupations])
        performance_occupations_df['Performance'] = ['Top 10' if x in top_10_occupations.index else 'Bottom 10' for x in performance_occupations_df.index]

        # Create bar chart
        fig_performance_occupations = px.bar(
            performance_occupations_df,
            y='2023 National Employment Matrix title',
            x='Employment change, percent, 2023–33',
            color='Performance',
            orientation='h',
            title='Top 10 and Bottom 10 Occupations by Projected Growth Rate (2023-2033)',
            color_discrete_map={'Top 10': '#2ecc71', 'Bottom 10': '#e74c3c'},
            labels={'Employment change, percent, 2023–33': 'Projected Growth Rate (%)', '2023 National Employment Matrix title': ''}
        )

        # Update layout
        fig_performance_occupations.update_layout(
            height=600,
            showlegend=True,
            xaxis_title="Percentage Change (%)",
            yaxis={'categoryorder': 'total ascending'},
            template="plotly_white"
        )

        # Add percentage labels on the bars
        fig_performance_occupations.update_traces(
            texttemplate='%{x:.1f}%',
            textposition='outside'
        )

        st.plotly_chart(fig_performance_occupations, use_container_width=True)

        # Optionally, add a data table showing the numeric changes
        if st.checkbox("Show detailed data", key="occupation_detailed_data"):
            change_data_occupations = performance_occupations_df[[
                '2023 National Employment Matrix title', 
                'Employment change, percent, 2023–33'
            ]]
            st.dataframe(change_data_occupations, hide_index=True)




