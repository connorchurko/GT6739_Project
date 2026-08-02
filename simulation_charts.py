#!/usr/bin/env python
# coding: utf-8

# In[27]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter


# In[28]:


## Loading in the dataframes from the simulation data
game_300_df = pd.read_excel('../Solitaire Data Test 5 300 Limit.xlsx', sheet_name='Move Data')
output_300_df = pd.read_excel('../Solitaire Data Test 5 300 Limit.xlsx', sheet_name='Output Data')

game_500_df = pd.read_excel('../Solitaire Data Test 6 500 Limit.xlsx', sheet_name='Move Data')
output_500_df = pd.read_excel('../Solitaire Data Test 6 500 Limit.xlsx', sheet_name='Output Data')

var_df = pd.read_excel('../Solitaire Variance Data.xlsx', sheet_name='Move Data')


# In[29]:


results = ['WON', 'LOST']
strategies = ['foundation_first', 'greedy', 'random']
strat_labels = ['Foundation First', 'Greedy', 'Random']
move_limits = [300, 500]


# In[30]:


# 1: Histogram for each strategy and move limit for total move count, with dashed line showing the average - wins and losses
output_folder = Path(r'C:\Users\mauni\OneDrive\Documents\Grad School\ISYE 6739 - Statistical Methods\Project\Project Figures\Move Count Histograms')

for result in results:
    for index, strategy in enumerate(strategies):
        for move_limit in move_limits:

            file_name = f'{strategy}_{move_limit}_{result}_moveCount_hist.png'
            output_file = output_folder / file_name

            if move_limit == 300:
                move_data = game_300_df.loc[(game_300_df['Strategy'] == strategy) & (game_300_df['Result'] == result), 'moveCount']
                avg_moves_per_win = output_300_df.loc[output_300_df['Strategy'] == strategy, 'avgMovesPerWin'].iloc[0]
                avg_moves_per_loss = output_300_df.loc[output_300_df['Strategy'] == strategy, 'avgMovesPerLoss'].iloc[0]
                wins = output_300_df.loc[output_300_df['Strategy'] == strategy, 'wins'].iloc[0]
                losses = output_300_df.loc[output_300_df['Strategy'] == strategy, 'losses'].iloc[0]
            elif move_limit == 500:
                move_data = game_500_df.loc[(game_500_df['Strategy'] == strategy) & (game_500_df['Result'] == result), 'moveCount']
                avg_moves_per_win = output_500_df.loc[output_500_df['Strategy'] == strategy, 'avgMovesPerWin'].iloc[0]
                avg_moves_per_loss = output_500_df.loc[output_500_df['Strategy'] == strategy, 'avgMovesPerLoss'].iloc[0]
                wins = output_500_df.loc[output_500_df['Strategy'] == strategy, 'wins'].iloc[0]
                losses = output_500_df.loc[output_500_df['Strategy'] == strategy, 'losses'].iloc[0]

            strat_name = strat_labels[index]

            if result == 'WON':
                avg_moves = avg_moves_per_win
                n = wins
            elif result == 'LOST':
                avg_moves = avg_moves_per_loss
                n = losses

            fig, ax = plt.subplots()

            plt.hist(move_data, bins=32, color='skyblue', edgecolor='black')
            plt.title(f'Histogram of Total Moves per Game: {strat_name}\nResult: {result}, Number of Games: {n}', fontweight='bold')
            plt.xlabel('Total Moves to Win', fontweight='bold')
            plt.ylabel('Frequency', fontweight='bold')

            plt.gca().set_axisbelow(True)
            plt.grid(axis='both', linestyle='-', color='lightgray', linewidth=0.7, alpha=0.6)

            plt.axvline(x=avg_moves, color='red', linestyle='--', linewidth=2, label=f'Average Moves to Win: {avg_moves:.2f}')
            plt.legend(edgecolor='gray', framealpha=0.5)

            plt.savefig(output_file, dpi=300, bbox_inches="tight", transparent=False)
            plt.close()


# In[31]:


# 2: Histogram for each strategy for each move type, show average with a dashed line - wins
output_folder = Path(r'C:\Users\mauni\OneDrive\Documents\Grad School\ISYE 6739 - Statistical Methods\Project\Project Figures\Move Type Bar Charts')

target_cols = ['t2t_count', 'tableau_count', 'waste_count', 'foundation_count']
chart_xlabel = ['Within Tableau', 'Stock to Tableau', 'To Wastepile', 'To Foundation']

for result in results:
    for index, strategy in enumerate(strategies):
        for move_limit in move_limits:


            file_name = f'{strategy}_{move_limit}_{result}_moveType_bar.png'
            output_file = output_folder / file_name

            if (move_limit == 300):
                move_data = game_300_df.loc[(game_300_df['Strategy'] == strategy) & (game_300_df['Result'] == result), target_cols]
                wins = output_300_df.loc[output_300_df['Strategy'] == strategy, 'wins'].iloc[0]
                losses = output_300_df.loc[output_300_df['Strategy'] == strategy, 'losses'].iloc[0]
            elif (move_limit == 500):
                move_data = game_500_df.loc[(game_500_df['Strategy'] == strategy) & (game_500_df['Result'] == result), target_cols]
                wins = output_500_df.loc[output_500_df['Strategy'] == strategy, 'wins'].iloc[0]
                losses = output_500_df.loc[output_500_df['Strategy'] == strategy, 'losses'].iloc[0]

            move_averages = move_data[target_cols].mean()
            # We want to show the breakdown of moves for each strategy (how many times a specific move was used for each strategy, show average or show total counts?)
            if result == 'WON':
                n = wins
            elif result == 'LOST':
                n = losses

            strat_name = strat_labels[index]

            plt.bar(chart_xlabel, move_averages, color='skyblue', edgecolor='black', width=0.6)
            plt.title(f'Individual Move Type Averages for all ({n}) games {result}: {strat_name}', fontweight='bold')
            plt.xlabel('Move Type', fontweight='bold')
            plt.ylabel('Average Moves per Game', fontweight='bold')

            plt.gca().set_axisbelow(True)
            plt.grid(axis='both', linestyle='-', color='lightgray', linewidth=0.7, alpha=0.6)

            plt.savefig(output_file, dpi=300, bbox_inches="tight", transparent=False)
            plt.close()


# In[32]:


# 3: Histogram showing time distribution for each strategy - wins and losses
output_folder = Path(r'C:\Users\mauni\OneDrive\Documents\Grad School\ISYE 6739 - Statistical Methods\Project\Project Figures\Game Time Histograms')

for result in results:
    for index, strategy in enumerate(strategies):
        for move_limit in move_limits:

            file_name = f'{strategy}_{move_limit}_{result}_gameTime_hist.png'
            output_file = output_folder / file_name

            if move_limit == 300:
                move_data = game_300_df.loc[(game_300_df['Strategy'] == strategy) & (game_300_df['Result'] == result), 'game_duration']
                avg_time_win = output_300_df.loc[output_300_df['Strategy'] == strategy, 'avg_duration_win'].iloc[0]
                avg_time_loss = output_300_df.loc[output_300_df['Strategy'] == strategy, 'avg_duration_loss'].iloc[0]
                wins = output_300_df.loc[output_300_df['Strategy'] == strategy, 'wins'].iloc[0]
                losses = output_300_df.loc[output_300_df['Strategy'] == strategy, 'losses'].iloc[0]
            elif move_limit == 500:
                move_data = game_500_df.loc[(game_500_df['Strategy'] == strategy) & (game_500_df['Result'] == result), 'game_duration']
                avg_time_win = output_500_df.loc[output_500_df['Strategy'] == strategy, 'avg_duration_win'].iloc[0]
                avg_time_loss = output_500_df.loc[output_500_df['Strategy'] == strategy, 'avg_duration_loss'].iloc[0]
                wins = output_500_df.loc[output_500_df['Strategy'] == strategy, 'wins'].iloc[0]
                losses = output_500_df.loc[output_500_df['Strategy'] == strategy, 'losses'].iloc[0]

            strat_name = strat_labels[index]

            if result == 'WON':
                avg_moves = avg_time_win
                n = wins
            elif result == 'LOST':
                avg_moves = avg_time_loss
                n = losses

            fig, ax = plt.subplots()

            plt.hist(move_data, bins=32, color='skyblue', edgecolor='black')
            plt.title(f'Histogram of Game Duration for Games {result}: {strat_name}\nNumber of games: {n}', fontweight='bold')
            plt.xlabel('Game Duration (seconds)', fontweight='bold')
            plt.ylabel('Frequency', fontweight='bold')

            plt.gca().set_axisbelow(True)
            plt.grid(axis='both', linestyle='-', color='lightgray', linewidth=0.7, alpha=0.6)

            plt.axvline(x=avg_moves, color='red', linestyle='--', linewidth=2, label=f'Average Time: {avg_moves:.2f}')
            plt.legend(edgecolor='gray', framealpha=0.5)

            plt.savefig(output_file, dpi=300, bbox_inches="tight", transparent=False)
            plt.close()


# In[50]:


# 4: Bar Chart showing average time comparison for each strategy
output_folder = Path(r'C:\Users\mauni\OneDrive\Documents\Grad School\ISYE 6739 - Statistical Methods\Project\Project Figures\Average Game Time Bar Charts')

for result in results:
    for move_limit in move_limits:

        file_name = f'{move_limit}_{result}_avgGameTime_bar.png'
        output_file = output_folder / file_name

        if (move_limit == 300):
            avg_t_ff_w = output_300_df.loc[output_300_df['Strategy'] == 'foundation_first', 'avg_duration_win'].iloc[0]
            avg_t_gr_w = output_300_df.loc[output_300_df['Strategy'] == 'greedy', 'avg_duration_win'].iloc[0]
            avg_t_rnd_w = output_300_df.loc[output_300_df['Strategy'] == 'random', 'avg_duration_win'].iloc[0]
            avg_t_ff_l = output_300_df.loc[output_300_df['Strategy'] == 'foundation_first', 'avg_duration_loss'].iloc[0]
            avg_t_gr_l = output_300_df.loc[output_300_df['Strategy'] == 'greedy', 'avg_duration_loss'].iloc[0]
            avg_t_rnd_l = output_300_df.loc[output_300_df['Strategy'] == 'random', 'avg_duration_loss'].iloc[0]
            median_ff = game_300_df.loc[(game_300_df['Strategy'] == 'foundation_first') & (game_300_df['Result'] == result), 'game_duration'].median()
            median_gr = game_300_df.loc[(game_300_df['Strategy'] == 'greedy') & (game_300_df['Result'] == result), 'game_duration'].median()
            median_rnd = game_300_df.loc[(game_300_df['Strategy'] == 'random') & (game_300_df['Result'] == result), 'game_duration'].median()
            wins = output_300_df['wins'].sum()
            losses = output_300_df['losses'].sum()
        elif (move_limit == 500):
            avg_t_ff_w = output_500_df.loc[output_500_df['Strategy'] == 'foundation_first', 'avg_duration_win'].iloc[0]
            avg_t_gr_w = output_500_df.loc[output_500_df['Strategy'] == 'greedy', 'avg_duration_win'].iloc[0]
            avg_t_rnd_w = output_500_df.loc[output_500_df['Strategy'] == 'random', 'avg_duration_win'].iloc[0]
            avg_t_ff_l = output_500_df.loc[output_500_df['Strategy'] == 'foundation_first', 'avg_duration_loss'].iloc[0]
            avg_t_gr_l = output_500_df.loc[output_500_df['Strategy'] == 'greedy', 'avg_duration_loss'].iloc[0]
            avg_t_rnd_l = output_500_df.loc[output_500_df['Strategy'] == 'random', 'avg_duration_loss'].iloc[0]
            median_ff = game_500_df.loc[(game_500_df['Strategy'] == 'foundation_first') & (game_500_df['Result'] == result), 'game_duration'].median()
            median_gr = game_500_df.loc[(game_500_df['Strategy'] == 'greedy') & (game_500_df['Result'] == result), 'game_duration'].median()
            median_rnd = game_500_df.loc[(game_500_df['Strategy'] == 'random') & (game_500_df['Result'] == result), 'game_duration'].median()
            wins = output_500_df['wins'].sum()
            losses = output_500_df['losses'].sum()

        if result == 'WON':
            time_avg = [avg_t_ff_w, avg_t_gr_w, avg_t_rnd_w]
            n = wins
        elif result == 'LOST':
            time_avg = [avg_t_ff_l, avg_t_gr_l, avg_t_rnd_l]
            n = losses

        median_data = [median_ff, median_gr, median_rnd]

        plt.bar(strat_labels, time_avg, color='skyblue', edgecolor='black', width=0.6, label='Average Time')
        plt.scatter(strat_labels,median_data, color='red', marker='D', s=100, zorder=3, label='Median Time')
        plt.title(f'Average Time for {n}/3000 games {result}', fontweight='bold')
        plt.xlabel('Strategies', fontweight='bold')
        plt.ylabel('Time per Game (seconds)', fontweight='bold')
        plt.gca().set_axisbelow(True)
        plt.grid(axis='both', linestyle='-', color='lightgray', linewidth=0.7, alpha=0.6)
        plt.legend()
        plt.savefig(output_file, dpi=300, bbox_inches="tight", transparent=False)
        plt.close()


# In[44]:


# 5: Show variance in moves for the same 5 seeds ran like 100 times
output_folder = Path(r'C:\Users\mauni\OneDrive\Documents\Grad School\ISYE 6739 - Statistical Methods\Project\Project Figures\Variance Charts')

seeds = [0, 1, 2, 3, 4]

for seed in seeds:
    for index, strategy in enumerate(strategies):
        for result in results:

            file_name = f'{strategy}_seed_{seed}_{result}_moveType_Variance.png'
            output_file = output_folder / file_name

            # Histogram showing variance of moves count per seed x strategy combo (color for result?)
            move_data = var_df.loc[(var_df['Strategy'] == strategy) & (var_df['Seed'] == seed) & (var_df['Result'] == result), 'moveCount']

            if result == 'WON':
                n = len(move_data)
            else:
                n = len(move_data)

            if n > 0:
                strat_title = strat_labels[index]
                bin_size = int(np.ceil(np.sqrt(n)))

                plt.hist(move_data, bins=bin_size, color='skyblue', edgecolor='black')
                plt.title(f'Histogram of Total Move Counts for Seed {seed} and {strat_title}\nGames {result} : {n}/100', fontweight='bold')
                plt.xlabel('Total Moves to Win', fontweight='bold')
                plt.ylabel('Frequency', fontweight='bold')

                plt.gca().set_axisbelow(True)
                plt.grid(axis='both', linestyle='-', color='lightgray', linewidth=0.7, alpha=0.6)

                plt.savefig(output_file, dpi=300, bbox_inches="tight", transparent=False)
                plt.close()

