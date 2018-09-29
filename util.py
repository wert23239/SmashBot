import melee
import pandas as pd
import numpy as np
from melee import Button
from melee.enums import Action
from keras_pandas.Automater import Automater
from keras.models import model_from_json
class Util:

    def __init__(self,logger=None,controller=None,config=None):
        self.x_list=[0,.25,.5,.75,1]
        self.y_list=[0,.25,.5,.75,1]
        self.button_list=[Button.BUTTON_A, Button.BUTTON_B,
                          Button.BUTTON_L, Button.BUTTON_Y,
                          Button.BUTTON_Z, None]
        self.logger=logger     
        self.controller=controller
        self.config=config
        self.create_model()
       
        
    def create_model(self):
        json_file = open(self.config.model_stucture, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        print(self.model.get_weights()[0][0][0::3])
        self.model.load_weights(self.config.model_weights)
        print(self.model.get_weights()[0][0][0::3])

    def do_attack(self,gamestate,ai_state,opponent_state):
        processed_input,processed_action = (
            self.preprocess_input(gamestate,ai_state,opponent_state))
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