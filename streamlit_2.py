import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
job_listings = pd.read_csv(r'C:\Users\31857\Desktop\streamlit\gOOgle_jobs.csv')

# Rename the column from 'cluster_label' to 'Job function'
job_listings.rename(columns={'cluster_label': 'Job function'}, inplace=True)

# Update the values for the rows where Company is 'Amul'
job_listings.loc[job_listings['Company'] == 'Amul', 'IQ_INDUSTRY_CLASSIFICATION'] = 'Consumer Staples'
job_listings.loc[job_listings['Company'] == 'Amul', 'IQ_INDUSTRY_GROUP'] = 'Food, Beverage and Tobacco'

# --- SIDEBAR FILTERS ---
st.sidebar.title("Filters")

# Industry filter
selected_industries = st.sidebar.multiselect(
    "Industry", 
    job_listings["IQ_INDUSTRY_CLASSIFICATION"].unique(), 
    default=job_listings["IQ_INDUSTRY_CLASSIFICATION"].unique()
)

# Job Function filter
selected_functions = st.sidebar.multiselect(
    "Job Function", 
    job_listings["Job function"].unique(), 
    default=job_listings["Job function"].unique()
)

# Keyword Search
search_term = st.sidebar.text_input("Keyword Search")

# Apply Filters
filtered_jobs = job_listings[
    job_listings["IQ_INDUSTRY_CLASSIFICATION"].isin(selected_industries) &
    job_listings["Job function"].isin(selected_functions) &
    job_listings["Standardized Role"].str.lower().str.contains(search_term.lower(), na=False)
]

# Group by company and calculate mean industry importance score
top_companies_data_via_imp_score = filtered_jobs.groupby('Company')['Mean Industry Importance Score'].mean().reset_index()
top_companies_data_via_imp_score = top_companies_data_via_imp_score.sort_values(by='Mean Industry Importance Score', ascending=False)

# Merge with other relevant data
top_companies_data_via_imp_score = pd.merge(
    top_companies_data_via_imp_score, 
    filtered_jobs[['Company', 'IQ_INDUSTRY_CLASSIFICATION', 'IQ_INDUSTRY_GROUP', 'Open Positions', 'Job function']].drop_duplicates('Company'), 
    how='left', 
    left_on='Company', 
    right_on='Company'
)

# Filter companies with at least 3 open positions
top_companies_data_via_imp_score = top_companies_data_via_imp_score[top_companies_data_via_imp_score['Open Positions'] >= 3].reset_index(drop=True)

# --- MAIN CONTENT ---
st.title("Job Insights Dashboard")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Top Companies", "Market Demand", "Trending Skills", "Industry Insights"])

# Tab 1: Top Companies
with tab1:
    st.subheader("Top Companies for Your Students")

    for index, row in top_companies_data_via_imp_score.iterrows():
        with st.container():
            st.write(f"**{index+1}. {row['Company']}**")
            col1, col2, col3 = st.columns(3)  # Divide the row into three columns for better layout
            with col1:
                st.write(f"**Industry:** {row['IQ_INDUSTRY_CLASSIFICATION']}")
            with col2:
                st.write(f"**Job Function:** {row['Job function']}")
            with col3:
                st.write(f"**Open Positions:** {row['Open Positions']}")
            st.button("Contact", key=row['Company'])  # Placeholder for a contact button

# Tab 2: Market Demand
with tab2:
    st.subheader("Current Market Demand")

    # Use the existing 'Open Positions' column
    top_companies_data = filtered_jobs[['Company', 'Open Positions', 'IQ_INDUSTRY_CLASSIFICATION', 'IQ_INDUSTRY_GROUP', 'Job function']].drop_duplicates('Company')
    top_companies_data = top_companies_data.sort_values(by='Open Positions', ascending=False)

    for index, row in top_companies_data.iterrows():
        with st.container():
            st.write(f"**{index+1}. {row['Company']}**")
            col1, col2, col3 = st.columns(3)  # Divide the row into three columns for better layout
            with col1:
                st.write(f"**Industry:** {row['IQ_INDUSTRY_CLASSIFICATION']}")
            with col2:
                st.write(f"**Job Function:** {row['Job function']}")
            with col3:
                st.write(f"**Open Positions:** {row['Open Positions']}")
            st.button("Contact", key=index)  # Placeholder for a contact button

# Tab 3: Trending Skills
with tab3:
    # Updated top skills data ordered in decreasing order of job postings
    top_skills_data = pd.DataFrame({
        'Skill': [
            'Time Management', 'Problem Solving', 'Communication', 'Adaptability', 'Team Collaboration', 
            'Data Analysis', 'Attention to Detail', 'Collaboration', 'Leadership', 
            'Project Management', 'Team Management', 'Organizational Skills', 
            'Analytical Thinking', 'Data Visualization', 'Financial Analysis', 'Agile Methodologies'
        ],
        'Job Postings': [
            376, 345, 334, 302, 247, 103, 87, 78, 61, 48, 40, 28, 22, 21, 19, 19
        ]
    })

    # Create Plotly charts here
    top_skills_fig = px.bar(top_skills_data, x='Skill', y='Job Postings', title='Top Skills in Demand')

    st.plotly_chart(top_skills_fig)

# Tab 4: Industry Insights
with tab4:
    st.subheader("Industry Insights")
    industry_counts = job_listings.groupby('IQ_INDUSTRY_CLASSIFICATION').count()['Standardized Role'].reset_index()
    industry_counts.columns = ['Industry', 'Open Positions']
    industry_counts = industry_counts.sort_values(by='Open Positions', ascending=False)

    fig = px.bar(
        industry_counts,
        x='Industry',
        y='Open Positions',
        title='Open Positions by Industry',
        color='Industry',
        color_discrete_sequence=px.colors.qualitative.Vivid,
        text='Open Positions',
        hover_data={'Industry': True, 'Open Positions': True}
    )

    fig.update_layout(
        title={
            'text': 'Open Positions by Industry',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Industry',
        yaxis_title='Open Positions',
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#7f7f7f"
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Arial, sans-serif"
        ),
        yaxis=dict(
            title='Open Positions',
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        xaxis=dict(
            title='Industry',
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        )
    )

    st.plotly_chart(fig)
