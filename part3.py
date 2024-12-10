import streamlit as st
import pandas as pd
import altair as alt

# Page title and author info
st.markdown("# NBA Player Performance Analysis: Understanding the Modern Game")
st.markdown("### By: Max Zhang, Zhuokai Wu, Jimmy Qiu")
st.write("") 

# Introduction text
st.markdown("""
This interactive visualization explores NBA player statistics from the 2023-24 regular season, 
focusing on how different aspects of player performance relate to each other. Whether you're 
a casual fan or a basketball enthusiast, this analysis will help you understand what makes 
certain players stand out and how different playing styles impact the game.
""")

# Load and prepare data
@st.cache_data  # Cache the data loading to improve performance
def load_data():
    df = pd.read_csv('2023-2024 NBA Player Stats - Regular.csv', sep=';', encoding='latin1')
    
    # Clean data: handle TOT (players who played for multiple teams)
    tot_players = df[df['Tm'] == 'TOT']['Player'].unique()
    clean_df = df[
        (df['Tm'] == 'TOT') |  # Keep total rows
        (~df['Player'].isin(tot_players))  # Keep players who didn't change teams
    ]
    return clean_df

df = load_data()

# Main interactive visualization
st.markdown("## Exploring Player Performance")
st.markdown("""
Use the controls below to explore different aspects of player performance. The visualization 
allows you to see how minutes played, scoring, and shooting efficiency relate to each other 
across the league.
""")

# Add filters for the visualization
min_minutes = st.slider("Minimum Minutes Played per Game", 0, 37, 10)
selected_teams = st.multiselect(
    "Choose your favorite team! (Default: All teams)",
    options=sorted(df['Tm'].unique()),
    default=[]
)

# Filter data based on user selection
filtered_df = df[df['MP'] >= min_minutes]
if selected_teams:
    filtered_df = filtered_df[filtered_df['Tm'].isin(selected_teams)]

# Create main interactive visualization
chart = alt.Chart(filtered_df).mark_circle().encode(
    x=alt.X('MP:Q', 
            title='Minutes Played per Game',
            scale=alt.Scale(zero=False)),
    y=alt.Y('PTS:Q', 
            title='Points per Game',
            scale=alt.Scale(zero=False)),
    color=alt.Color('FG%:Q', 
                   title='Field Goal %',
                   scale=alt.Scale(scheme='viridis')),
    size=alt.Size('AST:Q', 
                 title='Assists per Game',
                 scale=alt.Scale(range=[50, 400])),
    tooltip=[
        alt.Tooltip('Player:N', title='Player'),
        alt.Tooltip('Tm:N', title='Team'),
        alt.Tooltip('MP:Q', title='Minutes', format='.1f'),
        alt.Tooltip('PTS:Q', title='Points', format='.1f'),
        alt.Tooltip('FG%:Q', title='FG%', format='.1%'),
        alt.Tooltip('AST:Q', title='Assists', format='.1f')
    ]
).properties(
    width=700,
    height=500
).interactive()

st.altair_chart(chart, use_container_width=True)

# Analysis text
st.markdown("""
### Understanding the Visualization

This scatter plot reveals several interesting patterns in NBA player performance:

- **Playing Time and Scoring**: The relationship between minutes played and points scored 
  helps identify different player roles - from efficient role players to high-volume scorers.
  
- **Shooting Efficiency**: The color gradient shows field goal percentage, revealing how 
  some players maintain high efficiency despite heavy playing time and scoring load.

- **Playmaking Impact**: The size of each point represents assists per game, helping 
  identify playmakers and how their scoring relates to their distribution abilities.
""")

# Add a section break before contextual visualizations
st.write("---")