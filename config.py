import random

from melee import Button
from enum import Enum, unique
from numpy import argmax
@unique
class ModelType(Enum):
    RANDOM = 0
    BINARY = 1
    REGRESSION = 2


class Config():

    def __init__(self,model_stucture=None,model_weights=None,model_type=ModelType.RANDOM):
        self.model_stucture=model_stucture
        self.model_weights=model_weights
        if model_type==ModelType.RANDOM:
            self.model_predict=self.random_attack
        elif model_type==ModelType.BINARY:
            self.model_predict=self.binary_attack

    def random_attack(self, *unused):
        action=random.randint(0,149)
        return action

    def binary_attack(self,model,processed_input,processed_action):
        print(model.get_weights()[0][0][0::3])
        action_values=model.predict([processed_input,processed_action])
        action=argmax(action_values)
        return action
