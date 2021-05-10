import pprint
import numpy as np

#17 rows 5 columns
#start and end states
startState = (0,0)
goalState = (16,0)

#initialize the field with certain ravine cost
def initialize_grid(cost):
    grid = [[1 for i in range(5)] for j in range(17)]
    ravine_cost = cost

    for i in range(2, 7):
        grid[i][0] = ravine_cost
    for i in range(6, 11):
        grid[i][4] = ravine_cost
    for i in range(10, 15):
        grid[i][0] = ravine_cost
    return grid

#tuples of all possible actions
deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]

#gets proper actions from the 
def prop_actions(grid, state):
    deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]
    #get all neighbors
    neighbors = list((state[0] + d[0], state[1] + d[1]) for d in deltas)
    #zip neighbors with deltas to keep them together
    zipped = list(zip(neighbors, deltas))
    #sort out impossible neighbors
    filtered = list(filter(lambda x: (0<=x[0][0]< 17 and 0<=x[0][1]<5), zipped))
    #get possible neighbors and appropriate actions to get to them ordered in same way
    prop_nbors, acts = zip(*filtered)
    return prop_nbors, acts

#get the orthogonal actions to a specific action if they are possible to get to
def orthogonal(action, actions):
    result = []
    a_1 = tuple([action[1], action[0]])
    a_2 = tuple([-1*action[1], -1*action[0]])
    if a_1 in actions:
        result.append(a_1)
    if a_2 in actions:
        result.append(a_2)
    return result

#go from a state to where the action dictates a state to go
def apply_action(action, state):
    return (state[0] + action[0], state[1] + action[1])

#returns a list of tuples of (new state, probability to that new state, cost)
#for each possible neighbor to get to
def poss_action_cost(grid, state, action):
    #newstate, prob, cost triplets
    result = []
    properNeighbors, actions = prop_actions(grid, state)
    num_neighbors = len(properNeighbors)
    #special case of corners to simplify calculations
    if num_neighbors == 2:
        if action == actions[0]:
            result.append((properNeighbors[0], .9, 1))
            result.append((properNeighbors[1], .1, 1))
        else:
            result.append((properNeighbors[1], .9, 1))
            result.append((properNeighbors[0], .1, 1))
    #general case 3/4 neighbors
    else:
        #get orthogonal neighbors if there are 2, then you can move to either with 10% 
        #and to the main with 80%
        #otherwise it's 90%/10%
        orthog = orthogonal(action, actions)
        if len(orthog) == 2:
            newstate = apply_action(action, state)
            result.append((apply_action(action, state), .8, grid[newstate[0]][newstate[1]]))
            for act in orthog:
                orthogstate = apply_action(act, state)
                result.append((orthogstate, .1, grid[newstate[0]][newstate[1]]))
        else:
            newstate = apply_action(action, state)
            result.append((apply_action(action, state), .9, grid[newstate[0]][newstate[1]]))
            newstate = apply_action(orthog[0], state)
            result.append((apply_action(orthog[0], state), .1, grid[newstate[0]][newstate[1]]))
    return result

#value iteration algorithm
def valueiteration(grid):
    #dict representing our cost
    min_cost = {}
    for i in range(17):
        for j in range(5):
            state = (i,j)
            #initial guess of all the costs
            min_cost[state] = 100000
    #setting goal to 0 cost (since that's the exit state)
    min_cost[goalState] = 0

    #function used to return C(x) based on the cost of neighbors
    def exp_update(state, action):
        return sum(prob*(cost+min_cost[newstate]) for newstate, prob, cost in poss_action_cost(grid, state, action)) 
    #convergence boolean
    converge = False
    #counter = 0
    while not converge:
        #updated cost dict
        new_min_cost = {}
        for state in min_cost:
            #set goal and ravines to their exit costs (0, ravine cost respectively)
            if state == goalState:
                new_min_cost[state] = 0
            if grid[state[0]][state[1]] == ravine_cost:
                new_min_cost[state] = ravine_cost
        #for the other states, refigure the minimum costs using the value iteration update
        #minimizing over possible costs of each move in each state
        for state in min_cost:
            if state != goalState and grid[state[0]][state[1]] != ravine_cost:
                prop_nbors, actions = prop_actions(grid, state)
                new_min_cost[state] = min(exp_update(state, action) for action in actions)
        #print(max(abs(min_cost[state] - new_min_cost[state]) for state in min_cost))
        #counter+=1
        #convergence condition: the highest difference is less than 10^-10
        if max(abs(min_cost[state] - new_min_cost[state]) for state in min_cost) < 1e-10:
            converge = True
        #update dictionary with new value. Only need to keep track of 2 per iteration
        min_cost = new_min_cost
    
    #find policy
    #string associating deltas with direction
    direction_string = ['D', 'U', 'R', 'L']
    #path dict
    directions = {}
    for i in range(17):
        for j in range(5):
            state = (i,j)
            #intiialize all states as no path
            directions[state] = 'N'
    #for non exit states, find the lowest expected cost path out of possible actions
    for state in directions:
        if state != goalState and grid[state[0]][state[1]] != ravine_cost:
            prop_nbors, actions = prop_actions(grid, state)
            update_list = []
            #get all possible update values for each action
            for action in actions:
                update_list.append(exp_update(state, action))
            #find action that minimizes the expected cost
            act = actions[update_list.index(min(update_list))]
            #set that direction
            directions[state] = direction_string[deltas.index(act)]
    return min_cost, directions

#printer function irreleevant
def print_d(d):
    out = [[1 for i in range(5)] for j in range(17)] 
    for s in d:
        out[s[0]][s[1]] = d[s]
        if type(d[s]) is float:
            out[s[0]][s[1]] = round(d[s], 2)
        if type(d[s]) is int:
            out[s[0]][s[1]] = round(float(d[s]), 2)
    return out

#driver examples
grid = initialize_grid(1000)
ravine_cost = 1000
m, d = valueiteration(grid)
ravine_cost = 45.02
grid = initialize_grid(45.02)
m2, d2 = valueiteration(grid)
print(d2 == d)
pprint.pprint(print_d(d2))