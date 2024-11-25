import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# class User:
#     def __init__(self,name,skills_vector):
#         self.name = name
#         self.skills_vector = skills_vector

#File Path to jobs.csv for global use 
jobs_filepath = Path("project_data") / "generated_data" / "jobs.csv" #Gaurangi

#DEBUGGIGN STATEMENTS 
print("##########################################################################################################################################################################")
print("                                                    SHHHHHHHH - GAURANGI IS DEBUGGING                                                                                     ")

print("Jobs Filepath:", jobs_filepath)
print("Jobs Filepath as String:", str(jobs_filepath))

print("Does jobs_filepath exist?", jobs_filepath.exists())

jobs_data = pd.read_csv(jobs_filepath)

# Check the DataFrame
print("Jobs Data Shape:", jobs_data.shape)

import os
print("Current Working Directory:", os.getcwd())

print("                                                    SHHHHHHHH - GAURANGI IS DEBUGGING                                                                                     ")
print("##########################################################################################################################################################################")


##########

#File Path to users.xlsx for global use 
users_filepath = Path("project_data") / "generated_data" / "users.xlsx" #Gaurangi

def recommend_jobs(user_vector, jobs_data):
    jobs_skills = jobs_data.drop(['Job Title','Company Name'],axis=1)
    uservector = np.array(user_vector)

    print("##########################################################################################################################################################################")
    print("                                                    SHHHHHHHH - GAURANGI IS DEBUGGING                                                                                     ")

    print("User Vector Shape :", user_vector.shape)
    print("Jobs Data Shape :", jobs_data.shape)

    print("                                                    SHHHHHHHH - GAURANGI IS DEBUGGING                                                                                     ")
    print("##########################################################################################################################################################################")

    similarities = cosine_similarity([uservector],jobs_skills)

    jobs_data['Match'] = similarities[0]*100
    recommended_occupations = jobs_data[['Job Title','Company Name','Match']].sort_values(by='Match', ascending=False)

    return recommended_occupations[:10]


def job_recommendation():

    jobs_data = pd.read_csv(jobs_filepath) ##Gaurangi - 
    #DEBUGGIGN STATEMENTS 
    print("##########################################################################################################################################################################")
    print("                                                    SHHHHHHHH - GAURANGI IS DEBUGGING                                                                                     ")

    print(jobs_data.head(10)) # prints the jobs data - shows that jobs_data is populated correctly
    print("##########################################################################################################################################################################")


    users_df = pd.read_excel(users_filepath)

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


