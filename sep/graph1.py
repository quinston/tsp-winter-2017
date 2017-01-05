import inequalities

def pretty(x):
	return sorted(list(x), key=lambda y:(len(y[0]),y))

V = range(1,5+1)
E = [(1,2),(1,3),(1,5),(2,3),(2,4),(3,4),(4,5)]


print(pretty(inequalities.deltas(V, E)))

Vstar = range(1,4+1)
# there is a duplicate edge
Estar = [(1,2),(1,3),(1,4),(2,3),(2,4),(3,4),(3,4)]

print(pretty(inequalities.deltas(Vstar, Estar)))
