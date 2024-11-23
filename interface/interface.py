import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import home
import job_recommendation
import user_profile
import dashboard

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

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(http://placekitten.com/200/200);
                background-repeat: no-repeat;
                padding-top: 20px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "LinkedOut";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Streamlit app
def main():    

    st.title("LinkedOut")

    tab = st.tabs(["Home", "My Jobs", "My Profile"])


    with tab[0]:
        home.home()

    with tab[1]:
        job_recommendation.job_recommendation()

    with tab[2]:
        user_profile.user_profile()
    


    


# Run the app
if __name__ == "__main__":
    main()
