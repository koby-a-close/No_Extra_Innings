# Standings.py
# Created by KAC on 03/29/3030

"""This code will take game logs from a season and adjust the final standings for rules where there are no extra
innings and games tied after 9 innings are counted as ties."""

import pandas as pd
from pybaseball import schedule_and_record

# List of teams and years for analysis
teams = ['NYY', 'BOS', 'TBR', 'TOR', 'BAL', 'MIN', 'DET', 'KCR', 'CHW', 'CLE', 'HOU', 'SEA', 'OAK', 'LAA', 'TEX',
         'PHI', 'NYM', 'WSN', 'ATL', 'MIA', 'CHC', 'MIL', 'CIN', 'STL', 'PIT', 'LAD', 'ARI', 'SDP', 'COL', 'SFG']
years = [2019, 2018, 2017, 2016, 2015]

# Dictionaries for leagues and divisions
league_dict = {'NYY': 'AL', 'BOS': 'AL', 'TBR': 'AL', 'TOR': 'AL', 'BAL': 'AL',
                 'MIN': 'AL', 'DET': 'AL', 'KCR': 'AL', 'CHW': 'AL', 'CLE': 'AL',
               'HOU': 'AL', 'SEA': 'AL', 'OAK': 'AL', 'LAA': 'AL', 'TEX': 'AL',
               'PHI': 'NL', 'NYM': 'NL', 'WSN': 'NL', 'ATL': 'NL', 'MIA': 'NL',
               'CHC': 'NL', 'MIL': 'NL', 'CIN': 'NL', 'STL': 'NL', 'PIT': 'NL',
               'LAD': 'NL', 'ARI': 'NL', 'SDP': 'NL', 'COL': 'NL', 'SFG': 'NL'}
division_dict = {'NYY': 'E', 'BOS': 'E', 'TBR': 'E', 'TOR': 'E', 'BAL': 'E',
                 'MIN': 'C', 'DET': 'C', 'KCR': 'C', 'CHW': 'C', 'CLE': 'C',
                 'HOU': 'W', 'SEA': 'W', 'OAK': 'W', 'LAA': 'W', 'TEX': 'W',
                 'PHI': 'E', 'NYM': 'E', 'WSN': 'E', 'ATL': 'E', 'MIA': 'E',
                 'CHC': 'C', 'MIL': 'C', 'CIN': 'C', 'STL': 'C', 'PIT': 'C',
                 'LAD': 'W', 'ARI': 'W', 'SDP': 'W', 'COL': 'W', 'SFG': 'W'}

# Setup dataframes for new/old standings and some extra stats for analysis
df_original_standings = pd.DataFrame(columns=['Year', 'League', 'Division', 'Team', 'Wins', 'Losses', 'Pct'])
df_new_standings = pd.DataFrame(columns=['Year', 'League', 'Division', 'Team', 'Wins', 'Losses', 'Ties', 'Pct'])
df_analysis = pd.DataFrame(columns=['Year', 'Team', 'orig_pct', 'new_pct', 'delta_pct', 'inn_elim'])

# These loops go through each set of game logs and changes the win/loss totals to include ties.
for team in teams:
    for year in years:
        inn_elim = 0
        data = schedule_and_record(year, team)
        # Calculates the number of innings removed for each team
        inn_elim = sum(data.iloc[i]['Inn'] - 9 for i in range(len(data)) if data.iloc[i]['Inn'] > 9)
        # Calculates original standings
        original_W = sum(data['W/L'].str.startswith('W'))
        original_L = sum(data['W/L'].str.startswith('L'))
        original_pct = original_W/162
        # Calculates new standings by making any extra inning game a tie
        new_W = sum((data['Inn'] <= 9) & (data['W/L'].str.startswith('W')))
        new_L = sum((data['Inn'] <= 9) & (data['W/L'].str.startswith('L')))
        new_T = sum(data['Inn'] > 9)
        new_pct = (new_W+(0.5*new_T))/162
        delta_pct = new_pct - original_pct
        lg_temp = league_dict.get(team, "")
        div_temp = division_dict.get(team, "")

        df_original_standings = df_original_standings.append({'Year': year, 'League': lg_temp, 'Division': div_temp, 'Team': team, 'Wins': original_W,
                                                              'Losses': original_L, 'Pct': original_pct}, ignore_index=True)
        df_new_standings = df_new_standings.append({'Year': year, 'League': lg_temp, 'Division': div_temp, 'Team': team, 'Wins': new_W, 'Losses': new_L,
                                              'Ties': new_T, 'Pct': new_pct}, ignore_index=True)
        df_analysis = df_analysis.append({'Year': year, 'Team': team, 'orig_pct': original_pct, 'new_pct': new_pct,
                                              'delta_pct': delta_pct, 'inn_elim': inn_elim}, ignore_index=True)

# Order by division giving year end standings
df_original_standings.sort_values(by=['Year', 'League', 'Division', 'Pct'], inplace=True, ascending=False)
df_old_divisional = df_original_standings.copy()
df_new_standings.sort_values(by=['Year', 'League', 'Division', 'Pct'], inplace=True, ascending=False)
df_new_divisional = df_new_standings.copy()

# Order by league to see playoff pictures
df_original_standings.sort_values(by=['Year', 'League', 'Pct'], inplace=True, ascending=False)
df_old_playoffs = df_original_standings.copy().head(5)
df_new_standings.sort_values(by=['Year', 'League', 'Pct'], inplace=True, ascending=False)
df_new_playoffs = df_new_standings.copy().head(5)

# Save files to CSV
df_original_standings.to_csv('Original_Standings.csv', index=False)
df_new_standings.to_csv('New_Standings.csv', index=False)
df_analysis.to_csv('No_ExtraInn_Analysis.csv', index=False)

# Some basic analysis
num_changes = df_new_standings['Ties'].groupby(df_analysis['Year']).sum()
inn_eliminated = df_analysis['inn_elim'].groupby(df_analysis['Year']).sum()
df_analysis.sort_values(by=['delta_pct'], inplace=True)
top_hurt = df_analysis.head(5)
df_analysis.sort_values(by=['delta_pct'], inplace=True, ascending=False)
top_help = df_analysis.head(5)

