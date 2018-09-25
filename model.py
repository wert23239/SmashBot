import matplotlib
from keras import Model
from keras.layers import Dense
from keras_pandas.Automater import Automater
from keras import backend as K
import functools
import pandas
import pandas_ml as pdml
import tensorflow as tf



df=pandas.read_csv('Logs/stats.csv')
df["Opponent_Percent_Change"] = df["Opponent_Percent_Change"].shift(-1)
df["AI_Percent_Change"] = df["AI_Percent_Change"].shift(-1)
df.drop(len(df)-1,inplace=True)
df['.target'] = df.apply (lambda row: row["Opponent_Percent_Change"]>0,axis=1)
print(len(df[(df['.target'] > 0)]),len(df))
df=df.drop(columns=['AI_Action', 'Opponent_Action', 'Buttons Pressed'])
pdf=pdml.ModelFrame(df.to_dict(orient='list'),target='.target')
pdf.Da
sampler= pdf.imbalance.under_sampling.ClusterCentroids() 
sampled = pdf.fit_sample(sampler)