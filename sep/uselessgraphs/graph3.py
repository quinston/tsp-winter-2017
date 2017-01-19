import inequalities

V = range(1, 9+1)
E = [(1,6), (1,7), (1,2), (6,5), (6,7), (7,8), (2,3), (5,9), (8,9), (4,5), (4,8), (3,4), (4,9)]
Vstar = [(1,6,7), (5,6,7,8,9), (1,2,3,4,7,8), (4,5,9), (4,8,9), (1,2,3,4,5,6)]
Estar = [(1,6), (1,3), (3,6), (2,6), (1,2), (2,3), (3,6), (2,4), (2,5), (4,6), (3,5), (3,6), (4,5)]

# don't use these for the moment
weights = {(1,6): 1, (1,7): 1.2, (1,2): 1.1, (6,5): 1.3, (6,7): 0.9, (7,8): 1, (2,3): 1.2, (5,9): 1.1, (8,9): 1.3, (4,5): 0.9, (4,8): 1, (3,4): 1.2, (4,9): 1.1}

print(inequalities.makeSepLp(V, E, weights=weights))

print(inequalities.makeExtendedLp(V, E, Vstar, Estar, 1, weights=weights))
