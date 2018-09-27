import unittest
import melee
import util
import logger
class MyTest(unittest.TestCase):
   
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
if __name__ == '__main__':
    unittest.main()