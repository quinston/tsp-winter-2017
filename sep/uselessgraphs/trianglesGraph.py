import findTspCps

V = range(1,12+1)
E = [(1,2), (1,3), (2,3), 
(4,5), (4,6), (5,6),
(7,8), (7,9), (8,9),
(10, 11), (10,12), (11,12),
(3,10), (6,11), (9,12),
(2,4), (5,7), (1,8)]
Vstar = [(1,2,3), (4,5,6), (7,8,9), (10,11,12), (2,3,10,11,6,4),
(9,7,5,6,11,12), (1,8,9,12,10,3), (1,2,4,5,7,8)]
Estar = [(1,8), (1,7), (1,5), 
(2,8), (2,5), (2,6), 
(3,8), (3,6), (3,7), 
(4,5), (4,7), (4,6),
(5,7), (5,6), (6,7),
(5,8), (6,8), (7,8)]

weights = {(1,2): 1, (1,3): 1, (2,3): 1, (4,5): 1, (4,6): 1, (5,6): 1,
(7,8): 1, (7,9): 1, (8,9): 1, (10,11): 1, (10,12): 1, (11,12): 1,
(3,10): 7, (6, 11): 7, (9,12): 7,
(2,4): 11, (5,7): 11, (1,8): 11}

vinf = 1

findTspCps.findCps(V, E, Vstar, Estar, vinf, weights)