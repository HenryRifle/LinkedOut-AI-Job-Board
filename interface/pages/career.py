import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px

@st.cache_resource
def load_salary_model():
    return joblib.load('models\\rf_salary_model.pkl')


rf_model = load_salary_model()


def predict_salary(skills):
    skills_array = np.array([skills])
    predicted_salary = rf_model.predict(skills_array)[0]
    return predicted_salary


user_df = pd.read_excel('project_data\\generated_data\\users.xlsx')
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

skills_by_major_occupations_df = pd.read_excel('project_data\\2023-33\\skills.xlsx', sheet_name=1, header = 1)

skills_by_major_occupations_df = skills_by_major_occupations_df.rename(columns = {"2023 National Employment Matrix title" : "Occupation Category"})
skills_by_major_occupations_df = skills_by_major_occupations_df[skills_by_major_occupations_df["Occupation Category"] != "Total, all occupations"]
skills_by_major_occupations_df = skills_by_major_occupations_df[~skills_by_major_occupations_df.iloc[:, 0].str.contains("Footnotes|Note|Source", na=False)]

skills_by_major_occupations_df = skills_by_major_occupations_df.reset_index(drop=True)


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


current_user = user_df[user_df['Name'] == st.session_state.current_user]

current_user_skills = current_user.drop(['Name', 'Added Skills'], axis = 1)
skills_list = current_user_skills.iloc[0].tolist()

predicted_salary = predict_salary(skills_list)

st.title("My Career")

st.header(f"Hello, {st.session_state.current_user}. Here are some of your career insights.")
st.subheader(f"Your predicted salary is: ${predicted_salary:,.0f}")
st.warning("This figure is calculated based on the skills rating given in your profile.")

selected_occupation = st.selectbox("Select an Occupation:", occupations_df["2023 National Employment Matrix title"].unique().tolist())
occupation_data = occupations_df[occupations_df["2023 National Employment Matrix title"] == selected_occupation]

st.header("Occupation Insights")
skills_selected_data = skills_df[skills_df['2023 National Employment Matrix code'] == occupation_data['Occupation'].astype(str).values[0]]
st.subheader("AI Susceptibility: " + skills_selected_data["AI Susceptibility"].values[0])

if skills_selected_data["AI Susceptibility"].values[0] == "High":
    st.error(f'According to our formula, this occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.')
elif skills_selected_data["AI Susceptibility"].values[0] == "Medium":
    st.warning(f'According to our formula, this occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.')
else:
    st.success(f'According to our formula, this occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.')

st.subheader("Skill Comparison")

user_skills = user_df.drop(columns=['Name', 'Education', 'Added Skills']).values[0]

skills_selected_data = skills_selected_data.drop(columns=['Occupation', '2023 National Employment Matrix code', 'Education', 'Salary', 'AI Susceptibility Score', 'AI Susceptibility'])
occupation_skills = skills_selected_data[list(weights.keys())].values[0]

skill_comparison = pd.DataFrame({
    "Skill": list(weights.keys()),
    "User Skill Level": user_skills,
    "Required Skill Level": occupation_skills
})

skill_comparison["Difference"] = skill_comparison["Required Skill Level"] - skill_comparison["User Skill Level"]
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
    st.success(f"According to our formula, this occupation has a {skills_selected_data["AI Susceptibility"].values[0].lower()} susceptibility to Artificial Intelligence. Usually, occupations which use skills that can be easily replicated by AI are more susceptible to be automated.")




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

