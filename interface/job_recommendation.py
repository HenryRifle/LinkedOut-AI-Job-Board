import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# class User:
#     def __init__(self,name,skills_vector):
#         self.name = name
#         self.skills_vector = skills_vector



def recommend_jobs(user_vector, jobs_data):
    jobs_skills = jobs_data.drop(['Job Title','Company Name'],axis=1)
    uservector = np.array(user_vector)

    similarities = cosine_similarity([uservector],jobs_skills)

    jobs_data['Match'] = similarities[0]*100
    recommended_occupations = jobs_data[['Job Title','Company Name','Match']].sort_values(by='Match', ascending=False)

    return recommended_occupations[:10]


def job_recommendation():

    jobs_data = pd.read_csv('D:\\Big-Data-Project\\generated_data\\jobs.csv')


    users_df = pd.read_excel("D:\\Big-Data-Project\\generated_data\\users.xlsx")

    user_name = st.session_state.username
    user_data = users_df[users_df['Name'] == user_name]

    skill_columns = ['Education','Adaptability','Computers and information technology','Creativity','Critical and Analytical Thinking','Customer Service','Detail Oriented','Fine Motor Skills','Interpersonal Relations','Leadership','Mathematics','Mechanical','Physical Strength and Stamina','Problem Solving and Decision Making','Project Management','Scientific Skills','Speaking and Listening','Writing and Reading']
    user_skills = users_df.loc[users_df['Name'] == user_name, skill_columns]
    user_skills_vector = user_skills.values.flatten()
    null_skills = user_skills.isna().any()


    if null_skills.any():
        st.warning("Please go to user profile and update skills first!")
    else:
        recommendations = recommend_jobs(user_skills_vector, jobs_data)

        st.title(f"Here are your recommended jobs, {user_name}.")

        st.table(recommendations)


