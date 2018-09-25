import melee
import random
import pandas as pd
import numpy as np
from melee.enums import Action
from keras_pandas.Automater import Automater
from keras.models import model_from_json
class Util:

    def __init__(self,logger=None):
        self.x_list=[0,.25,.5,.75,1]
        self.y_list=[0,.25,.5,.75,1]
        BUTTONS=melee.Button
        self.button_list=[BUTTONS.BUTTON_A, BUTTONS.BUTTON_B,
                          BUTTONS.BUTTON_L, BUTTONS.BUTTON_Y,
                          BUTTONS.BUTTON_Z, None]
        self.logger=logger     
        self.categorical_vars=["Opponent_Facing","AI_Facing","target"] 
        self.numerical_vars=["Frame","Opponent_x","Opponent_y","AI_x","AI_y",
                "Opponent_Action_Num","AI_Action_Num","AI_Action_Frame",
                "Opponent_Action_Frame","Opponent_Jumps_Left", "AI_Jumps_Left",
                "Opponent_Stock","AI_Stock",
                "Opponent_Percent","AI_Percent","Buttons_Pressed_Converted"]
        self.model=[]
        self.create_model()
        
    def create_model(self):
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        self.model.load_weights("my_model_weights.h5")


    def do_random_attack(self,controller):
        x_cord=random.choice(self.x_list)
        y_cord=random.choice(self.y_list)
        button_choice=random.choice(self.button_list)
        controller.simple_press(x_cord,y_cord,button_choice)
        if self.logger:
            self.logger.log("Buttons_Pressed_Converted", self.convert_attack(x_cord,y_cord,button_choice),concat="True")  

    def do_model_attack(self,controller,gamestate):
        processed_input,processed_action = self.preprocess_input(gamestate)
        action_values=self.model.predict([processed_input,processed_action])
        action=np.argmax(action_values)
        print(action)
        x_cord,y_cord,button_choice=self.unconvert_attack(action)
        controller.simple_press(x_cord,y_cord,button_choice)
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
        y_cord=action//5*.25
        action=action%5
        x_cord=action//5*.25
        return x_cord,y_cord,self.button_list[button_choice]  

    def preprocess_input(self,gamestate):
        ai_state = gamestate.ai_state
        opponent_state = gamestate.opponent_state
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
        #df=df_test.append([df_test.head(1)]*149,ignore_index=True)
        # # Change to all actions
        # df['Buttons_Pressed_Converted'] = df.apply (lambda row:row.name,axis=1)
        #return 0
        return result,np.array(range(149))