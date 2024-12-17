import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
from user_login import login_user, logout_user
# from scipy.stats import percentileofscore
# from sklearn.metrics.pairwise import cosine_similarity


st.set_page_config(layout="wide")


if not login_user():
    st.stop()


if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()



@st.cache_resource
def load_salary_model():
    return joblib.load('models/rf_salary_model.pkl')


rf_model = load_salary_model()


def predict_salary(skills):
    skills_array = np.array([skills])
    predicted_salary = rf_model.predict(skills_array)[0]
    return predicted_salary



user_df = pd.read_excel('project_data/generated_data/users.xlsx')
occupations_df_23 = pd.read_excel('project_data/2023-33/occupation.xlsx', sheet_name = 2, header = 1)
occupations_df_19 = pd.read_excel('project_data/2019-29/occupation.xlsx', sheet_name = 2, header = 1)
occupations_df_23 = occupations_df_23[occupations_df_23['Occupation type'] != 'Summary']
occupations_df_19 = occupations_df_19[occupations_df_19['Occupation type'] != 'Summary']
occupations_df_23 = occupations_df_23.rename(columns={"2023 National Employment Matrix code" : "Occupation"})
occupations_df_19 = occupations_df_19.rename(columns={"2019 National Employment Matrix code" : "Occupation"})
occupations_df = pd.merge(occupations_df_23,occupations_df_19, on='Occupation', how='left')

skills_df = pd.read_excel('project_data/2023-33/skills.xlsx', sheet_name=2, header = 1)
skills_df = skills_df.drop(columns = ['Employment, 2023','Employment, 2033','Employment change, numeric, 2023–33','Employment change, percent, 2023–33'])
skills_df = skills_df.rename(columns = {"2023 National Employment Matrix title" : "Occupation","Typical education needed for entry" : "Education","Median annual wage, dollars, 2023[1]" : "Salary"})
skills_df['Education'] = skills_df['Education'].map({'-' : 0, 'No formal educational credential' : 0,'High school diploma or equivalent' : 1, 'Some college, no degree' : 1, 'Postsecondary nondegree award' : 1,'Associate\'s degree' : 2, 'Bachelor\'s degree' : 3, 'Master\'s degree' : 4, 'Doctoral or professional degree' : 5})
skills_df['Occupation'] = skills_df['Occupation'].str.replace(r'\[\d+\]', '', regex=True).str.strip()

skills_by_major_occupations_df = pd.read_excel('project_data/2023-33/skills.xlsx', sheet_name=1, header = 1)

skills_by_major_occupations_df = skills_by_major_occupations_df.rename(columns = {"2023 National Employment Matrix title" : "Occupation Category"})
skills_by_major_occupations_df = skills_by_major_occupations_df[skills_by_major_occupations_df["Occupation Category"] != "Total, all occupations"]
skills_by_major_occupations_df = skills_by_major_occupations_df[~skills_by_major_occupations_df.iloc[:, 0].str.contains("Footnotes|Note|Source", na=False)]

skills_by_major_occupations_df = skills_by_major_occupations_df.reset_index(drop=True)


#Weights defining AI susceptibility for each skill
weights = {
    "Adaptability": 0.08,
    "Computers and information technology": 0.06,
    "Creativity and innovation": 0.09,
    "Critical and analytical thinking": 0.08,
    "Customer service": 0.06,
    "Detail oriented": 0.05,
    "Fine motor": 0.03,
    "Interpersonal": 0.08,
    "Leadership": 0.08,
    "Mathematics": 0.08,
    "Mechanical": 0.03,
    "Physical strength and stamina": 0.05,
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

current_user = user_df[user_df['Name'] == st.session_state.current_user]


current_user_skills = current_user.drop(['Name', 'Added Skills', 'Current Occupation'], axis = 1)

# This is a weird way to filter out the occupation from skills dataset but just comparing the current occupation string to the Occupation column in skills_df is not working for some reason!
user_current_occupation = current_user['Current Occupation'].values[0]
user_occ_data = occupations_df[occupations_df["2023 National Employment Matrix title"] == user_current_occupation]
user_occupation_skills = skills_df[skills_df['2023 National Employment Matrix code'] == user_occ_data['Occupation'].astype(str).values[0]]

user_occupation_skills_filtered = user_occupation_skills.drop(['Occupation', '2023 National Employment Matrix code', 'Salary', 'AI Susceptibility', 'AI Susceptibility Score'], axis = 1)
# sim = cosine_similarity(current_user_skills, user_occupation_skills_filtered)[0]

# user_percentile = percentileofscore(sim, sim[0], kind = "rank")

# st.write(user_percentile)


national_df_23 = pd.read_excel('project_data/oesm23nat/national_M2023_dl.xlsx')

national_useroccupation_df = national_df_23[national_df_23['OCC_CODE'] == user_occupation_skills['2023 National Employment Matrix code'].values[0]]

def compute_wage_percentile(wage):
    if wage >= national_useroccupation_df['A_PCT90'].values[0]:
        return '90th Percentile'
    elif wage >= national_useroccupation_df['A_PCT75'].values[0]:
        return '75th Percentile'
    elif wage >= national_useroccupation_df['A_MEDIAN'].values[0]:
        return '50th Percentile'
    elif wage >= national_useroccupation_df['A_PCT25'].values[0]:
        return '25th Percentile'
    else:
        return '10th Percentile'


def show_career_page():

    st.title("💼 My Career")

    
    st.header(f"Hello, {st.session_state.current_user}.")
    st.header("📊 Here are your Career Insights")

    st.subheader(f"💰 Based on your skills, your predicted salary is: ${predicted_salary:,.0f}")

    st.subheader(f'For your occupation, the average annual salary is ${national_useroccupation_df["A_MEDIAN"].values[0]:,.0f}')
    user_wage_percentile = compute_wage_percentile(predicted_salary)

    st.subheader('Your predicted salary falls in the ' + user_wage_percentile + ' of all '+ user_current_occupation + '.')

    national_df_melted = national_useroccupation_df.melt(
    id_vars=["OCC_TITLE"],
    value_vars=["A_PCT25", "A_MEDIAN", "A_PCT75", "A_PCT90"],
    var_name="Percentile",
    value_name="Salary"
    )
    national_df_melted["Percentile"] = national_df_melted["Percentile"].replace(
        {"A_PCT25": "25th Percentile", "A_MEDIAN": "Median (50th)", "A_PCT75": "75th Percentile", "A_PCT90": "90th Percentile"}
    )

    salary_fig = px.bar(
    national_df_melted,
    x="Percentile",
    y="Salary",
    color="Percentile",
    title="Annual Salary Distribution by Percentile",
    labels={"OCC_TITLE": "Occupation Title", "Salary": "Annual Salary (USD)", "Percentile": "Percentile"},
    text= "Salary"
    )

    salary_fig.update_layout(
        yaxis_title="Annual Salary (USD)",
        legend_title="Percentile",
    )

    st.plotly_chart(salary_fig)




    occupation_data = occupations_df[occupations_df["2023 National Employment Matrix title"] == user_current_occupation]

    skills_selected_data = skills_df[skills_df['2023 National Employment Matrix code'] == occupation_data['Occupation'].astype(str).values[0]]
    st.subheader("🤖 AI Susceptibility: " + skills_selected_data["AI Susceptibility"].values[0])

    if skills_selected_data["AI Susceptibility"].values[0] == "High":
        st.write(f'#### This occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.')
    elif skills_selected_data["AI Susceptibility"].values[0] == "Medium":
        st.write(f'#### This occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.')
    else:
        st.write(f'#### This occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.')

    df1 = pd.DataFrame(list(weights.items()), columns=["Skill", "Susceptibility"])

    # Sort by susceptibility (low to high)
    df_sorted = df1.sort_values(by="Susceptibility", ascending=True)

    most_prone = df_sorted.head(3)
    most_resistant = df_sorted.tail(3)

    st.write("### Most AI-Prone Skills:")
    for i in most_prone['Skill']:
        st.write(i)

    st.write("### Most AI-Resistant Skills:")
    for i in most_resistant['Skill']:
        st.write(i)





    

    user_skills = current_user.drop(columns=['Name', 'Education', 'Added Skills','Current Occupation']).values[0]

    skills_selected_data = skills_selected_data.drop(columns=['Occupation', '2023 National Employment Matrix code', 'Education', 'Salary', 'AI Susceptibility Score', 'AI Susceptibility'])
    occupation_skills = skills_selected_data[list(weights.keys())].values[0]

    

    skill_comparison = pd.DataFrame({
        "Skill": list(weights.keys()),
        "Your Skill Level": user_skills,
        "Required Skill Level": occupation_skills
    })

    sorted_skills = skill_comparison.sort_values(by='Required Skill Level', ascending=False)
    
    top_skills = sorted_skills.head(4)

    st.subheader('💡Most Required Skills for this Occupation:')
    for i in top_skills['Skill']:
        st.write('• '+i)

    
    st.header("🛠️ Skill Comparison")
    st.write('Here is a comparison of your skills vs the average skill level required for this profession.')
    st.write('You can see what you are good at, and which areas you can improve on right here.')


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
    user_occupation_skills_filtered,
    labels=dict(x="Skill", y="Industry"),
    x=user_occupation_skills_filtered.columns,
    y=[user_current_occupation],
    color_continuous_scale="Blues",
    aspect="auto"
    )

    fig.update_layout(
        title = "Skill Importance Heatmap for " + user_current_occupation.strip() + ".",
        xaxis = dict(
            title = "Skills",
            tickangle = 45,
            tickfont = dict(size =10),
        ),
        yaxis = dict(
            title = "Industries",
            tickfont = dict(size=10),
        ),
        height = 500, 
        width = 1200, 
    )
            
    st.plotly_chart(fig)


null_skills = current_user_skills.isna().any()

if null_skills.any():
    st.warning("Please go to user profile and update all the skills first.")
else:
    skills_list = current_user_skills.iloc[0].tolist()
    predicted_salary = predict_salary(skills_list)
    show_career_page()

