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
import itertools

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
        #self.weka = Weka()
        #self.weka.start_jvm()


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

    def printHeader(self):
        header = "width,height,pacman_x,pacman_y,legal_1,legal_2,legal_3,legal_4,legal_5,facing,n_ghost,p_living,g1_living,g2_living,g3_living,g4_living,g1_x,g1_y,g2_x,g2_y,g3_x,g3_y,g4_x,g4_y,g1_m,g2_m,g3_m,g4_m,d_g1,d_g2,d_g3,d_g4,n_food,d_food,north_wall,south_wall,east_wall,west_wall,val,action"
        return header

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
        self.line.extend(map(str,legal))
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

        #print self.line[9]
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
    score = 0
    last_actions = [None] * 5
    action_counter = 0

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
        #self.score =  ''.join(self.line[len(self.line)-1:len(self.line)])
        return self.line


    def printHeader(self):
        header = "width,height,pacman_x,pacman_y,legal_1,legal_2,legal_3,legal_4,legal_5,facing,n_ghost,p_living,g1_living,g2_living,g3_living,g4_living,g1_x,g1_y,g2_x,g2_y,g3_x,g3_y,g4_x,g4_y,g1_m,g2_m,g3_m,g4_m,d_g1,d_g2,d_g3,d_g4,n_food,d_food,north_wall,south_wall,east_wall,west_wall,val,action"
        return header


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
        #self.line.append(str(width))
        #self.line.append(str(height))
        self.line.append(gameState.getPacmanPosition()[0])
        self.line.append(gameState.getPacmanPosition()[1])
        self.line.extend(map(str,legal))
        self.line.append(str(gameState.data.agentStates[0].getDirection()))
       # self.line.append(str(gameState.getNumAgents() - 1))
        self.line.extend(map(str,gameState.getLivingGhosts()[1:]))
        self.line.extend([i for sub in gameState.getGhostPositions() for i in sub])
        self.line.extend(map(str,[gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]))
        self.line.extend(distances)
        self.line.append(gameState.getNumFood())
        if gameState.getNumFood()>0:
            self.line.append(gameState.getDistanceNearestFood())
        else:
            self.line.append(9999)

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

       # self.line.append(str(val))
       #self.line.append(str(action))
       # self.line.append(str(gameState.getScore()))
        return self.line

    def chooseAction(self, gameState):
        width, height = gameState.data.layout.width, gameState.data.layout.height
        previous =(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1])

        self.countActions = self.countActions + 1
        move = None
        self.legal = gameState.getLegalActions(0) #Legal position from the pacman
        val, idx = min((val, idx) for (idx, val) in enumerate(gameState.data.ghostDistances) if val != None)
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
            else:
                move=Directions.NORTH
        #si pacman esta por ENCIMA del fantasma mas cercano
        elif gameState.getGhostPositions()[idx][1]<gameState.getPacmanPosition()[1] and Directions.SOUTH in self.legal:
            #hay una pared al sur de pacman
            if gameState.getWalls()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1]:
        #Hay una pared en la casilla inferior izquierda de pacman
                if gameState.getWalls()[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]-1] and self.lastMove in self.legal:
                    move = self.last_actions[(self.action_counter % 4 + 1) % 4]
        #Hay una pared en la esquina inferior derecha de pacman
                elif gameState.getWalls()[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]-1] and self.lastMove in self.legal:
                    move = self.lastMove
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
            else:
                move=Directions.EAST

        if Directions.STOP in self.legal:
            self.legal.remove(Directions.STOP)
        if (gameState.getDistanceNearestFood() < val/2):
            if gameState.getFood()[gameState.getPacmanPosition()[0] + 1][gameState.getPacmanPosition()[1]] and Directions.EAST in self.legal:
                move = Directions.EAST
            elif gameState.getFood()[gameState.getPacmanPosition()[0] - 1][gameState.getPacmanPosition()[1]] and Directions.WEST in self.legal:
                move = Directions.WEST
            elif gameState.getFood()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1] + 1] and Directions.NORTH in self.legal:
                move = Directions.NORTH
            elif gameState.getFood()[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1] - 1] and Directions.SOUTH in self.legal:
                move = Directions.SOUTH

        if move == self.last_actions[(self.action_counter % 5 + 4 ) % 5]:
            #print(move)
            #print(self.last_actions[(self.action_counter % 5 + 4) % 5])
            #print("entra")
            print(self.legal)

        self.lastMove = move
        self.getLineData(gameState,move)
        self.last_actions[self.action_counter % 5] = move
        self.action_counter = self.action_counter + 1
        return move

    def chooseAction2(self,gameState):
        legal = gameState.getLegalPacmanActions()
        x = self.getLineData(gameState,Directions.EAST)
        a = self.weka.predict("../p1/models/keyboard_other_model.model",x,"../p1/classification/classification_test_othermaps_keyboard.arff")
        legal.remove(Directions.STOP)

        if (a in legal):
            return a
        else: 
            a = Directions.STOP
            move_random = random.randint(0, 3)
            if   ( move_random == 0 ) and Directions.WEST in legal:  a = Directions.WEST
            if   ( move_random == 1 ) and Directions.EAST in legal: a = Directions.EAST
            if   ( move_random == 2 ) and Directions.NORTH in legal:   a = Directions.NORTH
            if   ( move_random == 3 ) and Directions.SOUTH in legal: a = Directions.SOUTH
        return a

import math

class QLearningAgent(BustersAgent):
    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = 4, observeEnable = True, elapseTimeEnable = True):
        self.pacmanX = 0
        self.pacmanY = 0
        self.ghostDistances = None
        self.g_state = None
        self.currentState = None
        self.v_score = [0, 0]
        self.tick = 0
        self.modifier = 1.0 
        self.actions = {"North":0, "East":1, "South":2,"West":3, "Exit":4}
        self.n_gameStates = 2**4
        self.n_actions = len(self.actions)
        self.table_file = open("qtable.txt","r+")
        self.q_table = self.readQtable()
        self.alpha = 0.40 
        self.gamma = 0.5
        #self.epsilon = 0.70
        self.epsilon = 0.65
        self.legalActions = None
        self.dic_states = self.generateStates()
        #print(len(self.dic_states))
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def readQtable(self):
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        return q_table

    def writeQtable(self):
        self.table_file.seek(0)
        self.table_file.truncate()

        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")

    def __del__(self):
	"Destructor. Invokation at the end of each episode"
        self.writeQtable()
        self.table_file.close()

    def computePosition(self, xPosition, yPosition, gameState):
        val, idx = min((val, idx) for (idx, val) in enumerate(self.ghostDistances) if val != None)

        walls = gameState.getWalls()
        #print(self.ghostDistances)
        state=[0,0,0,0,0,0,0]
        """
        Calcula el estado en el que se encuentra pacman.
        Version 0:
            gameState[0]: 0 = south 1 = north
            gameState[1]: 0 = west 1 = east
            gameState[2] = ghost_close
        #fantasma mas cercano al norte
        """
        #fantasma1
        if gameState.getNumAgents() - 1 > 0:
            if gameState.getLivingGhosts()[idx] == True and gameState.getGhostPositions()[0] != None:
                #fantasma1 este/oeste
                if gameState.getGhostPositions()[idx][0] >= xPosition:
                    state[0] = 1
                else:
                    state[0] = 0
                #fantasma1 norte/sur
                if gameState.getGhostPositions()[idx][1] >= yPosition:
                    state[1] = 1
                else:
                    state[1] = 0
        else:
            state[0] = 0
            state[1] = 0
        #pared norte
        if  walls[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1] + 1]:
            state[2]=1
        else:
            state[2] = 0
        #pared sur
        if  walls[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1] - 1]:
            state[3]=1
        else:
            state[3] = 0
        #pared este
        #print(walls[gameState.getPacmanPosition()[0] +1][gameState.getPacmanPosition()[1]])
        if  walls[gameState.getPacmanPosition()[0] + 1][gameState.getPacmanPosition()[1]]:
            state[4]=1
        else:
            state[4] = 0
        #pared oeste
        if  walls[gameState.getPacmanPosition()[0] - 1][gameState.getPacmanPosition()[1]]:
            state[5]=1
        else:
            state[5] = 0

        if gameState.getNumAgents() - 1 > 0:
            if val <= 1 :
                state[6] = 2
            if val > 1 and val  < 6:
                state[6] = 1
            else:
                state[6] = 0
        st = "".join(map(str,state))
        #print(st)
        #print(self.dic_states.get(st))
        #for index in self.dic_states:
            #print(self.dic_states[index])
            #if self.dic_states[index] == st:
                #print(index)
                #return index
        #print(self.dic_states[st])
        return(self.dic_states[st])

    def generateStates(self):
        b_3 = [0,1,2]
        b_2 = [0,1]
        states_b2 = [list(item) for item in itertools.product("01", repeat = 6)]
        states_b3 = [list(item) for item in itertools.product("012", repeat = 1)]
        states = [ i+j for (i,j) in itertools.product(states_b2,states_b3)]
        states = {"".join(map(str,states[i])) : i for i in range(0, len(states))}
        for i in range(98,120):
            states.pop(i,None)
        for i in range(99,120):
            states.pop(i,None)
        return states

    def getQValue(self, state, action):

        """
          Returns Q(gameState,action)
          Should return 0.0 if we have never seen a gameState
          or the Q node value otherwise
        """
        position = self.computePosition(self.pacmanX, self.pacmanY, self.g_state)
        position= 0
        action_column = self.actions[action]
        return self.q_table[position][action_column]

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        if len(self.legalActions)==0:
          return 0
        return max(self.q_table[self.computePosition(self.pacmanX, self.pacmanY,self.g_state)])

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        if len(self.legalActions)==0:
          return "exit" 

        best_actions = [self.legalActions[0]]
        best_value = self.getQValue(state,self.legalActions[0])
        for action in self.legalActions:
            value = self.getQValue(state, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value

        return random.choice(best_actions)

    def update(self, state, action, nextState, reward):
        normal = ((1-self.alpha)*self.getQValue(state, action) + self.alpha*(reward))
        extra = self.alpha*(reward+self.gamma*max(self.getValue(nextState),self.getQValue(nextState, self.computeActionFromQValues(nextState))))
        self.q_table[self.computePosition(self.pacmanX,self.pacmanY,self.g_state)][self.actions.get(action)] = normal + extra
        #print(self.epsilon)
        #self.epsilon -= 0.0001

    def getPolicy(self, state):
	"Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(state)

    def getValue(self, state):
	"Return the highest q value for a given gameState"
        return self.computeValueFromQValues(state)

    def getPacmanLegalActions(self,gameState):
        return gameState.getLegalActions()

    def getGhostPositions(self):
        return (self.g_state.getNoisyGhostDistances())

    def getNextState(self, action):
        if action == "West":
            return self.computePosition(self.pacmanX+1,self.pacmanY,self.g_state)
        if action =="East":
            return self.computePosition(self.pacmanX-1,self.pacmanY,self.g_state)
        if action == "North":
            return self.computePosition(self.pacmanX,self.pacmanY+1,self.g_state)
        if action == "South":
            return self.computePosition(self.pacmanX,self.pacmanY-1,self.g_state)

    def getReward(self, gameState):
        val, idx = min((val, idx) for (idx, val) in enumerate(self.ghostDistances) if val != None)
        reward = 0.0
        max_distance =math.sqrt(gameState.data.layout.width**2 + gameState.data.layout.height**2)
        walls = gameState.getWalls()
        dist = max_distance - val #+ 6
        factor = 1
        #print(dist)

        reward = (-self.v_score[(self.tick % 2 + 1) % 2] + self.v_score[self.tick % 2])
        #Si el fantasma mas cercano esta vivo (evita errores)
        if(gameState.getLivingGhosts()[idx] != None):
            #si pacman esta encerrado entre dos paredes
            if ((walls[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]] and walls[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]]) or (walls[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]+1] and  walls[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1])):
                #reward = reward - dist - 30
            #si pacman esta en la misma altura o ancho del fantasma mas cercano
                if gameState.getPacmanPosition()[1] == gameState.getGhostPositions()[idx][1]:
                    #reward = reward - dist 
                    if val > 6:
                        reward = reward -dist-30
                    elif val >= 2 and val <=6:
                        reward = reward + dist + 20
                    elif val < 2:
                        reward = reward + dist + 25
            #si pacman esta en contacto con alguna pared
            elif walls[gameState.getPacmanPosition()[0]-1][gameState.getPacmanPosition()[1]] or walls[gameState.getPacmanPosition()[0]+1][gameState.getPacmanPosition()[1]] or walls[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]+1] or walls[gameState.getPacmanPosition()[0]][gameState.getPacmanPosition()[1]-1]:
                #reward = reward -dist - 10
                if gameState.getPacmanPosition()[1] == gameState.getGhostPositions()[idx][1]:
                    #reward = reward -dist 
                    if val > 6:
                        reward = reward -dist-20
                    elif val >= 2 and val <=6:
                        reward = reward + dist +10
                    elif val < 2:
                        reward = reward + dist + 15
            else:
                    #en caso de no estar con paredes
                if val >= 2 and val <= 6:
                    reward = reward + dist + 35 
                elif val < 2:
                    reward = reward + dist + 50 
                else:
                    reward = reward - dist

        return float(reward)

    def printState(self,currentState,action,qvalue,reward,random):
        print("=========================================")
        if(random == True):
            print("Accion aleatoria tomada")
        print("Estado actual: %d" % currentState)
        print("Mejor accion para %d: %s" % (currentState, self.getPolicy(self.currentState)))
        print("Accion tomada: %s con Q-valor %f" % (self.getPolicy(self.currentState), float(qvalue)))
        print("Recompensa: %d" % reward)
        #self.printQtable()
        print("=========================================")
        print("")

    def printQtable(self):
        for line in self.q_table:
            print(line)

    def getAction(self, gameState):
        """
          Compute the action to take in the current gameState.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal gameState, you
          should choose None as the action.
        """
        #obtener datos necesarios de gameState
        self.g_state = gameState
        #rint(self.g_state.data.getLivingGhosts())
        #print(self.g_state.getNumAgents())
        self.v_score[self.tick % 2] = self.g_state.getScore()
        #distancia a los fantasmas
        #self.getGhostsPositions()
        self.ghostDistances = self.getGhostPositions()
        #posicion de pacman
        self.pacmanX = gameState.getPacmanPosition()[0] 
        self.pacmanY = gameState.getPacmanPosition()[1]
        #acciones legales
        self.legalActions = self.getPacmanLegalActions(self.g_state)
        self.legalActions.remove("Stop")
        #estado actual
        self.currentState = self.computePosition(self.pacmanX,self.pacmanY,gameState)
        #action = self.legalActions[0] 
        action = self.getPolicy(self.currentState) 
        reward = self.getReward(gameState) 
        #print(reward)


        #self.printState(self.currentState,action,float(self.getQValue(self.currentState,action)),reward,False)
        self.update(self.currentState,action,self.getNextState(action),reward)
        self.tick += 1

        flip = util.flipCoin(self.epsilon)

        if flip:
            action = random.choice(self.legalActions)
            #self.printState(self.currentState,action,float(self.getQValue(self.currentState,action)),reward,True)
            self.update(self.currentState,action,self.getNextState(action),reward)
            self.tick += 1
            return action
        return self.getPolicy(gameState)
