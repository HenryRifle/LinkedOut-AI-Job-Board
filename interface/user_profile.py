import streamlit as st
import pandas as pd

#class User:
#
 #   def __init__(self,name,skills_vector):
 #       self.name = name
 #       self.skills_vector = skills_vector
 #       self.initial_update = False

def user_profile():
    name = st.session_state.current_user

    st.title(f"Rate yourself on the following skills, {name}")

    skills = [
        "Education", "Adaptability", "Computers and information technology", "Creativity",
        "Critical and Analytical Thinking", "Customer Service", "Detail Oriented",
        "Fine Motor Skills", "Interpersonal Relations", "Leadership", "Mathematics",
        "Mechanical", "Physical Strength and Stamina", "Problem Solving and Decision Making",
        "Project Management", "Scientific Skills", "Speaking and Listening",
        "Writing and Reading"
    ]

    slider_options = {
        "0 - No Experience": 0,
        "1 - Basic Awareness": 1,
        "2 - Foundational Knowledge": 2,
        "3 - Intermediate Proficiency": 3,
        "4 - Advanced Proficiency": 4,
        "5 - Expert": 5
    }

    user_ratings = {}

    # Create sliders with Beginner and Advanced labels below
    for skill in skills:
        st.write(f"### {skill}")

        # Slider
        selected_option = st.select_slider(
            label=skill,
            options=list(slider_options.keys()),
            key=f"slider_{skill}"

        )

        # Converting the option to its mapped numerical value so we can store them in the excel
        user_ratings[skill] = slider_options[selected_option]

    users_df = pd.read_excel('project_data/generated_data/users.xlsx')

    if st.button("Submit"):
        for key, value in user_ratings.items():
            users_df.loc[users_df['Name'] == name, key] = value
        st.success("Updated your information successfully!")
        
        users_df.to_excel('project_data/generated_data/users.xlsx', index=False)


if 'username' not in st.session_state:
    st.session_state.username = "Test User" 

