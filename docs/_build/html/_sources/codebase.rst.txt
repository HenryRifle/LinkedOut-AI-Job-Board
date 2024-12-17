Codebase Documentation
======================

This document provides an overview of the LinkedOut project codebase, including the main modules and their functionality.

Modules
-------

1. **Dashboard.py**
   - **Purpose**: This file contains the main dashboard interface for the LinkedOut application. It handles user interaction, visualizes data, and provides links to different features of the application.

2. **My Career.py**
   - **Purpose**: This is the career page, containing salary prediction, skills difference and AI Susceptibility predictor.


3. **Home.py**
   - **Purpose**: This is the home page. This is where the user can see user recommendations, job recommendations and can also change his skill settings.


Installation
============

To set up the LinkedOut project locally, follow these steps:

1. Install the required dependencies:
   ::
   
    pip install -r requirements.txt

2. Run the project with streamlit:
   ::
   
    streamlit run home.py


Algorithm Documentation
======================

For detailed documentation on the algorithms used in the LinkedOut project (Cosine Similarity and RandomForestRegression), refer to the relevant sections:

- `Cosine Similarity Documentation <cosine_similarity.html>`_
- `RandomForestRegression Documentation <random_forest_regression.html>`_
