import streamlit as st
import joblib
from pathlib import Path

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from user_login import login_user, logout_user

# Check login before showing any content
if not login_user():
    st.stop()

# Modified logout button
if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()



# Define base directory
BASE_DIR = Path(__file__).parent.parent.parent

@st.cache_resource
def load_salary_model():
    return joblib.load(BASE_DIR / 'models' / 'rf_salary_model.pkl')

rf_model = load_salary_model()


def predict_salary(skills):
    skills_array = np.array([skills])
    predicted_salary = rf_model.predict(skills_array)[0]
    return predicted_salary



class User:

    def __init__(self,name,skills_vector):
        self.name = name
        self.skills_vector = skills_vector





def main():
    st.title("Salary Prediction based on skills")
    st.subheader("Rate yourself on the following skills:")

    name = st.text_input("Enter your name", placeholder="John Doe")
    st.write("Rate yourself on the following skills:")


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



    if st.button("Predict Salary"):

        if name.strip():
            new_user = User(name= name, skills_vector= [education, adaptability,computer_ability,creativity,critical_thinking,customer_service,detail_oriented,fine_motor,interpersonal,leadership,mathematics,mechanical,physical_strength,problem_solving,project_management,science,speaking,writing])

        # Predict salary
        predicted_salary = predict_salary(new_user.skills_vector)

        st.write(f"Based on your skills, your predicted salary is:\n\n ${predicted_salary:,.2f}")

# Run the app
if __name__ == "__main__":
    main()

