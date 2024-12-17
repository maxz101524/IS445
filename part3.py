import streamlit as st
import pandas as pd
import altair as alt

st.markdown("# NBA Player Performance Analysis: Understanding the Modern Game")
st.markdown("### By: Max Zhang, Zhuokai Wu, Jimmy Qiu")
st.write("") 

st.markdown("""
This interactive visualization explores NBA player statistics from the 2023-24 regular season, 
focusing on how different aspects of player performance relate to each other. Whether you're 
a casual fan or a basketball enthusiast, this analysis will help you understand what makes 
certain players stand out and how different playing styles impact the game.
""")

@st.cache_data  
def load_data():
    df = pd.read_csv('2023-2024 NBA Player Stats - Regular.csv', sep=';', encoding='latin1')
    
    tot_players = df[df['Tm'] == 'TOT']['Player'].unique()
    clean_df = df[
        (df['Tm'] == 'TOT') |  
        (~df['Player'].isin(tot_players))  
    ]
    return clean_df

df = load_data()

st.markdown("## Exploring Player Performance")
st.markdown("""
Use the controls below to explore different aspects of player performance. The visualization 
allows you to see how minutes played, scoring, and shooting efficiency relate to each other 
across the league.
""")

min_minutes = st.slider("Minimum Minutes Played per Game", 0, 37, 10)
selected_teams = st.multiselect(
    "Choose your favorite team! (Default: All teams)",
    options=sorted(df['Tm'].unique()),
    default=[]
)

filtered_df = df[df['MP'] >= min_minutes]
if selected_teams:
    filtered_df = filtered_df[filtered_df['Tm'].isin(selected_teams)]

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

st.write("---")

st.markdown("## Preseason Predictions vs Reality")
st.markdown("""
Before every NBA season, analysts make predictions about team performance. Let's see if teams are living up to the hype. In the plot below, hover above any point to see team name and the predicted vs. actual winrates.
""")

actual = pd.read_csv('NBA Stats 202324 Team Metrics Away-Home-Last 5 Splits-2.csv')
expected = pd.read_csv('Teams_Estimated_Metrics_Season23_24.csv')

actual['TEAM'] = actual['TEAM'].str.strip()
expected['TEAM_NAME'] = expected['TEAM_NAME'].str.strip()

comparison_data = pd.DataFrame({
    'Team': actual['TEAM'],
    'Actual_Win_PCT': actual['WIN%'],
    'Expected_Win_PCT': expected['W_PCT'],
    'Conference': actual['CONF']
})

comparison_chart = alt.Chart(comparison_data).mark_circle(size=100).encode(
    x=alt.X('Expected_Win_PCT:Q', 
            title='Preseason Expected Win %',
            scale=alt.Scale(domain=[0, 1])),
    y=alt.Y('Actual_Win_PCT:Q', 
            title='Current Win %',
            scale=alt.Scale(domain=[0, 1])),
    color=alt.Color('Conference:N', 
                   scale=alt.Scale(domain=['East', 'West'],
                                 range=['#C41E3A', '#1D428A'])),  # NBA official colors
    tooltip=['Team', 'Expected_Win_PCT:Q', 'Actual_Win_PCT:Q']
).properties(
    width=600,
    height=400
)

diagonal = alt.Chart(pd.DataFrame({'x': [0, 1], 'y': [0, 1]})).mark_line(
    strokeDash=[5, 5],
    color='gray',
    opacity=0.5
).encode(x='x', y='y')

st.altair_chart(comparison_chart + diagonal, use_container_width=True)

st.markdown("""
Looking at how NBA teams are performing compared to preseason predictions tells us an interesting story 
about expectations versus reality. Teams above the dotted line are exceeding expectations - they're 
winning more games than analysts thought they would. Teams below the line are falling short of their 
predicted success. This season, several teams have surprised analysts - for example, high-performing 
teams like Oklahoma City and Minnesota are doing even better than expected, while some traditionally 
strong teams haven't quite lived up to preseason hype. This shows how unpredictable the NBA can be, 
with young teams sometimes developing faster than expected and veteran teams facing unexpected challenges.
""")


st.markdown("## Team Performance Profile")
st.markdown("""
How do teams achieve their success? This visualization shows the relationship between scoring (PPG) 
and pace, with defensive rating indicated by point size. Teams above the middle of the plot are 
higher scoring, while teams further right play at a faster pace. Larger circles indicate better defense.
""")

actual['defense_size'] = actual['dEFF'].max() - actual['dEFF']

performance_chart = alt.Chart(actual).mark_circle().encode(
    x=alt.X('PACE:Q', 
            title='Pace (Possessions per 48 minutes)',
            scale=alt.Scale(zero=False)),
    y=alt.Y('PPG:Q', 
            title='Points Per Game',
            scale=alt.Scale(zero=False)),
    size=alt.Size('defense_size:Q', 
                 title='Defensive Rating',
                 legend=alt.Legend(title="Defense Quality")),
    color=alt.Color('CONF:N',
                   scale=alt.Scale(domain=['East', 'West'],
                                 range=['#C41E3A', '#1D428A'])),
    tooltip=['TEAM', 
            alt.Tooltip('PPG:Q', title='Points Per Game', format='.1f'),
            alt.Tooltip('PACE:Q', title='Pace', format='.1f'),
            alt.Tooltip('dEFF:Q', title='Defensive Rating', format='.1f'),
            alt.Tooltip('WIN%:Q', title='Win %', format='.3f')]
).properties(
    width=600,
    height=400
)


notable_teams = pd.concat([
    actual.nlargest(3, 'PPG'),
    actual.nlargest(3, 'PACE')
]).drop_duplicates()

text = alt.Chart(notable_teams).mark_text(
    align='left',
    baseline='middle',
    dx=5
).encode(
    x='PACE:Q',
    y='PPG:Q',
    text='TEAM:N'
)

st.altair_chart(performance_chart + text, use_container_width=True)

st.markdown("""
The way teams score points in the NBA can tell us a lot about their playing style and strategy. 
Looking at this chart, we can see big differences in how teams approach the game. Teams like Indiana 
and Boston score a lot of points but do it in different ways - Indiana plays at a very fast pace, 
while Boston is more methodical but highly efficient. Teams with larger circles are better at stopping 
their opponents from scoring (better defense), prooving that success in the NBA isn't just about 
scoring points. Some teams win with high-powered offenses, others with strong defense, and the best 
teams often excel at both.
""")

st.write("---")
st.markdown("## Dataset Sources")
st.markdown("""1. 2023-2024 NBA Player Stats - Regular (Main Dataset): https://github.com/maxz101524/IS445/blob/main/2023-2024%20NBA%20Player%20Stats%20-%20Regular%20Comma%20Sep.csv""")
st.markdown("""2. NBA Stats 2023-24 Actual Team Metrics: https://github.com/maxz101524/IS445/blob/main/NBA%20Stats%20202324%20Team%20Metrics%20Away-Home-Last%205%20Splits-2.csv""")
st.markdown("""3. NBA Stats 2023-24 Projected Team Metrics: https://github.com/maxz101524/IS445/blob/main/Teams_Estimated_Metrics_Season23_24.csv""")