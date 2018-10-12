import csv
import time
import datetime
import os
from melee.enums import Action,Menu

class Logger:
    def __init__(self):
        timestamp = datetime.datetime.fromtimestamp(time.time())
        #Create the Pipes directory if it doesn't already exist
        if not os.path.exists("Logs/"):
            os.makedirs("Logs/")
        #self.csvfile = open('Logs/' + str(timestamp) + '.csv', 'w')
        self.csvfile = open('Logs/stats_test.csv', 'w')
        fieldnames = ['Frame', 'Opponent_x',
            'Opponent_y', 'AI_x', 'AI_y', 'Opponent_Facing', 'AI_Facing',
            'Opponent_Action','Opponent_Action_Num' ,'AI_Action','AI_Action_Num', 
            'Opponent_Action_Frame', 'AI_Action_Frame','Opponent_Jumps_Left', 'AI_Jumps_Left', 
            'Opponent_Stock', 'AI_Stock','Opponent_Percent', 'AI_Percent', 
            'Opponent_Percent_Change', 'AI_Percent_Change','Opponent_Stock_Change', 'AI_Stock_Change', 
            'Buttons Pressed', 'Buttons_Pressed_Converted' ,'Notes', 'Frame Process Time']
        self.writer = csv.DictWriter(self.csvfile, fieldnames=fieldnames, extrasaction='ignore')
        self.current_row = dict()
        self.rows = []
        self.filename = self.csvfile.name
        self.action_map= self.create_action_map()
        self.write_log_initial()
        # These needed to be shifted up 1
        self.past_opponent_percent=0
        self.past_ai_percent=0
        self.past_opponent_stock=0
        self.past_ai_stock=0

    def log(self, column, contents, concat=False):
        #Should subsequent logs be cumulative?
        if concat:
            if column in self.current_row:
                self.current_row[column] += contents
            else:
                self.current_row[column] = contents
        else:
            self.current_row[column] = contents

    #Log any common per-frame items
    def log_frame(self, gamestate):
        if gamestate.menu_state not in [Menu.IN_GAME, Menu.SUDDEN_DEATH]:
            self.past_opponent_percent = 0
            self.past_ai_percent = 0
            self.past_opponent_stock = 3
            self.past_ai_stock = 3
        ai_state = gamestate.ai_state
        opponent_state = gamestate.opponent_state

        self.log('Frame', gamestate.frame)
        self.log('Opponent_x', str(opponent_state.x))
        self.log('Opponent_y', str(opponent_state.y))
        self.log('AI_x', str(ai_state.x))
        self.log('AI_y', str(ai_state.y))
        self.log('Opponent_Facing', opponent_state.facing)
        self.log('AI_Facing', ai_state.facing)
        self.log('Opponent_Action', str(opponent_state.action))
        self.log('Opponent_Action_Num', str(Action(opponent_state.action).value))
        self.log('AI_Action', str(ai_state.action))
        self.log('AI_Action_Num', str(Action(ai_state.action).value))
        self.log('Opponent_Action_Frame', str(opponent_state.action_frame))
        self.log('AI_Action_Frame', str(ai_state.action_frame))
        self.log('Opponent_Jumps_Left', str(opponent_state.jumps_left))
        self.log('AI_Jumps_Left', str(ai_state.jumps_left))
        self.log('Opponent_Stock', str(opponent_state.stock))
        self.log('AI_Stock', str(ai_state.stock))
        self.log('Opponent_Percent', str(opponent_state.percent))
        self.log('AI_Percent', str(ai_state.percent))
        self.log('Opponent_Percent_Change', str(opponent_state.percent-self.past_opponent_percent))
        self.log('AI_Percent_Change', str(ai_state.percent-self.past_ai_percent))
        self.log('Opponent_Stock_Change', opponent_state.stock-self.past_opponent_stock)
        self.log('AI_Stock_Change', ai_state.stock-self.past_ai_stock)
        self.past_opponent_percent=opponent_state.percent
        self.past_ai_percent=ai_state.percent
        self.past_opponent_stock=opponent_state.stock
        self.past_ai_stock=ai_state.stock

    def write_frame(self):
        self.rows.append(self.current_row)
        self.current_row = dict()

    def write_log_initial(self):
        self.writer.writeheader()

    def write_log(self):
        self.writer.writerows(self.rows)

    def create_action_map(self):
        action_map={}
        for name, _ in Action.__members__.items():
            if "DEAD" in name:
                action_map["DEAD"]=name
            elif "WALK" in name:
                action_map["MOVE"]=name   
            elif ("ITEM" in name or "NESS" in name or 
                  "FOX" in name or "THROWN" in name or
                 "BEAM" in name or "DAMAGE" in name or
                 "TECH" in name):
                action_map["VOID"]=name    
            elif ("FSMASH" in name or 
                  "FAIR" in name or 
                  "FTILT" in name or 
                  "NEUTRAL_ATTACK_2" in name):
                action_map["FOWARD_A"] = name
            elif ("BSMASH" in name or 
                  "BAIR" in name or 
                  "BTILT" in name or
                  "NEUTRAL_ATTACK_3" in name):    
                action_map["BACK_A"] = name
            elif "NAIR" in name or "NEUTRAL_ATTACK_1" in name:
                action_map["NEUTRAL_A"] = name
            elif "UPSMASH" in name or "UPTILT" in name:
                action_map["UP_A"] = name
            elif "NEUTRAL_B" in name:
                action_map["NETURAL_B"]=name    
            elif "DOWN_B" in name:
                action_map["DOWN_B"]=name   
            elif "UP_B" in name:
                action_map["UP_B"]=name   
            elif "SWORD_DANCE" in name:
                action_map["SWORD_DANCE"]=name    
            elif "THROW_" in name:
                action_map[name] = name
            elif "SHIELD" in name:
                action_map["SHEILD"] = name
            elif "DODGE" in name:
                action_map["DODGE"] = name
            elif "EDGE" in name:
                action_map["EDGE"] = name
            elif "JUMP" in name:
                action_map["JUMP"] = name
            else:
                action_map[name]=name
        return action_map    


