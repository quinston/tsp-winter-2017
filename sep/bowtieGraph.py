import inequalities
import pprint

V = range(1,6+1)
E = [(1,2), (1,3), (1,5), (2,3), (2,6), (3,4), (4,5), (4,6), (5,6)]
Vstar = [(1,2,3), (1,3,4,5), (2,3,4,6), (4,5,6), (1,2,5,6)]
Estar = [(1,5), (1,2), (2,5), (1,3), (3,5), (2,3), (2,4), (3,4), (4,5)]

weights = {(1,2): 10, (1,3): 10, (1,5): 1, (2,3): 10, (2,6): 1, (3,4): 1, (4,5): 10, (4,6): 10, (5,6): 10}
vinf = 3

import findTspCps
vinf = 6
findTspCps.findCps(V, E, Vstar, Estar, vinf, weights)

