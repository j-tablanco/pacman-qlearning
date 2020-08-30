# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters
import os
from wekaI import Weka

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs

class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        '''self.weka = Weka()
        self.weka.start_jvm()'''


    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):

    "An agent controlled by the keyboard that displays beliefs about ghost positions."
    index = 0
    line = []

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):

        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)
        line = [None]


    def getAction(self, gameState):
    	self.getLineData('../keyboar.arff',gameState,BustersAgent.getAction(self, gameState))

        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

    def printLineData(self):
        return self.line

    def getLineData(self,file,gameState,action):
        val, idx = min((val, idx) for (idx, val) in enumerate(gameState.data.ghostDistances) if val != None)
        width, height = gameState.data.layout.width, gameState.data.layout.height
        legal = [None, None, None, None, None]
        self.line = []
        #West, Stop, East, North, South

       	if 'West' in gameState.getLegalPacmanActions():
       		legal [0] = 'West'
       	if 'Stop' in gameState.getLegalPacmanActions():
       		legal [1] = 'Stop'
       	if 'East' in gameState.getLegalPacmanActions():
       		legal [2] = 'East'
       	if 'North' in gameState.getLegalPacmanActions():
       		legal [3] = 'North'
       	if 'South' in gameState.getLegalPacmanActions():
       		legal [4] = 'South'

        distances = [i if i is not None else 0 for i in gameState.data.ghostDistances ]

        self.line.append(str(width))
        self.line.append(str(height))
        self.line.append(str(gameState.getPacmanPosition()[0]))
        self.line.append(str(gameState.getPacmanPosition()[1]))
        self.line.extend(legal)
        self.line.append(gameState.data.agentStates[0].getDirection())
        self.line.append(str(gameState.getNumAgents() - 1))
        self.line.extend(map(str,gameState.getLivingGhosts()))
        self.line.extend(map(str,[i for sub in gameState.getGhostPositions() for i in sub]))
        self.line.extend(map(str,[gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]))
        self.line.extend((map(str,distances)))
        self.line.append(str(gameState.getNumFood()))
        if gameState.getNumFood()>0:
            self.line.append(str(gameState.getDistanceNearestFood()))
        else:
            self.line.append(str(9999))

        #paredes alrededor de PacMan
        #norte
        if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]+1]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #sur
        if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #este
        if gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #oeste
        if gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))

        self.line.append(str(val))
        self.line.append(str(action))
        self.line.append(str(gameState.getScore()))

        print self.line[9]
        return self.line

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food

    ''' Print the layout'''
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

class BasicAgentAA(BustersAgent):

    line = []
    lastMove = Directions.STOP
    legal = []
    score = 0



    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0


    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food

    def printLineData(self):
        self.score =  ''.join(self.line[len(self.line)-1:len(self.line)])
        return self.line

    def getLineData(self,gameState,action):
        val, idx = min((val, idx) for (idx, val) in enumerate(gameState.data.ghostDistances) if val != None)
        width, height = gameState.data.layout.width, gameState.data.layout.height
        legal = [None, None, None, None, None]
        self.line = []


        #West, Stop, East, North, South
       	if 'West' in gameState.getLegalPacmanActions():
       		legal [0] = 'West'
       	if 'Stop' in gameState.getLegalPacmanActions():
       		legal [1] = 'Stop'
       	if 'East' in gameState.getLegalPacmanActions():
       		legal [2] = 'East'
       	if 'North' in gameState.getLegalPacmanActions():
       		legal [3] = 'North'
       	if 'South' in gameState.getLegalPacmanActions():
       		legal [4] = 'South'

        distances = [i if i is not None else 0 for i in gameState.data.ghostDistances ]
        self.line.append(str(width))
        self.line.append(str(height))
        self.line.append(str(gameState.getPacmanPosition()[0]))
        self.line.append(str(gameState.getPacmanPosition()[1]))
        self.line.extend(legal)
        self.line.append(gameState.data.agentStates[0].getDirection())
        self.line.append(str(gameState.getNumAgents() - 1))
        self.line.extend(map(str,gameState.getLivingGhosts()))
        self.line.extend(map(str,[i for sub in gameState.getGhostPositions() for i in sub]))
        self.line.extend(map(str,[gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]))
        self.line.extend((map(str,distances)))
        self.line.append(str(gameState.getNumFood()))
        if gameState.getNumFood()>0:
            self.line.append(str(gameState.getDistanceNearestFood()))
        else:
            self.line.append(str(9999))

        #paredes alrededor de PacMan
        #norte
        if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]+1]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #sur
        if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #este
        if gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #oeste
        if gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))

        self.line.append(str(val))
        self.line.append(str(action))
        self.line.append(str(gameState.getScore()))

    def chooseAction(self, gameState):
        width, height = gameState.data.layout.width, gameState.data.layout.height
        previous =(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1])

        self.countActions = self.countActions + 1

        self.legal = gameState.getLegalActions(0) #Legal position from the pacman

        if self.lastMove in self.legal:
            move = self.lastMove
        elif Directions.EAST in self.legal:
            move=Directions.EAST
        elif Directions.NORTH in self.legal:
            move=Directions.NORTH
        elif Directions.WEST in self.legal:
            move=Directions.WEST
        elif Directions.SOUTH in self.legal:
            move=Directions.SOUTH
        else:
            move=Directions.STOP

        #if self.lastMove in self.legal:
        #    self.legal.remove(self.lastMove)

        #devuelve el menor valor y su indice en la lista de distancias
        val, idx = min((val, idx) for (idx, val) in enumerate(gameState.data.ghostDistances) if val != None)

        #si pacman esta por DEBAJO del fantasma mas cercano
        if gameState.getGhostPositions()[idx][1]>gameState.getPacmanPosition()[1] and Directions.NORTH in self.legal:
            #hay una pared al norte de pacman
            if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]+1]:
        #Hay pared en la casilla superior izquierda de pacman
                if gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]+1] and self.lastMove in self.legal:
                    move = self.lastMove
        #Hay pared en la casilla superior derecha de pacman
                elif gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]+1] and self.lastMove in self.legal:
                    move = self.lastMove
                if Directions.NORTH in self.legal:
                    self.legal.remove(Directions.NORTH)
            else:
                move=Directions.NORTH
        #si pacman esta por ENCIMA del fantasma mas cercano
        elif gameState.getGhostPositions()[idx][1]<gameState.getPacmanPosition()[1] and Directions.SOUTH in self.legal:
            #hay una pared al sur de pacman
            if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1]:
        #Hay una pared en la casilla inferior izquierda de pacman
                if gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]-1] and self.lastMove in self.legal:
                    move = self.lastMove
        #Hay una pared en la esquina inferior derecha de pacman
                elif gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]-1] and self.lastMove in self.legal:
                    move = self.lastMove
                if Directions.SOUTH in self.legal:
                    self.legal.remove(Directions.SOUTH)
            else:
                move=Directions.SOUTH

        #si pacman esta a la DERECHA del fantasma mas cercano
        elif gameState.getGhostPositions()[idx][0]<gameState.getPacmanPosition()[0]+1 and Directions.WEST in self.legal:
            #hay una pared al oeste de pacman
            if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]+1]:
        #Hay una pared en la esquina superior izquierda de pacman
                if gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]+1] and self.lastMove in self.legal:
                    move = self.lastMove
        #Hay pared en la esquina inferior izquierda de pacman
                elif gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]-1] and self.lastMove in self.legal:
                    move = self.lastMove
                if Directions.WEST in self.legal:
                    self.legal.remove(Directions.WEST)
            else:
                move=Directions.WEST


        #si pacman esta a la IZQUIERDA del fantasma mas cercano
        elif gameState.getGhostPositions()[idx][0]>gameState.getPacmanPosition()[0]-1 and Directions.EAST in self.legal:
            #hay una pared al este de pacman
            if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1]:
        #Hay una pared en la esquina superior derecha de pacman
                if gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]+1] and self.lastMove in self.legal:
                    move = self.lastMove
        #Hay pared en la esquina inferior derecha de pacman
                elif gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]-1] and self.lastMove in self.legal:
                    move = self.lastMove
                if Directions.EAST in self.legal:
                    self.legal.remove(Directions.EAST)
            else:
                move=Directions.EAST


        if Directions.STOP in self.legal:
            self.legal.remove(Directions.STOP)


        self.lastMove = move
        self.getLineData(gameState,move)

        return move

class MLAgent (BustersAgent):
    line = []
    legal = [None,None,None,None,None]

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)


    def printLineData(self):
        print self.line[len(self.line)-1:len(self.line)]
        return self.line

    def chooseAction(self, gameState):

        val, idx = min((val, idx) for (idx, val) in enumerate(gameState.data.ghostDistances) if val != None)
        width, height = gameState.data.layout.width, gameState.data.layout.height
        legal = [None, None, None, None, None]
        self.line = []


        #West, Stop, East, North, South
       	if 'West' in gameState.getLegalPacmanActions():
       		legal [0] = 'West'
       	if 'Stop' in gameState.getLegalPacmanActions():
       		legal [1] = 'Stop'
       	if 'East' in gameState.getLegalPacmanActions():
       		legal [2] = 'East'
       	if 'North' in gameState.getLegalPacmanActions():
       		legal [3] = 'North'
       	if 'South' in gameState.getLegalPacmanActions():
       		legal [4] = 'South'

        distances = [i if i is not None else 0 for i in gameState.data.ghostDistances ]

        self.line.append(str(width))
        self.line.append(str(height))
        self.line.append(str(gameState.getPacmanPosition()[0]))
        self.line.append(str(gameState.getPacmanPosition()[1]))
        self.line.extend(legal)
        self.line.append(gameState.data.agentStates[0].getDirection())
        self.line.append(str(gameState.getNumAgents() - 1))
        self.line.extend(map(str,gameState.getLivingGhosts()))
        self.line.extend(map(str,[i for sub in gameState.getGhostPositions() for i in sub]))
        self.line.extend(map(str,[gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]))
        self.line.extend((map(str,distances)))
        self.line.append(str(gameState.getNumFood()))
        if gameState.getNumFood()>0:
            self.line.append(str(gameState.getDistanceNearestFood()))
        else:
            self.line.append(str(9999))
        #paredes alrededor de PacMan
        #norte
        if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]+1]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #sur
        if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #este
        if gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        #oeste
        if gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]]:
            self.line.append(str(True))
        else:
            self.line.append(str(False))
        self.line.append(str(val))
        #print gameState.getScore()


        move = self.weka.predict('../p1/models/meta_naiveBayes.model',self.line,'../p1/training/training_keyboard_ff.arff')
        #weka.stop_jvm()
        #print move
        return move
