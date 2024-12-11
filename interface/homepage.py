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

artificial_users_df = pd.read_csv('project_data/generated_data/users_artificial.csv')

skill_columns = artificial_users_df.drop(columns=['Name', 'Unnamed: 0', 'Current Occupation'], errors='ignore')

user_similarities = cosine_similarity(skill_columns)

artificial_users_df['Match (%)'] = user_similarities[0]*100
recommended_users = artificial_users_df[['Name','Current Occupation','Match (%)']].sort_values(by='Match (%)', ascending=False)

recommended_users = recommended_users[recommended_users['Name'] != st.session_state.current_user]

def home():
    name = st.session_state.current_user
    st.title(f"Welcome to LinkedOut, {name} !")

    st.subheader("Recommended for you : ")

    st.table(recommended_users[:5].assign(hack='').set_index('hack'))
