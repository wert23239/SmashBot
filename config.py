import random

from melee import Button
from enum import Enum, unique
from numpy import argmax
@unique
class ModelType(Enum):
    RANDOM = 0
    BINARY = 1
    REGRESSION = 2

MODEL_PREFIX="Models/"
JSON_SUFFIX=".json"
WEIGHTS_SUFFIX=".h5"

class Config():

    def __init__(self,model_file_name,model_type=ModelType.RANDOM):
        self.model_stucture=MODEL_PREFIX+model_file_name+JSON_SUFFIX
        self.model_weights=MODEL_PREFIX+model_file_name+WEIGHTS_SUFFIX
        if model_type==ModelType.RANDOM:
            self.model_predict=self.random_attack
        elif model_type==ModelType.BINARY:
            self.model_predict=self.binary_attack

    def random_attack(self, *unused):
        action=random.randint(0,149)
        return action

    def binary_attack(self,model,processed_input,processed_action):
        action_values=model.predict([processed_input,processed_action])
        action=argmax(action_values)
        return action
