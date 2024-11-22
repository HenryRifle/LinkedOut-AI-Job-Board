import pandas as pd
import numpy as np
import openpyxl
import pandas as pd
import holoviews as hv
from holoviews import opts
import streamlit as st
from bokeh.models import HoverTool
hv.extension('bokeh')
import plotly.express as px

path = 'project_data'
filename = path + '/2019-29/occupation.xlsx'

# occu_obj = openpyxl.load_workbook(path + '\\2019-29\\occupation.xlsx')

# occu_obj_23 = openpyxl.load_workbook(path + '\\2023-33\\occupation.xlsx')


index_sheet = pd.read_excel("project_data\\2019-29\\occupation.xlsx")
# index_sheet_23 = pd.read_excel()
sheet_data = {}
sheet_data_23 = {}

def basic_data_cleaning(data1):

    data1 = data1.rename(columns={data1.columns[0]: "Job Title"})
    
    try:
        index = data1[data1['Job Title'].str.contains('Footnotes')].index[0]
    except:
        index = data1[data1['Job Title'].str.contains('U.S. Bureau of Labor Statistics')].index[0]
        
    data1 = data1.iloc[:index]

    try:
        data1 = data1.drop('2019 National Employment Matrix code', axis=1)
    except:
        pass
    
    return data1

for i in index_sheet.index:
    data = pd.read_excel(filename, sheet_name=i+1, skiprows=1)
    
    print(index_sheet.loc[i].iloc[0])
    
    sheet_data[index_sheet.loc[i].iloc[0]] = basic_data_cleaning(data)


df = pd.DataFrame(sheet_data[index_sheet.loc[0].iloc[0]])
melted_df = df.melt(
    id_vars='Job Title',
    value_vars=['Employment, 2019', 'Employment, 2029'],
    var_name='Year',
    value_name='Employment'
)
melted_df['Year'] = melted_df['Year'].str.extract(r'(\d+)').astype(int)

def dashboard():
    st.title("Employment Trends (2019-2029)")
    st.write("Interactive line plot of employment trends for selected occupational groups.")

    selected_groups = st.multiselect(
        "Select Occupational Groups",
        options=df['Job Title'].unique(),
        default=df['Job Title'].unique()
    )


    filtered_data = melted_df[melted_df['Job Title'].isin(selected_groups)]


    fig = px.line(
        filtered_data,
        x="Year",
        y="Employment",
        color="Job Title",
        title="Employment Trends by Job Title",
        labels={"Employment": "Employment Numbers", "Year": "Year", "Job Title": "Job Title"}
    )

    fig.update_layout(
        legend=dict(title="Job Title", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=1000,
        width=800
    )


    fig.update_traces(
        hovertemplate="<b>%{legendgroup}</b><br>Year: %{x}<br>Employment: %{y}<extra></extra>"
    )


    st.plotly_chart(fig, use_container_width=True)
dashboard()