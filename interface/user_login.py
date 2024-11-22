import streamlit as st
import json
from pathlib import Path
import pandas as pd
from user_profile import User
import user_profile

def load_users():
    """Load users from JSON file."""
    users_file = Path(__file__).parent / 'data' / 'users.json'
    users_file.parent.mkdir(exist_ok=True)


    
    if not users_file.exists():
        # Create default admin user if file doesn't exist
        default_users = {
            "admin": "admin123"
        }
        with open(users_file, 'w') as f:
            json.dump(default_users, f)
    
    with open(users_file, 'r') as f:
        return json.load(f)

def save_users(users):
    """Save users to JSON file."""
    users_file = Path(__file__).parent / 'data' / 'users.json'
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
        
        # Create tabs for login and signup
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        # Login tab
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    users = load_users()
                    users_df = pd.read_excel("project_data\\generated_data\\users.xlsx")
                    if username in users and password == users[username]:
                        st.session_state.logged_in = True
                        st.session_state.user = users_df[users_df['Name'] == username]
                        st.session_state.username = username
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
                signup_submit = st.form_submit_button("Sign Up")

                if signup_submit:
                    users = load_users()
                    users_df = pd.read_excel("project_data\\generated_data\\users.xlsx")

                    if not new_username or not new_password:
                        st.error("Please fill in all fields!")
                    elif new_username in users:
                        st.error("Username already exists! Please choose a different username.")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match!")
                    else:
                        users[new_username] = new_password
                        save_users(users)
                        st.session_state.username = new_username
                        new_user_data = {"Name": new_username}
                        users_df = pd.concat([users_df, pd.DataFrame([new_user_data])], ignore_index=True)
                        users_df.to_excel("project_data\\generated_data\\users.xlsx", index=False)
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
