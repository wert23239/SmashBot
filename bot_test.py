import unittest
import melee
import util
import logger
class MyTest(unittest.TestCase):
   
    def test_util(self):
        utils=util.Util(logger=None)
        expected=0
        for i in range(len(utils.button_list)):
            for j in range(len(utils.y_list)):
                for k in range(len(utils.x_list)):
                    result = (
                        utils.convert_attack(utils.x_list[k],utils.y_list[j],utils.button_list[i]))
                    self.assertEqual(result, expected)
                    expected+=1    

if __name__ == '__main__':
    unittest.main()