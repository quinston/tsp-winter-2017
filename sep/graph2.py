import inequalities

V = range(1, 4+1)
E = [(1,2),(1,3),(1,4),(2,4),(3,4)]
weights = {(1,2): 2, (1,3): 2.1, (1,4): 2.05, (2,4): 1.95, (3,4): 1.96}
Vstar = [(1,2,4), (1,3,4), (1,2,3,4)]
Estar = [(1,3), (2,3), (1,2), (1,3), (2,3)]

print(inequalities.makeSepLp(V, E, weights))
print(inequalities.makeExtendedLp(V, E, Vstar, Estar, 4))
print(inequalities.makeExtendedLp(V, E, Vstar, Estar, 3))
print(inequalities.makeExtendedLp(V, E, Vstar, Estar, 2))
print(inequalities.makeExtendedLp(V, E, Vstar, Estar, 1))

