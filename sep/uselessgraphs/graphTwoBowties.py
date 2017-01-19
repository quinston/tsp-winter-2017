"""
bowties joined each at both ends by four edges
"""

V = range(1, 12+1)
E = [(1,2), (1,3), (2,3), (3,4), (1,5), (2,6), (4,5), (4,6), (5,6),
(7,8), (7,9), (8,9), (9, 10), (7,11), (8,12), (10,11), (10,12), (11,12),
(5,7), (6,8),
(1, 11), (2, 22)]
Vstar = [(1,2,3), (1,3,4,5), (2,3,4,6), (4,5,6), 
(5,6,7,8), 
(7,8,9), (7,9,10,11), (8,9,10,12), (10,11,12), 
(1,2, 11, 12),
(2,6,8,12),
(1,5,7,11)]
Estar = [(1,10), (1,2), (1,3), (2,3), (2,12), (3,11), (2,4), (3,4), (4,5),
(5,6), (6,7), (6,8), (7,8), (7,12), (8,11), (7,9), (8,9), (9,10), 
(5,12), (5,11),
(10,12), (10, 11)]

weights = {(1,2): 10, (1,3): 10, (2,3): 10, (1,5): 1, (2,6): 1, (3,4): 1, (4,5): 10, (4,6): 10, (5,6): 10,
(5,7): 1, (6,8): 1,
(7,8): 10, (8,9): 10, (7,9): 10, (7,11): 1, (9,10): 1, (8,12): 1, (10,11): 10, (10,12): 10, (11,12): 10,
(1,11): 1, (2,22): 1}

import findTspCps

for vinf in V:
	print("\nvinf = {}".format(vinf))
	findTspCps.findCps(V, E, Vstar, Estar, vinf, weights)
