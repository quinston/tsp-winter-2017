import findTspCps

V = range(1,8+1)
E = [(1,2),(1,3),(2,4),(3,4),
(1,7),(3,5),(4,6),(2,8),
(7,8),(5,7),(6,8),(5,6)]
Vstar = [(1,2,3,4), (1,3,5,7), (3,4,5,6), (2,4,6,8), (5,6,7,8), (1,2,7,)]
Estar = [(1,6),(1,2),(1,4),(1,3),(2,6),(2,3),(3,4),(4,6),
(5,6),(2,5),(4,5),(3,5)]

weights = {(1,2):10,(1,3):10,(2,4):10,(3,4):10,
(1,7): 1,(3,5): 1,(4,6): 1,(2,8): 1,
(7,8): 10,(5,7): 10,(6,8): 10,(5,6): 10}

vinf = 1

findTspCps.findCps(V,E,Vstar,Estar,vinf,weights)