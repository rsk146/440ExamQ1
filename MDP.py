import pprint
import numpy as np
#5 rows 17 columns

startState = (0,0)
goalState = (16,0)

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

deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]

def prop_actions(grid, state):
    deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]
    neighbors = list((state[0] + d[0], state[1] + d[1]) for d in deltas)
    zipped = list(zip(neighbors, deltas))
    filtered = list(filter(lambda x: (0<=x[0][0]< 17 and 0<=x[0][1]<5), zipped))
    prop_nbors, acts = zip(*filtered)
    return prop_nbors, acts

def orthogonal(action, actions):
    result = []
    a_1 = tuple([action[1], action[0]])
    a_2 = tuple([-1*action[1], -1*action[0]])
    if a_1 in actions:
        result.append(a_1)
    if a_2 in actions:
        result.append(a_2)
    return result

def apply_action(action, state):
    return (state[0] + action[0], state[1] + action[1])

def poss_action_cost(grid, state, action):
    #newstate, prob, cost triplets
    result = []
    properNeighbors, actions = prop_actions(grid, state)
    num_neighbors = len(properNeighbors)
    if num_neighbors == 2:
        if action == actions[0]:
            result.append((properNeighbors[0], .9, 1))
            result.append((properNeighbors[1], .1, 1))
        else:
            result.append((properNeighbors[1], .9, 1))
            result.append((properNeighbors[0], .1, 1))
    else:
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

def valueiteration(grid):
    min_cost = {}
    for i in range(17):
        for j in range(5):
            state = (i,j)
            min_cost[state] = 100000
    min_cost[goalState] = 0

    def exp_update(state, action):
        return sum(prob*(cost+min_cost[newstate]) for newstate, prob, cost in poss_action_cost(grid, state, action)) 

    converge = False
    counter = 0
    while not converge:
        new_min_cost = {}
        for state in min_cost:
            if state == goalState:
                new_min_cost[state] = 0
            if grid[state[0]][state[1]] == ravine_cost:
                new_min_cost[state] = ravine_cost
        for state in min_cost:
            if state != goalState and grid[state[0]][state[1]] != ravine_cost:
                prop_nbors, actions = prop_actions(grid, state)
                new_min_cost[state] = min(exp_update(state, action) for action in actions)
        #print(max(abs(min_cost[state] - new_min_cost[state]) for state in min_cost))
        counter+=1
        if max(abs(min_cost[state] - new_min_cost[state]) for state in min_cost) < 1e-10:
            converge = True
        min_cost = new_min_cost

    direction_string = ['D', 'U', 'R', 'L']
    directions = {}
    for i in range(17):
        for j in range(5):
            state = (i,j)
            directions[state] = 'N'
    for state in directions:
        if state != goalState and grid[state[0]][state[1]] != ravine_cost:
            prop_nbors, actions = prop_actions(grid, state)
            update_list = []
            for action in actions:
                update_list.append(exp_update(state, action))
            act = actions[update_list.index(min(update_list))]
            directions[state] = direction_string[deltas.index(act)]
    return min_cost, directions

def print_d(d):
    out = [[1 for i in range(5)] for j in range(17)] 
    for s in d:
        out[s[0]][s[1]] = d[s]
        if type(d[s]) is float:
            out[s[0]][s[1]] = round(d[s], 2)
        if type(d[s]) is int:
            out[s[0]][s[1]] = round(float(d[s]), 2)
    return out

grid = initialize_grid(1000)
ravine_cost = 1000
m, d = valueiteration(grid)
ravine_cost = 45.02
grid = initialize_grid(45.02)
m2, d2 = valueiteration(grid)
print(d2 == d)

pprint.pprint(print_d(d2))