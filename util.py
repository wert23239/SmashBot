import melee
import random

class Util:

    def __init__(self,logger=None):
        self.x_list=[0,.25,.5,.75,1]
        self.y_list=[0,.25,.5,.75,1]
        BUTTONS=melee.Button
        self.button_list=[BUTTONS.BUTTON_A, BUTTONS.BUTTON_B,
                          BUTTONS.BUTTON_L, BUTTONS.BUTTON_Y,
                          BUTTONS.BUTTON_Z, None]
        self.logger=logger                  

    def do_random_attack(self,controller):
        x_cord=random.choice(self.x_list)
        y_cord=random.choice(self.y_list)
        button_choice=random.choice(self.button_list)
        #print(x_cord,y_cord,button_choice)
        #print(self.convert_attack(x_cord,y_cord,button_choice))
        controller.simple_press(x_cord,y_cord,button_choice)
        if self.logger:
            self.logger.log("Buttons Pressed Converted", self.convert_attack(x_cord,y_cord,button_choice),concat="True")  

    def convert_attack(self,x_cord,y_cord,button_choice):
        x_num=x_cord/.25
        y_num=y_cord/.25
        button_choice=self.button_list.index(button_choice)
        return int(x_num+y_num*5+button_choice*25 ) 