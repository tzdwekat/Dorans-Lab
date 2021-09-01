import pandas as pd
import numpy as np


## PROGRAM PARAMETERS ##
wk_dir = 'C:/Users/tariq/DLAB'
datapath = wk_dir + '/DATA/COMEBACK_DATA/comeback.csv'

#CREATE THE DATA FRAME
df = pd.read_csv(datapath,index_col=0)

#tf = df.groupby(["matchid","timestamp_minute","teamId"]).agg({"totalGold":"sum","win":"max"}).reset_index()
#tf2 = tf.pivot(index=["matchid","timestamp_minute"],columns="teamId",values="totalGold") #,"win"])
#pivot the table with an aggregate function
tf = pd.pivot_table(df,values=["totalGold","win"],
                     index=["matchid","timestamp_minute"],
                     columns="teamId",
                     aggfunc="sum").reset_index()
#rename columns
tf.columns = ["matchid","time","blue_gold","red_gold","blue_win","red_win"]
#Make the data nicer
conditions = [
    (tf['blue_gold'] - tf['red_gold'] )> 0,
    (tf['blue_gold'] - tf['red_gold'] )< 0]
choices = ['blue', 'red']
tf['lead'] = np.select(conditions, choices, default='Neutral')
tf["gold_difference"] = np.abs(tf['blue_gold'] - tf['red_gold'] )
tf['lead_cat'] = pd.cut(tf['gold_difference'], [0,500,1500,2000,500000],
        labels = ['very low','lowlead','midlead','highlead'], right = False)
#Make an 'win_adv' columns where value is 1 if advantaged team wins and 0 otherwise
conditions = [
    (tf['blue_win'] == 5) & (tf['lead'] == 'blue'),
    (tf['blue_win'] == 5) & (tf['lead'] == 'red'),
    (tf['red_win'] == 5) & (tf['lead'] == 'red'),
    (tf['red_win']== 5) & (tf['lead'] == 'blue'),
    ]
choices = [1, 0, 1, 0]
tf['adv_win'] = np.select(conditions, choices, default = np.NaN)
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
#groupby to find a win rate for each minute of the game and each lead category
tf2 = tf.groupby(['time','lead_cat']).agg({'adv_win':[mean_shrink]}).reset_index()
tf2.columns = ['time','lead_cat','adv_winrate']
tfvlow = tf2[tf2['lead_cat'] == 'very low']
tflow = tf2[tf2['lead_cat'] == 'lowlead']
tfmid = tf2[tf2['lead_cat'] == 'midlead']
tfhigh = tf2[tf2['lead_cat'] == 'highlead']
#plot the data
import matplotlib.pyplot as plt
plt.xlabel ('Time (minute)')
plt.ylabel ('Win %')
plt.title ('Win Rate by Time (Based on Gold Lead)')
plt.grid(True)
plt.xlim (0,70)
plt.plot(tfvlow['time'], tfvlow['adv_winrate'], color= 'red',
         label = 'Very Low Lead')
plt.plot(tflow['time'], tflow['adv_winrate'], color= 'blue',
         label = 'Low Lead')
plt.plot(tfmid['time'], tfmid['adv_winrate'], color= 'green',
         label = 'Mid Lead')
plt.plot(tfhigh['time'], tfhigh['adv_winrate'], color= 'gold',
         label = 'High Lead')
plt.legend()
plt.show()
# new definition of gold lead by total gold and percentage of it
tf['game_gold'] = tf['blue_gold'] + tf['red_gold']
tf['blue%'] = (tf['blue_gold']/tf['game_gold'])*100
tf['red%'] = (tf['red_gold']/tf['game_gold'])*100
tf['bdeficit'] = (tf['blue%'])<50
tf['lead%'] = np.where(tf['bdeficit']==False, tf['blue%'], tf['red%'])
tf['lead%'] = tf['lead%'].round(1)
tf['deficit%'] = np.where(tf['bdeficit']==True, tf['blue%'], tf['red%'])
tf['deficit%'] = tf['deficit%'].round(1)
#tf['lead%'] = tf.round({'lead%':1})
tf3 = tf.groupby(['lead%']).agg({'adv_win':[mean_shrink],'lead%':'count'}).reset_index()
tf3.columns = ['lead%','win_rate','sample_size']
#ijdisjbf
conditions = [
    (tf['blue_win'] == 5) & (tf['lead'] == 'blue'),
    (tf['blue_win'] == 5) & (tf['lead'] == 'red'),
    (tf['red_win'] == 5) & (tf['lead'] == 'red'),
    (tf['red_win']== 5) & (tf['lead'] == 'blue'),
    ]
choices = [0, 1, 0, 1]
tf['def_win'] = np.select(conditions, choices, default = np.NaN)

tf4 = tf.groupby(['deficit%']).agg({'def_win':[mean_shrink],'deficit%':'count'}).reset_index()
tf4.columns = ['deficit%','win_rate','sample_size']
tf['def_win'] = (1- tf['adv_win'])

export_csv = tf.to_csv(r'C:\Users\tariq\DLAB\DATA\COMEBACK_DATA\logregdef.csv', index = None, header=True)
#plot to show for leads
fig, ax1 = plt.subplots()
color = 'gold'
ax1.set_xlabel('Percentage of Total Gold')
ax1.set_ylabel('Win Rate', color=color)
ax1.plot(tf3['lead%'], tf3['win_rate'], color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'black'
ax2.set_ylabel('Frequency', color=color)  # we already handled the x-label with ax1
ax2.plot(tf3['lead%'], tf3['sample_size'], color=color)
ax2.tick_params(axis='y', labelcolor=color)
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
#plot to show for deficits
fig, ax1 = plt.subplots()
color = 'cyan'
ax1.set_xlabel('Percentage of Total Gold')
ax1.set_ylabel('Win Rate', color=color)
ax1.plot(tf4['deficit%'], tf4['win_rate'], color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'black'
ax2.set_ylabel('Frequency', color=color)  # we already handled the x-label with ax1
ax2.plot(tf4['deficit%'], tf4['sample_size'], color=color)
ax2.tick_params(axis='y', labelcolor=color)
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
#making a time under deficit label
df2 = df.groupby(by=['matchid','teamId']).agg({'timestamp_minute':'count'}).reset_index()
tfq = tf.merge(df2, how='left', on='matchid')

conditions = [
    (tfq['teamId'] == 100) & (tfq['blue_win'] == 5),
    (tfq['teamId'] == 200) & (tfq['red_win'] == 5),
    (tfq['teamId'] == 100) & (tfq['blue_win'] == 0),
    (tfq['teamId'] == 200) & (tfq['red_win'] == 0),
    ]
choices = [1, 1, 0, 0]
tfq['win'] = np.select(conditions, choices, default = np.NaN)

conditions = [
    (tfq['teamId'] == 100) & (tfq['blue%'] < 50),
    (tfq['teamId'] == 200) & (tfq['red%'] < 50),
    (tfq['teamId'] == 100) & (tfq['blue%'] >= 50),
    (tfq['teamId'] == 100) & (tfq['blue%'] >= 50),
    ]
choices = [1, 1, 0, 0]

tfq['def?'] = np.select(conditions, choices, default = np.NaN)
tfq1 = tfq.groupby(by=['matchid','teamId']).agg({'time':'count','def?':'sum','win':'sum'}).reset_index()
tfq1['%TUD'] = (tfq1['def?'] / tfq1['time']) * 100
tfq1.columns = ['matchid','teamid','time','TUD','win', '% of TUD']
tfq1['win'] = tfq1['win'] / tfq1['time']
tfq1['% of TUD'] = tfq1['% of TUD'].round(1)
export_csv = tfq1.to_csv(r'C:\Users\tariq\DLAB\DATA\COMEBACK_DATA\TUDlogreg.csv', index = None, header=True)
