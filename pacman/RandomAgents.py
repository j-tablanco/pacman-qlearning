__author__ = "Aprendizaje Automatico"
__copyright__ = "Copyright 2016, Planning and Learning Group"
__version__ = "1.0.1"

from game import Agent
from game import Directions
from game import GameStateData
import random
import sys

class RandomAgent(Agent):
    """
    Random Agent
    """
    def __init__( self, index = 0 ):

        self.lastMove = Directions.STOP
        self.index = index

    def getAction( self, state):
        legal = state.getLegalActions(self.index)
        move = self.getMove(legal)

        if move == Directions.STOP:
            # Try to move in the same direction as before
            if self.lastMove in legal:
                move = self.lastMove


        if move not in legal:
            move = random.choice(legal)

        self.lastMove = move

        return move

    def getMove(self, legal):
        move = Directions.STOP
        move_random = random.randint(0, 3)
        if   ( move_random == 0) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
