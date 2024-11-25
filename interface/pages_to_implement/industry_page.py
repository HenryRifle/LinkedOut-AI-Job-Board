import sys
import streamlit as st
import plotly.express as px
from pathlib import Path
import plotly.graph_objects as go

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


print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import pandas as pd
    print(f"Pandas version: {pd.__version__}")
except ImportError as e:
    print(f"Import error: {e}")
    raise

# Define base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Read the data
filename = BASE_DIR / 'project_data' / '2023-33' / 'industry.xlsx'
industry_df = pd.read_excel('project_data\\2023-33\\industry.xlsx', sheet_name=11, header=1)

# Drop unnecessary columns
industry_df = industry_df.drop(columns=["Industry type", "Output, 2023[1][2]", "Output, 2033[1][2]", "Compound annual rate of change, output, 2023–33"])

# Rename columns for clarity
industry_df = industry_df.rename(columns={
    "Employment, 2023": "2023 Employment",
    "Employment, 2033": "2033 Employment",
    "2023 National Employment Matrix title": "Industry",
    "2023 National Employment Matrix code": "Code",
    "Employment change, numeric, 2023–33": "Prediction Numeric Change",
    "Employment change, percent, 2023–33": "Prediction Percent Change",
    "Compound annual rate of change, employment, 2023–33": "Prediction Annual Rate of Change"
})

# Clean up data
industry_df = industry_df.drop_duplicates(subset='Industry', keep='first')  # gets rid of dups
industry_df = industry_df.drop(industry_df.tail(5).index)  # drops the footnotes

# Create Streamlit sidebar multiselect
selected_industries = st.sidebar.multiselect(
    "Select Industries",
    options=industry_df['Industry'].unique(),
    default=industry_df['Industry'].unique()[:10]  # Default to first 10 for better visibility
)

# Create figure
fig = go.Figure()

# Filter and sort data
filtered_df = industry_df[industry_df['Industry'].isin(selected_industries)].sort_values('2023 Employment', ascending=True)

# Add lines connecting 2023 and 2033 points
for idx, row in filtered_df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row['2023 Employment'], row['2033 Employment']],
        y=[row['Industry'], row['Industry']],
        mode='lines',
        line=dict(color='gray', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add 2023 points
fig.add_trace(go.Scatter(
    x=filtered_df['2023 Employment'],
    y=filtered_df['Industry'],
    mode='markers',
    name='2023',
    marker=dict(
        symbol='circle',
        size=12,
        color='#377eb8'
    ),
    hovertemplate="<b>%{y}</b><br>" +
                  "2023 Employment: %{x:,.0f} thousand<extra></extra>"
))

# Add 2033 points
fig.add_trace(go.Scatter(
    x=filtered_df['2033 Employment'],
    y=filtered_df['Industry'],
    mode='markers',
    name='2033',
    marker=dict(
        symbol='circle',
        size=12,
        color='#e41a1c'
    ),
    hovertemplate="<b>%{y}</b><br>" +
                  "2033 Employment: %{x:,.0f} thousand<extra></extra>"
))

# Add change annotations
for idx, row in filtered_df.iterrows():
    change = row['2033 Employment'] - row['2023 Employment']
    change_pct = (change / row['2023 Employment']) * 100
    fig.add_annotation(
        x=max(row['2023 Employment'], row['2033 Employment']) + filtered_df['2033 Employment'].max() * 0.02,
        y=row['Industry'],
        text=f"{'+' if change > 0 else ''}{change:,.0f} ({change_pct:+.1f}%)",
        showarrow=False,
        font=dict(
            size=10,
            color='green' if change > 0 else 'red'
        ),
        xanchor='left'
    )

# Update layout
fig.update_layout(
    height=max(600, len(selected_industries) * 40),
    width=1000,
    title="Employment Change by Industry (2023-2033)",
    xaxis_title="Employment Numbers (thousands)",
    yaxis_title="Industry",
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template="plotly_white",
    xaxis=dict(
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='lightgray'
    ),
    margin=dict(r=150)  # Add right margin for annotations
)

# Add descriptive text
st.title("Employment Change by Industry (2023-2033)")
st.write("""
Interactive chart showing employment changes by industry between 2023 and 2033.
- Blue dots represent 2023 employment
- Red dots represent projected 2033 employment
- Gray lines connect the same industry across years
- Numbers on the right show absolute and percentage changes
""")
st.plotly_chart(fig, use_container_width=True)

# Optionally, add a data table showing the numeric changes
if st.checkbox("Show detailed data"):
    change_data = filtered_df[[
        'Industry', 
        '2023 Employment', 
        '2033 Employment', 
        'Prediction Numeric Change', 
        'Prediction Percent Change'
    ]]
    st.dataframe(change_data)
