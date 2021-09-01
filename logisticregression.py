import pandas as pd
import numpy as np


## PROGRAM PARAMETERS ##
wk_dir = 'C:/Users/tariq/DLAB'
datapath = wk_dir + '/DATA/COMEBACK_DATA/comeback.csv'
datapath2 = wk_dir + '/DATA/COMEBACK_DATA/logregdef.csv'
datapath3 = wk_dir +'/DATA/COMEBACK_DATA/TUDlogreg.csv'
#CREATE THE DATA FRAME
df = pd.read_csv(datapath,index_col=0)
df1 = pd.read_csv(datapath2,index_col=0)
sf = pd.read_csv(datapath3,index_col=0)

df1 = df1.loc[:,["time","def_win","deficit%"]].dropna()
dfxnp = df1.loc[:,["time","deficit%"]]
dfynp = df1.loc[:,["def_win"]]
dfnp = df1.to_numpy()
sf1 =  sf.groupby(by=['% of TUD']).agg({'win':'sum'}).reset_index()
#
#import matplotlib.pyplot as plt
#plt
#plt.bar(df1[df1(deficit%)],df1[df1(def_win)], Label = "test", color ="b")
#plt.legend()
#plt.xlabel('def percent')
#plt.ylabel('win freq')
#plt.title



from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

x_train, x_test, y_train, y_test = train_test_split(df1[['deficit%']],df1.def_win,test_size=0.9)

model = LogisticRegression()
model.fit(x_train, y_train)

predictions = model.predict(x_test)


score = model.score(x_test, y_test)
print(score)
matrix = confusion_matrix(y_test,predictions)
print(matrix)

xlin = np.linspace(30,50)[:,np.newaxis]
probs = model.predict_proba(xlin)

import matplotlib.pyplot as plt
plt.xlabel ('Percentage of Total Gold')
plt.ylabel ('Win Probability')
plt.title ('Model Test')
plt.grid(True)
plt.xlim (30,50)
plt.ylim (0,1)
plt.plot(xlin, probs[:,1], color= 'green',
         label = 'yes')
plt.legend()
plt.show()

x1_train, x1_test, y1_train, y1_test = train_test_split(dfxnp,dfynp,test_size=0.9)
model1 = LogisticRegression()
model1.fit(x1_train, y1_train)

predictions1 = model1.predict(x1_test)


score1 = model1.score(x1_test, y1_test)
print(score1)
matrix1 = confusion_matrix(y1_test,predictions1)
print(matrix1)

#Ridge regression








