import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from user_login import login_user, logout_user

# Check login before showing any content
if not login_user():
    st.stop()

if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()


def home():
    name = st.session_state.current_user
    artificial_users_df = pd.read_csv('project_data/generated_data/users_artificial.csv')

    skill_columns = artificial_users_df.drop(columns=['Name', 'Unnamed: 0', 'Current Occupation'], errors='ignore')
    users_df = pd.read_excel("project_data/generated_data/users.xlsx")

    current_user = st.session_state.current_user
    skill_columns_names = ['Education','Adaptability','Computers and information technology','Creativity','Critical and Analytical Thinking','Customer Service','Detail Oriented','Fine Motor Skills','Interpersonal Relations','Leadership','Mathematics','Mechanical','Physical Strength and Stamina','Problem Solving and Decision Making','Project Management','Scientific Skills','Speaking and Listening','Writing and Reading']
    user_skills = users_df.loc[users_df['Name'] == current_user, skill_columns_names]
    user_skills_vector = user_skills.values.flatten()
    null_skills = user_skills.isna().any()

    st.title(f"Welcome to LinkedOut, {name} !")

    if null_skills.any(): 
        st.warning("Please go to user profile and update all the skills first.")
    else:
        st.subheader("Recommended for you : ")
        user_similarities = cosine_similarity(skill_columns, [user_skills_vector])
        artificial_users_df['Match (%)'] = user_similarities*100
        recommended_users = artificial_users_df[['Name','Current Occupation','Match (%)']].sort_values(by='Match (%)', ascending=False)
        recommended_users = recommended_users[recommended_users['Name'] != st.session_state.current_user]

        st.table(recommended_users[:5].assign(hack='').set_index('hack'))
