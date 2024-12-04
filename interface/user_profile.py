import streamlit as st
import pandas as pd

class User:
    def __init__(self,name,skills_vector):
        self.name = name
        self.skills_vector = skills_vector
        self.initial_update = False


def user_profile():
    # Input fields
    name = st.session_state.current_user
    
    st.title(f"Rate yourself on the following skills, {name}")

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

    user_ratings = {
        "Education": education,
        "Adaptability": adaptability,
        "Computers and information technology": computer_ability,
        "Creativity": creativity,
        "Critical and Analytical Thinking": critical_thinking,
        "Customer Service": customer_service,
        "Detail Oriented": detail_oriented,
        "Fine Motor Skills": fine_motor,
        "Interpersonal Relations": interpersonal,
        "Leadership": leadership,
        "Mathematics": mathematics,
        "Mechanical": mechanical,
        "Physical Strength and Stamina": physical_strength,
        "Problem Solving and Decision Making": problem_solving,
        "Project Management": project_management,
        "Scientific Skills": science,
        "Speaking and Listening": speaking,
        "Writing and Reading": writing
    }

    users_df = pd.read_excel("project_data\\generated_data\\users.xlsx")

    if st.button("Submit"):
        # new_user_data.update(user_ratings)
        for key, value in user_ratings.items():
            users_df.loc[users_df['Name'] == name, key] = value
        # users_df = pd.concat([users_df, pd.DataFrame([new_user_data])], ignore_index=True)
        st.success("Updated your information successfully!")
        users_df.to_excel('project_data\\generated_data\\users.xlsx', index=False)



