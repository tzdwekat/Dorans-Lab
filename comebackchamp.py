# -*- coding: utf-8 -*-
"""
Created on Tue May  5 18:12:56 2020

@author: tariq
"""

import pandas as pd
import numpy as np
import math
from sqlalchemy import create_engine

## PROGRAM PARAMETERS ##
wk_dir = 'C:/Users/tariq/DLAB'
datapath = wk_dir + '/DATA/COMEBACK_DATA/comebackchamp.csv'

#CREATE THE DATA FRAME
df = pd.read_csv(datapath,index_col=0)

#tf = df.groupby(["matchid","timestamp_minute","teamId"]).agg({"totalGold":"sum","win":"max"}).reset_index()
#tf2 = tf.pivot(index=["matchid","timestamp_minute"],columns="teamId",values="totalGold") #,"win"])
#pivot the table with an aggregate function
tf = pd.pivot_table(df,values=["totalGold","win"],
                     index=["matchid","champion","participantid"],
                     columns="teamId",
                     aggfunc="sum").reset_index()
#rename columns
tf.columns = ["matchid","champ","partid","blue_gold","red_gold","blue_win","red_win"]
#make an equation for mean shrinking
def mean_shrink(game_outcomes):
    """ Take a list of binary data and compute win rate estimate that shrinks
    towards 0. """
    n_wins = game_outcomes.sum(skipna = False)
    n_games = len(game_outcomes)
    n_fake_wins = 5
    n_fake_games = 10
    winrate_shrunk = ((n_wins + n_fake_wins)/(n_games + n_fake_games))*100
    return winrate_shrunk
#make a champ win column in which the win is counted for the champion rather than the team
conditions = [
    (tf['partid'] == 1) & (tf['blue_win'] == 1),
    (tf['partid'] == 2) & (tf['blue_win'] == 1),
    (tf['partid'] == 3) & (tf['blue_win'] == 1),
    (tf['partid'] == 4) & (tf['blue_win'] == 1),
    (tf['partid'] == 5) & (tf['blue_win'] == 1),
    (tf['partid'] == 1) & (tf['blue_win'] == 0),
    (tf['partid'] == 2) & (tf['blue_win'] == 0),
    (tf['partid'] == 3) & (tf['blue_win'] == 0),
    (tf['partid'] == 4) & (tf['blue_win'] == 0),
    (tf['partid'] == 5) & (tf['blue_win'] == 0),
    (tf['partid'] == 6) & (tf['red_win'] == 1),
    (tf['partid'] == 7) & (tf['red_win'] == 1),
    (tf['partid'] == 8) & (tf['red_win'] == 1),
    (tf['partid'] == 9) & (tf['red_win'] == 1),
    (tf['partid'] == 10) & (tf['red_win'] == 1),
    (tf['partid'] == 6) & (tf['red_win'] == 0),
    (tf['partid'] == 7) & (tf['red_win'] == 0),
    (tf['partid'] == 8) & (tf['red_win'] == 0),
    (tf['partid'] == 9) & (tf['red_win'] == 0),
    (tf['partid'] == 10) & (tf['red_win'] == 0)
    ]
choices = [1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0]
tf['champ_win'] = np.select(conditions, choices)
#we need total gold
tf1 = pd.pivot_table(df,values=["totalGold","win"],
                     index=["matchid","timestamp_minute"],
                     columns="teamId",
                     aggfunc="sum").reset_index()
tf1.columns = ["matchid","timestamp_minute","blue_gold","red_gold","blue_win","red_win"]
tf['totalgold'] = tf1['blue_gold'] + tf1['red_gold']
tf['redg'] = tf1['red_gold']
tf['blueg'] = tf1['blue_gold']
#make team gold rather than redg blueg
conditions =[
    (tf['partid'] == 1),
    (tf['partid'] == 2),
    (tf['partid'] == 3),
    (tf['partid'] == 4),
    (tf['partid'] == 5),
    (tf['partid'] == 6),
    (tf['partid'] == 7),
    (tf['partid'] == 8),
    (tf['partid'] == 9),
    (tf['partid'] == 10)
        ]
choices = [tf['blueg'],tf['blueg'],tf['blueg'],tf['blueg'],tf['blueg'],tf['redg'],tf['redg'],tf['redg'],tf['redg'],tf['redg']]
tf['teamg'] = np.select(conditions, choices)

tf['gold%'] = (tf['teamg']/tf['totalgold'])*100
tf = tf[tf['gold%'] <= 50]
tf['def%'] = 50 - tf['gold%']
tf['def%'] = 2 * tf['def%']
tf['def%'] = tf['def%'].round(1)
tf['def_cat'] = pd.cut(tf['def%'], [0,2.5,5,10,25],
        labels = [1,2,3,4], right = False)
tf[['def_cat']] = tf[['def_cat']].apply(pd.to_numeric)
#tfvlow = tf[tf['lead_cat'] == 'vlowdef']
#tflow = tf[tf['lead_cat'] == 'lowdef']
#tfmid = tf[tf['lead_cat'] == 'middef']
#tfhigh = tf[tf['lead_cat'] == 'highdef']
#tfvhigh = tf[tf['lead_cat'] == 'vhighdef']
tfg = tf.groupby(["champ","def_cat"]).agg({'champ_win':[mean_shrink,'count']}).reset_index()
tfg.columns = ['champion','def','win%','sample size']
tfgluc = tfg[tfg['champion'] == 'Lucian']
tfgez = tfg[tfg['champion'] == 'Ezreal']
tfgkai = tfg[tfg['champion'] == 'KaiSa']
tfgcait = tfg[tfg['champion'] == 'Caitlyn']
#plot the data baby
#lucian graph
import matplotlib.pyplot as plt
plt.xlabel ('Deficit Category')
plt.ylabel ('Win Percentage')
plt.title ('Champion Win Rate Along Deficit Percentage')
plt.grid(True)
plt.ylim(40,65)
plt.xlim(1,4)   
plt.plot(tfgluc['def'], tfgluc['win%'], color= 'Blue',
         label = 'Lucian')
plt.plot(tfgez['def'], tfgez['win%'], color= 'Yellow',
         label = 'Ezreal')
plt.plot(tfgcait['def'], tfgcait['win%'], color= 'green',
         label = 'Cait')
plt.plot(tfgkai['def'], tfgkai['win%'], color= 'Purple',
         label = 'Kaisa')
plt.legend()
plt.show()




























