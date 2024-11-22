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





def user_profile():
    # Input fields
    name = st.session_state.username

    st.title(f"Rate yourself on the following skills, {name}")

    skills = [
        "Education", "Adaptability", "Computers and information technology", "Creativity",
        "Critical and Analytical Thinking", "Customer Service", "Detail Oriented",
        "Fine Motor Skills", "Interpersonal Relations", "Leadership", "Mathematics",
        "Mechanical", "Physical Strength and Stamina", "Problem Solving and Decision Making",
        "Project Management", "Scientific Skills", "Speaking and Listening",
        "Writing and Reading"
    ]

    user_ratings = {}

    # Create sliders with Beginner and Advanced labels below
    for skill in skills:
        st.write(f"### {skill}")
        
        # Slider
        user_ratings[skill] = st.slider("", 0.0, 5.0, 2.5, 0.5, key=skill)  # Slider widget

        # Labels below the slider using HTML
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between;">
                <span>Beginner</span>
                <span>Advanced</span>
            </div>
            """,
            unsafe_allow_html=True,
        )



    users_df = pd.read_excel("project_data\\generated_data\\users.xlsx")

    if st.button("Submit"):
        
        for key, value in user_ratings.items():
            users_df.loc[users_df['Name'] == name, key] = value
        st.success("Updated your information successfully!")
        
        
        users_df.to_excel('project_data\\generated_data\\users.xlsx', index=False)



if 'username' not in st.session_state:
    st.session_state.username = "Test User" 
user_profile()

