import streamlit as st
import json
from pathlib import Path
import uuid
import pandas as pd

#Importing the datasets
occupations_df_23 = pd.read_excel('project_data/2023-33/occupation.xlsx', sheet_name = 2, header = 1)
occupations_df_19 = pd.read_excel('project_data/2019-29/occupation.xlsx', sheet_name = 2, header = 1)
occupations_df_23 = occupations_df_23[occupations_df_23['Occupation type'] != 'Summary']
occupations_df_19 = occupations_df_19[occupations_df_19['Occupation type'] != 'Summary']
occupations_df_23 = occupations_df_23.rename(columns={"2023 National Employment Matrix code" : "Occupation"})
occupations_df_19 = occupations_df_19.rename(columns={"2019 National Employment Matrix code" : "Occupation"})
occupations_df = pd.merge(occupations_df_23,occupations_df_19, on='Occupation', how='left')

def load_users():
    """Load users from JSON file."""
    users_file = Path(__file__).parent / 'user_data' / 'users.json'
    users_file.parent.mkdir(exist_ok=True)
    
    default_users = {
        "admin": {
            "password": "admin123",
            "userID": str(uuid.uuid4())
        }
    }
    
    if not users_file.exists():
        with open(users_file, 'w') as f:
            json.dump(default_users, f)
        return default_users
    
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
            if not isinstance(users, dict):
                return default_users
            return users
    except (json.JSONDecodeError, IOError) as e:
        # Log the error for debugging
        print(f"Error loading users: {e}")
        return default_users

def save_users(users):
    """Save users to JSON file."""
    users_file = Path(__file__).parent / 'user_data' / 'users.json'
    with open(users_file, 'w') as f:
        json.dump(users, f)
    

def login_user():
    """Handle the login process and signup."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("Welcome to LinkedOut")
        st.subheader("Not your average linkedin")
        st.write("Please login or signup to continue")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        # Login tab
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    users = load_users()
                    # Check if users were loaded correctly
                    if users is None or not isinstance(users, dict):
                        st.error("Error loading user data.")
                        return

                    # Safer login check
                    if (username in users and 
                        isinstance(users[username], dict) and 
                        'password' in users[username] and 
                        users[username]['password'] == password):
                        
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.session_state.user_id = users[username].get('userID', str(uuid.uuid4()))
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

        # Sign up tab
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                selected_occupation = st.selectbox("Select an Occupation:", occupations_df["2023 National Employment Matrix title"].unique().tolist(), index=None, placeholder="Choose your current occupation")
                signup_submit = st.form_submit_button("Sign Up")
                
                if signup_submit:
                    users = load_users()
                    

                    # Validate input
                    if not new_username or not new_password:
                        st.error("Please fill in all fields!")
                    elif new_username in users:
                        st.error("Username already exists! Please choose a different username.")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match!")
                    elif any(user.get('password') == new_password for user in users.values()):
                        st.error("This password is already in use! Please choose a different password.")
                    elif not selected_occupation:
                        st.error("Please select an occupation!")
                    else:
                        # Create new user
                        users[new_username] = {
                            "password": new_password,
                            "userID": str(uuid.uuid4()),
                            "occupation": selected_occupation.strip()
                        }
                        new_user_data = {"Name": new_username, "Current Occupation": selected_occupation}
                        users_df = pd.read_excel('project_data/generated_data/users.xlsx')
                        users_df = pd.concat([users_df, pd.DataFrame([new_user_data])], ignore_index=False)
                        users_df.to_excel('project_data/generated_data/users.xlsx')
                        save_users(users)
                        st.success("Account created successfully! Please go to the Login tab to sign in.")

    return st.session_state.logged_in

def logout_user():
    """Log out the user."""
    st.session_state.logged_in = False

# Add this to the main section of your Streamlit pages
if __name__ == "__main__":
    if login_user():
        if st.sidebar.button("Logout", key="main_logout_button"):
            logout_user()
            st.rerun()
        # Your main app content goes here
        st.write("Main app content")
