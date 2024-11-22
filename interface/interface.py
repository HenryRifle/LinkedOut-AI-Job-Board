import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from user_login import login_user, logout_user

# Check login before showing any content
if not login_user():
    st.stop()


if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()

# Define base directory
BASE_DIR = Path(__file__).parent.parent

class User:

    def __init__(self,name,skills_vector):
        self.name = name
        self.skills_vector = skills_vector



def recommend_jobs(user_vector, jobs_data):
    jobs_skills = jobs_data.drop(['Job Title','Company Name'],axis=1)
    uservector = np.array(user_vector)

    similarities = cosine_similarity([uservector],jobs_skills)

    jobs_data['Match'] = similarities[0]*100
    recommended_occupations = jobs_data[['Job Title','Company Name','Match']].sort_values(by='Match', ascending=False)

    return recommended_occupations[:10]

user_data = []

# Streamlit app
def main():

    st.title("LinkedOut")
    st.subheader("Not your average linkedin")

    st.write("Please fill out the following details:")


    # Input fields
    name = st.text_input("Enter your name", placeholder="John Doe")
    st.write("Rate yourself on the following skills:")

    # Updated path using pathlib
    jobs_data = pd.read_csv(BASE_DIR / 'generated_data' / 'jobs.csv')


    # Skill sliders
    education = st.slider("Education", 0.0, 5.0, 2.5,0.5)
    adaptability = st.slider("Adaptability", 0.0, 5.0, 2.5,0.5)
    computer_ability = st.slider("Computers and information technology", 0.0, 5.0,2.5, 0.5)
    creativity = st.slider("Creativity", 0.0, 5.0, 2.5,0.5)
    critical_thinking = st.slider("Critical and Analytical Thinking", 0.0, 5.0, 2.5,0.5)
    customer_service = st.slider("Customer Service", 0.0, 5.0, 2.5,0.5)
    detail_oriented = st.slider("Detail Oriented", 0.0, 5.0, 2.5,0.5)
    fine_motor = st.slider("Fine Motor Skills", 0.0, 5.0, 2.5,0.5)
    interpersonal = st.slider("Interpersonal Relations", 0.0, 5.0, 2.5,0.5)
    leadership = st.slider("Leadership", 0.0, 5.0, 2.5,0.5)
    mathematics = st.slider("Mathematics", 0.0, 5.0, 2.5,0.5)
    mechanical = st.slider("Mechanical", 0.0, 5.0, 2.5,0.5)
    physical_strength = st.slider("Physical Strength and Stamina", 0.0, 5.0, 2.5,0.5)
    problem_solving = st.slider("Problem Solving and Decision Making", 0.0, 5.0, 2.5,0.5)
    project_management = st.slider("Project Management", 0.0, 5.0, 2.5,0.5)
    science = st.slider("Scientific Skills", 0.0, 5.0, 2.5,0.5)
    speaking = st.slider("Speaking and Listening", 0.0, 5.0, 2.5,0.5)
    writing = st.slider("Writing and Reading", 0.0, 5.0, 2.5,0.5)

    # Submit button
    if st.button("Submit"):
        if name.strip():

            new_user = User(name= name, skills_vector= [education, adaptability,computer_ability,creativity,critical_thinking,customer_service,detail_oriented,fine_motor,interpersonal,leadership,mathematics,mechanical,physical_strength,problem_solving,project_management,science,speaking,writing])

            # Save user object to backend
            # user_data.append(user)

            recommendations = recommend_jobs(new_user.skills_vector, jobs_data)

            st.write(f"Here are your recommended jobs, {name}.")

            st.table(recommendations)
        else:
            st.error("Name cannot be empty. Please provide your name.")

# Run the app
if __name__ == "__main__":
    main()
