
"""
Returns V, E, V*, E*
"""
def readUsa532():
	# Note the vertices start at 0
	# but we are going to make them start at 1
	V = list(range(1, 532+1))

	E = []
	# format is V V w_e
	with open('usa532_del.edg') as f:
		# Skip first line
		f.readline()
		for line in f:
			l = [int(x) for x in line.split()]
			E.append((l[0] + 1, l[1] + 1))


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

	return (V,E,Vstar,Estar)

if __name__ == '__main__':
	vinf = 1
	import gridGraph
	V, E, Vstar, Estar = gridGraph.gridGraph(6)
	#V, E, Vstar, Estar = readUsa532()
	import mod2cutSolver
	mod2cutSolver.mod2cutsLoop(V, E, Vstar, Estar, vinf)
