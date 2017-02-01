
"""
Returns V, E, V*, E*, weights
"""
def readUsa532():
	# Note the vertices start at 0
	# but we are going to make them start at 1
	V = list(range(1, 532+1))

	weights = {}

	E = []
	# format is V V w_e
	with open('usa532_del.edg') as f:
		# Skip first line
		f.readline()
		for line in f:
			l = [int(x) for x in line.split()]
			E.append((l[0] + 1, l[1] + 1))
			weights[E[-1]] = l[2]


	Estar = []
	faceBoundaryCycles = None

	# format is V* V* w_e
	with open('usa532_dual.edg') as f:
		# Get number of faces
		l = [int(x) for x in f.readline().split()]
		noFaces = l[0]
		faceBoundaryCycles = dict((i, set()) for i in range(noFaces))
		numEdge = 0

		for line in f:
			l = [int(x) for x in line.split()]
			Estar.append((l[0] + 1, l[1] + 1))
			# Add incident vertices to boundary cycle
			faceBoundaryCycles[l[0]].add(E[numEdge][0])
			faceBoundaryCycles[l[0]].add(E[numEdge][1])
			faceBoundaryCycles[l[1]].add(E[numEdge][0])
			faceBoundaryCycles[l[1]].add(E[numEdge][1])
			
			numEdge += 1

	Vstar = [tuple(faceBoundaryCycles[i]) for i in range(noFaces)]

	assert (len(V) + len(Vstar) - len(E) == 2)

	return (V,E,Vstar,Estar, weights)

if __name__ == '__main__':
	vinf = 10
	weights = None
	import gridGraph
	V, E, Vstar, Estar = gridGraph.gridGraph(12)
	# V, E, Vstar, Estar, weights = readUsa532()
	import mod2cutSolver
	mod2cutSolver.mod2cutsLoop(V, E, Vstar, Estar, vinf, weights)
