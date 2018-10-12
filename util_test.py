import unittest
import melee
from melee.enums import Action
import util
import logger
class UtilTest(unittest.TestCase):
   
    def test_util_convert(self):
        utils=util.Util(logger=None)
        expected=0
        for i in range(len(utils.button_list)):
            for j in range(len(utils.y_list)):
                for k in range(len(utils.x_list)):
                    result = (
                        utils.convert_attack(utils.x_list[k],utils.y_list[j],utils.button_list[i]))
                    self.assertEqual(result, expected)
                    expected+=1    
    def test_util_unconvert(self):
        utils=util.Util(logger=None)
        x_cord,y_cord,button_choice=utils.unconvert_attack(4)
        self.assertEqual(x_cord,1)
        self.assertEqual(y_cord,0)
        self.assertEqual(button_choice,melee.Button.BUTTON_A)
        x_cord,y_cord,button_choice=utils.unconvert_attack(5)
        self.assertEqual(x_cord,0)
        self.assertEqual(y_cord,.25)
        self.assertEqual(button_choice,melee.Button.BUTTON_A)
        x_cord,y_cord,button_choice=utils.unconvert_attack(26)
        self.assertEqual(x_cord,.25)
        self.assertEqual(y_cord,0)
        self.assertEqual(button_choice,melee.Button.BUTTON_B)  

    def create_fake_row(self):
        return dict({
        "Frame":1,
        "Opponent_x":-70.0,
        "Opponent_y":7.0,
        "AI_x":70.0,
        "AI_y":7.0,
        "Opponent_Facing":True,
        "AI_Facing":False,
        "Opponent_Action":Action.ENTRY,
        "Opponent_Action_Num":322,
        "AI_Action":Action.ENTRY,
        "AI_Action_Num":322,
        "Opponent_Action_Frame":-1,
        "AI_Action_Frame":-1,
        "Opponent_Jumps_Left":1,
        "AI_Jumps_Left":1,
        "Opponent_Stock":4,
        "AI_Stock":4,
        "Opponent_Percent":0,
        "AI_Percent":0,
        "Opponent_Percent_Change":0,
        "AI_Percent_Change":0,
        "Opponent_Stock_Change":0,
        "AI_Stock_Change":0,
        "Buttons Pressed":0,
        "Buttons_Pressed_Converted":107})

    def test_preprocess_rows_size(self):
        utils=util.Util(logger=None)
        reward_row=self.create_fake_row()
        reward_row["AI_Stock_Change"]=-1
        rows = [self.create_fake_row(),self.create_fake_row(),self.create_fake_row(),reward_row]
        Y_train,X_train,action_train=utils.preprocess_rows(rows)
        print(X_train)
        print(Y_train)
        self.assertEqual(3,len(Y_train))
        self.assertEqual(Y_train[0],-.99**2)
        self.assertEqual(Y_train[1],-.99)
        self.assertEqual(Y_train[2],-1)
        self.assertEqual(len(X_train[0]),17)

if __name__ == '__main__':
    unittest.main()