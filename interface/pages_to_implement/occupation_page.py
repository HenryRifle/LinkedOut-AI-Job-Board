import pandas as pd
import numpy as np
import openpyxl
import pandas as pd
import streamlit as st
import plotly.express as px
import os

# path = 'D:\Big-Data-Project\project_data'
filename_29 = '../project_data/2019-29/occupation.xlsx'
filename_33 = '../project_data/2023-33/occupation.xlsx'

occu_obj_29 = openpyxl.load_workbook(filename_29)
occu_obj_33 = openpyxl.load_workbook(filename_33)

index_sheet_23 = pd.read_excel(filename_29)
index_sheet_33 = pd.read_excel(filename_29)

sheet_data_23 = {}
sheet_data_33 = {}

def basic_data_cleaning(data1):

    data1 = data1.rename(columns={data1.columns[0]: "Occupation Title"})
    
    try:
        index = data1[data1['Occupation Title'].str.contains('Footnotes')].index[0]
    except:
        index = data1[data1['Occupation Title'].str.contains('U.S. Bureau of Labor Statistics')].index[0]
        
    data1 = data1.iloc[:index]

    # try:
    #     data1 = data1.drop('2019 National Employment Matrix code', axis=1)
    # except:
    #     pass
    
    return data1

for i in index_sheet_23.index:
    data = pd.read_excel(filename_29, sheet_name=i+1, skiprows=1)
    
    print(index_sheet_23.loc[i].iloc[0])
    
    sheet_data_23[index_sheet_23.loc[i].iloc[0]] = basic_data_cleaning(data)

for i in index_sheet_33.index:
    data = pd.read_excel(filename_33, sheet_name=i+1, skiprows=1)
    
    print(index_sheet_33.loc[i].iloc[0])
    
    sheet_data_23[index_sheet_33.loc[i].iloc[0]] = basic_data_cleaning(data)


df = pd.DataFrame(sheet_data[index_sheet.loc[3].iloc[0]])

df = df[df['Job Title'] != 'Total, all occupations']

df = df[['Job Title', 'Employment, 2019', 'Employment, 2029', 'Employment change, numeric, 2019-29']]

st.title("Projected Employment Growth: 2019 vs. 2029")

#Filtering top 5 jobs by Employment change numeric
top_5_jobs = df.nlargest(5, 'Employment change, numeric, 2019-29')

default_jobs = top_5_jobs['Job Title'].tolist()

df = df.drop(columns=['Employment change, numeric, 2019-29'])

selected_jobs = st.multiselect(
    "Select Job Titles to Display:",
    options=df['Job Title'].unique(),
    default=default_jobs
)

filtered_df = df[df['Job Title'].isin(selected_jobs)]

melted_df = filtered_df.melt(id_vars=['Job Title'], var_name='Year', value_name='Employment')

fig = px.bar(
    melted_df,
    x='Job Title',
    y='Employment',
    color='Year',
    title='Employment in 2019 vs. 2029 (Most Job Growth)',
    labels={'Employment': 'Employment (Thousands)', 'Job Title': 'Occupation'}
)

fig.update_layout(
    barmode='group',
    xaxis_title="Job Title",
    yaxis_title="Employment (Thousands)",
    legend_title="Year"
)

st.plotly_chart(fig, use_container_width=True)