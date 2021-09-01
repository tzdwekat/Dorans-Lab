# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 19:59:52 2019

@author: tariq
"""
import pandas as pd
import numpy as np
import math
from sqlalchemy import create_engine

## PROGRAM PARAMETERS ##
wk_dir = 'C:/Users/tariq/DLAB'
datapath = wk_dir + '/DATA/COMEBACK_DATA/comeback.csv'
db_str = 'mysql+pymysql://LOLread:LaberLabsLOLquery'+'@lolsql.stat.ncsu.edu/lol2019'

#CREATE THE DATA FRAME
dfg = pd.read_csv(datapath)
#make team gold rather than an individuals gold
tg = dfg.groupby(by=['matchid','teamId','timestamp_minute']).agg({'totalGold':'sum'}).reset_index()
tg = tg.rename(columns={'totalGold':'teamGold'})
dfg = dfg.merge(tg, how = 'left', on=['matchid','teamId','timestamp_minute'])
#make gold difference 
BTG_subset=dfg[dfg['teamId']==100]
RTG_subset=dfg[dfg['teamId']==200]
reshapeB = BTG_subset.reset_index().pivot_table( index ='matchid',columns ='timestamp_minute',values ='teamGold')
reshapeR = RTG_subset.reset_index().pivot_table( index ='matchid',columns ='timestamp_minute',values ='teamGold')
golddiff = reshapeB - reshapeR
golddiff = golddiff.reset_index()
golddiffmelted = golddiff.melt(id_vars = ['matchid'])
golddiffmelted = golddiffmelted.rename(columns={'value':'tgolddiff'})
#merge the gold diff value back onto dfg
dfg = dfg.merge(golddiffmelted, how ='left', on=['matchid','timestamp_minute'])
#EDAtual game we want
EDAsub = dfg[dfg['matchid']== 2943759795
]
EDAsub = EDAsub[EDAsub['participantid']==1]
EDAsub = EDAsub.drop('Unnamed: 0', 1)
#Variance Subset
#EDAsubv = EDAsub.groupby(by=['timestamp_minute','matchid','teamId']).agg({'tgolddiff':'var'}).reset_index()
#EDAsubv = EDAsubv.rename(columns={'tgolddiff':'Gold Diff Variance'})
EDAsubv = EDAsub.var()  
EDAsublist = ['tgolddiff']
EDAsubv = EDAsubv.loc[EDAsublist]
#function to make a changing limit to make data more readable 
EDAsub['abs'] = EDAsub['tgolddiff'].abs()
bound = max(EDAsub['abs'])
def round_up(n, decimals=0): 
    multiplier = 10 ** decimals 
    return math.ceil(n * multiplier) / multiplier
bound = round_up(bound, -3)
bound = bound +1000
tbound = max(EDAsub['timestamp_minute'])
tbound = tbound + 1
#graphing gold diff vs time
import matplotlib.pyplot as plt
plt.xlabel ('Time (minute)')
plt.ylabel ('Gold Difference')
plt.title ('Gold Difference VS Time Graph')
plt.ylim (-bound,bound)
plt.xlim (0, tbound )
plt.grid(True)
plt.plot(EDAsub['timestamp_minute'], EDAsub['tgolddiff'], color= 'blue' if EDAsub['win'].iat[0] else 'red',
         label = 'gold difference')
plt.legend()
plt.show()
#print the variance of the data
print (EDAsubv)
#Make an algorithim that estimates that a team will win if it is more ahead at a certain time
#based on this algorithim make a graph that measures how accurate this prediction is for all the times we use 
##Negative values means red team has an advantage positive values means blue team has an advantage
conditions = [
    (dfg['win'] == 1) & (dfg['tgolddiff'] >= 1000) & (dfg['teamId'] == 100),
    (dfg['win'] == 0) & (dfg['tgolddiff'] <= 1000) & (dfg['teamId'] == 100),
    (dfg['win'] == 0) & (dfg['tgolddiff'] >= -1000) & (dfg['teamId'] == 200),
    (dfg['win'] == 1) & (dfg['tgolddiff'] <= -1000) & (dfg['teamId'] == 200),
    (dfg['tgolddiff'] == 0)
    ]
choices = ['Correct', 'Correct', 'Correct', 'Correct', 'Not Predictable']
dfg['win predictor'] = np.select(conditions, choices, default='Wrong')
#now we have a row that tells us whether our predictor was wrong or right we want to quantify how often that prediction is right
#make a subset with only one data thing so you can assess it more easily
pids = [1,6]
goldlead = dfg[dfg.participantid.isin(pids)]
confsub1 = dfg[dfg['participantid']== 1]

confsubtable = confsub1[['timestamp_minute','win predictor','matchid']]

confsubtable.replace({'win predictor':{'Not Predictable' : np.NaN, 'Wrong' : int(0), 'Correct' : int(1)}}, inplace = True)
#confsubtable.drop(columns=['Index'])
confsubtable1 = confsubtable.pivot(index=('matchid'), columns='timestamp_minute', values='win predictor')
#Getting a total for each column 
summarydata = pd.DataFrame()
summarydata['Sum'] = confsubtable1.sum(axis=0, skipna = True)
summarydata['Count'] = confsubtable1.count(axis=0)
summarydata['Percentage'] = (summarydata['Sum']/summarydata['Count'])*100
summarydata['sample mean'] = summarydata['Sum']/summarydata['Count']
summarydata['error'] = summarydata['Count'] - summarydata['Sum'] 
summarydata['error'] = (summarydata['error'] / summarydata['Count']) * 100
summarydata.reset_index(inplace = True)
#Find the confidence Interval
#use a 0.95 confidence interval so z = 1.96, count = sample size, error = error, and accuracy = percentage 
summarydata['interval'] = 1.96 * (( (summarydata['error'] * (100 - (summarydata['error'])) ) / summarydata['Count'] )**0.5)
summarydata['linterval'] = summarydata['Percentage'] - summarydata['interval']
summarydata['uinterval'] = summarydata['Percentage']  + summarydata['interval']




#create a graph with the percentage correct and the 
plt.xlabel ('Time (minute)')
plt.ylabel ('Percent Correct')
plt.title ('What is the best time?')
plt.ylim (45,95)
plt.xlim (5,30)
plt.grid (True)
plt.plot(summarydata['timestamp_minute'], summarydata['Percentage'], color = 'blue', 
         label = 'Percentage')
plt.plot(summarydata['timestamp_minute'], summarydata['linterval'], color = 'red', 
         label = 'Confidence Interval')
plt.plot(summarydata['timestamp_minute'], summarydata['uinterval'], color = 'red')
plt.legend()
plt.show()
#with this data 12 seemes to be the best time
#lets try finding the best time at a certain win-rate
#gold lead per time vs percentage
goldlead['absolute difference'] = goldlead['tgolddiff'].abs().astype(int)
#confsub1['Team Lead'] = np.where(confsub1['tgolddiff'] < 0, 'Blue', 'Red')
conditions = [
    (goldlead['tgolddiff']  > 0) ,
    (goldlead['tgolddiff'] < 0) ,
    (goldlead['tgolddiff'] == 0)
    ]
choices = ['Blue', 'Red', 'Neutral']
goldlead['Team Lead'] = np.select(conditions, choices, default= 'impossible')
#categorize gold leads
goldlead['glc'] = pd.cut(goldlead['absolute difference'], [0,500,1500,2000,500000],
        labels = ['very low','lowlead','midlead','highlead'], right = False)
#subset the data for win sums per minute
gwinp = goldlead.groupby(['timestamp_minute','glc']).agg({'win':['sum','mean','count']}).reset_index()




#cool = dfg.groupby(by=['timestamp_minute','teamId']).agg({'tgolddiff':'mean'}).reset_index()






