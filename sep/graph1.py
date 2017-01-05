import inequalities
import pprint 

pp = pprint.PrettyPrinter()

def pretty(x):
	return pp.pformat(sorted(list(x), key=lambda y:(len(y[0]),y)))

V = range(1,5+1)
E = [(1,2),(1,3),(1,5),(2,3),(2,4),(3,4),(4,5)]
weights = {(1,2): 3.1, (1,3): 3.2, (1,5): 3.11, (2,3): 3.14, (2,4): 2.9, (3,4): 3.04, (4,5): 3.03}

print(inequalities.makeSepLp(V, E, weights))

Vstar = range(1,4+1)
# there is a duplicate edge
# make sure these are exactly the intersecting pairs for the dual of the dual (primal) edges
Estar = [(1,4), (1,3), (3,4), (1,2), (2,4), (2,3), (3,4)]

print(inequalities.makeExtendedLp(V, E, [(1,2,3), (2,3,4), (1,3,4,5), (1,2,4,5)], Estar, 5, weights))
