import melee
import pandas as pd
import numpy as np
import random
import objgraph
from melee import Button
from melee.enums import Action
from keras_pandas.Automater import Automater
from keras.models import model_from_json
class Util:

    def __init__(self,logger=None,controller=None,config=None):
        self.x_list=[0,.25,.5,.75,1]
        self.y_list=[0,.25,.5,.75,1]
        self.button_list=[None, Button.BUTTON_B,
                          Button.BUTTON_L, Button.BUTTON_Y,
                          Button.BUTTON_Z, Button.BUTTON_A]
        self.logger=logger     
        self.controller=controller
        self.startE=1
        self.endE=.01
        self.e=1.0
        self.config=config
        if config:
            self.create_model()
       
        
    def create_model(self):
        json_file = open(self.config.model_stucture, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        self.model.compile(optimizer="Adam", loss='mae')
        #self.model.load_weights(self.config.model_weights)

    def do_attack(self,gamestate,ai_state,opponent_state):
        processed_input,processed_action = (
            self.preprocess_input(gamestate,ai_state,opponent_state))

        if np.random.rand(1) < self.e:
            action=random.randint(0,149)
        else:
            action=self.config.model_predict(self.model,processed_input,processed_action)
       
        x_cord,y_cord,button_choice=self.unconvert_attack(action)

        self.controller.simple_press(x_cord,y_cord,button_choice)
        if self.logger:
            self.logger.log("Buttons_Pressed_Converted", self.convert_attack(x_cord,y_cord,button_choice),concat="True")          

    def convert_attack(self,x_cord,y_cord,button_choice):
        x_num=x_cord/.25
        y_num=y_cord/.25
        button_choice=self.button_list.index(button_choice)
        return int(x_num+y_num*5+button_choice*25 ) 

    def unconvert_attack(self,action):
        button_choice=action//25
        action=action%25
        y_cord=action//5
        action=action%5
        x_cord=action
        return self.x_list[x_cord],self.y_list[y_cord],self.button_list[button_choice]  
    
    def train(self,rows):
        Y_train,X_train,action_train=self.preprocess_rows(rows)
        history=self.model.fit([X_train,action_train], Y_train,batch_size=32, epochs=10,validation_split=.2,verbose=0)
        if self.e>self.endE:
            self.e=self.e-.005
        return history.history['val_loss'][-1]

    def preprocess_rows(self,rows):
        df=pd.DataFrame.from_dict(rows)
        df["Opponent_Percent_Change"] = df["Opponent_Percent_Change"].shift(-1)
        df["AI_Percent_Change"] = df["AI_Percent_Change"].shift(-1)
        df["Opponent_Stock_Change"] = df["Opponent_Stock_Change"].shift(-1)
        df["AI_Stock_Change"] = df["AI_Stock_Change"].shift(-1)
        df.drop(len(df)-1,inplace=True)

        #reward
        df['target'] = df.apply (lambda row: (int(row["AI_Percent_Change"])>0)*-.1+(int(row["AI_Stock_Change"])<0)*-1,axis=1)
        
        df[["Opponent_Facing", "AI_Facing","target"]] *= 1
        discount_factor=.99
        current_reward=0
        df=df.drop(columns=['AI_Action', 'Opponent_Action', 
                            'Buttons Pressed', 'Opponent_Percent_Change',
                            'AI_Percent_Change',"AI_Stock_Change","Opponent_Stock_Change"])
        reward_avg=0
        reward_min=0
        for i in reversed(df.index):
            df.loc[i,"target"]=df.loc[i,"target"]+discount_factor*current_reward
            current_reward=df.loc[i,"target"]
            reward_avg+=current_reward
            reward_min=min(reward_min,current_reward)
        print("Reward Average: ",reward_avg/len(df))
        print("Min Reward: ",reward_min)
        Y_train=df['target'].astype(float).values
        X_train=df[df.columns.difference(['target', 'Buttons_Pressed_Converted'])].astype(float).values
        action_train=df['Buttons_Pressed_Converted'].astype(int).values    
        return Y_train,X_train,action_train


    def preprocess_input(self,gamestate,ai_state,opponent_state):
        df= pd.DataFrame({
            'Frame':[gamestate.frame],
            'Opponent_x':[(opponent_state.x)],
            'Opponent_y':[(opponent_state.y)],
            'AI_x' : [(ai_state.x)],
            'AI_y' : [(ai_state.y)],
            'Opponent_Facing' : [(opponent_state.facing)],
            'AI_Facing' : [(ai_state.facing)],
            'Opponent_Action_Num' : [(Action(opponent_state.action).value)],
            'AI_Action_Num' : [(Action(ai_state.action).value)],
            'Opponent_Action_Frame' : [(opponent_state.action_frame)],
            'AI_Action_Frame' : [(ai_state.action_frame)],
            'Opponent_Jumps_Left' : [(opponent_state.jumps_left)],
            'AI_Jumps_Left' : [(ai_state.jumps_left)],
            'Opponent_Stock' : [(opponent_state.stock)],
            'AI_Stock' : [(ai_state.stock)],
            'Opponent_Percent' : [(opponent_state.percent)],
            'AI_Percent' : [(ai_state.percent)]          
            })
        df[["Opponent_Facing", "AI_Facing"]] *= 1
        df_test=df.head(1)
        result=df.head(1).astype(float).values
        result=np.tile(result,(149,1))
        return result,np.array(range(149))