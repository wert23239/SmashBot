from keras import backend as K
from keras import Model
from keras.layers import Dense,Input,concatenate
from keras.utils import to_categorical
from keras.optimizers import SGD
from  sklearn.utils import resample
import functools
import pandas
import tensorflow as tf
import numpy as np


def main():
    linear=True
    df=preprocess(linear)
    # fix session
    sess = tf.Session()
    with sess.as_default():
        seed = 7
        np.random.seed(seed)
        if linear:
            linear_model(df)


def preprocess(linear):
    df=pandas.read_csv('Logs/stats_test.csv')
    df["Opponent_Percent_Change"] = df["Opponent_Percent_Change"].shift(-1)
    df["AI_Percent_Change"] = df["AI_Percent_Change"].shift(-1)
    df.drop(len(df)-1,inplace=True)
    df=df.drop(columns=['AI_Action', 'Opponent_Action', 'Buttons Pressed', 'Notes', 'Frame Process Time'])
    df[["Opponent_Facing", "AI_Facing"]] *= 1
    if linear:
        df['target'] = df.apply (lambda row: row["Opponent_Percent_Change"]>0,axis=1)
        df=df.drop(columns=['Opponent_Percent_Change','AI_Percent_Change'])
        df_majority = df[df.target==False]
        df_minority = df[df.target==True]
        #print(df_majority)
        #print(len(df_majority),len(df_minority))
        df_majority_downsampled = resample(df_majority, 
                                    replace=False,    # sample without replacement
                                    n_samples=int(len(df_minority)*1.2),     # to match minority class
                                    random_state=123) # reproducible results
        df = pandas.concat([df_majority_downsampled, df_minority]).sample(frac=1)
        df.reset_index(drop=True,inplace=True)
        df[["target"]] *= 1
    return df    

def linear_model(df):
    Y_train=df['target'].astype(int).values
    X_train=df[df.columns.difference(['target', 'Buttons_Pressed_Converted'])].astype(float).values
    action_train=df['Buttons_Pressed_Converted'].astype(int).values
    # Input layer
    inputs = Input(shape=(17,))
    action = Input(shape=(1,))
    input_and_actions= concatenate([inputs,action])
    x = Dense(32, activation='relu')(input_and_actions)
    x = Dense(8, activation='relu')(x)
    x = Dense(1, kernel_initializer='normal', activation='sigmoid')(x)
    model = Model(inputs=[inputs,action], outputs=x)
    precision = as_keras_metric(tf.metrics.precision)
    recall = as_keras_metric(tf.metrics.recall)
    model.compile(optimizer="Adam", loss='binary_crossentropy', metrics=['accuracy',precision,recall])
    # Train model
    history=model.fit([X_train,action_train], Y_train, epochs=3,validation_split=.2,verbose=1)
    json_string = model.to_json()
    with open("model_fake.json", "w") as json_file:
        json_file.write(json_string)
        model.save_weights('model_fake.h5')  


def as_keras_metric(method):
    @functools.wraps(method)
    def wrapper(self, args, **kwargs):
        """ Wrapper for turning tensorflow metrics into keras metrics """
        value, update_op = method(self, args, **kwargs)
        K.get_session().run(tf.local_variables_initializer())
        with tf.control_dependencies([update_op]):
            value = tf.identity(value)
        return value
    return wrapper

if __name__ == '__main__':
    main()