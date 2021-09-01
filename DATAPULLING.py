# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 19:23:50 2019

@author: tariq
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

## PROGRAM PARAMETERS ##
wk_dir = 'C:\\Users\\tariq\\DLAB\\'
db_str = 'mysql+pymysql://LOLread:LaberLabsLOLquery'+'@lolsql.stat.ncsu.edu/lol2019'
datapath = wk_dir + '\\DELIVERABLES\\PULLING DATA TEXT FILE\\pulldata.txt\\'

## FUNCTIONS ##
def query_to_df(datapath ,engine,rep_games=0): # filepath of text file that contains query
    with open(datapath) as f:
        query_str = f.read()
    if rep_games != 0:
        query_str=query_str.replace('1234',str(100))
    print(datapath)
    return pd.read_sql(query_str,engine) # returns a dataframe

## BODY ##
engine = create_engine(db_str)
df = query_to_df(wk_dir+'DELIVERABLES\\'+ 'PULLING DATA TEXT FILE\\' + 'pulldata.txt',engine)

df.to_csv(wk_dir+'Data\\'+ 'COMEBACK_DATA\\' + 'comeback.csv')