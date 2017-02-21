	


"""
vertices: of the form range(1, n+1)
edges: list of iterables, each set containing two integers
weights: map from edges to real numbers
"""

"""
Returns a list of pairs of subsets S of V to  delta(S)

usePlaceholders: Print 1, 2, 3, ..., |E| instead of the actual edge
"""
def deltas(vertices, edges, usePlaceholders=False):
	import itertools
	for i in range(2, len(vertices)//2 + 1):
		for S in itertools.combinations(vertices, i):
			if not usePlaceholders:
				yield (S, [e for e in edges if (e[0] in S and e[1] not in S) or (e[0] not in S and e[1] in S)])
			elif usePlaceholders:
				yield (S, [i for i,e in enumerate(edges, 1) if (e[0] in S and e[1] not in S) or (e[0] not in S and e[1] in S)])

"""
Returns an iterable of ((v), (e1, e2, ...))
where delta(v) = {e1, e2, ...}
"""
def degreeConstraints(vertices, edges, usePlaceholders=False):
	import itertools
	for i in vertices:
		if not usePlaceholders:
			yield ((i,), [e for e in edges if i in e])
		elif usePlaceholders:
			yield ((i,), [j for j,e in enumerate(edges, 1) if i in e])


def makeSepLp(vertices, edges, weights=None):
	return """Minimize
{objective}
subject to
{equalities}
{inequalities}
bounds
{bounds}""".format(
equalities='\n'.join(' + '.join("x{}".format(i) for i in constraint[1]) + " = 2" for constraint in degreeConstraints(vertices, edges, True)),
objective=' + '.join("{}x{}".format("" if weights == None else weights[e], i) for i,e in enumerate(edges, 1)),
inequalities='\n'.join(' + '.join("x{}".format(i) for i in constraint[1]) + " >= 2" for constraint in deltas(vertices, edges, True)),
bounds='\n'.join("x{} >= 0".format(i) for i,e in enumerate(edges, 1))
)

"""
Returns a dictionary of the form { e -> ["ze,u", "ze,v"] } where e* = {u,v}, vinf not in e, e in E
"""
def getExtraVariables(edges, dualEdges, vinf):
	return dict((eIndex, ["z{},{}".format(eIndex, fIndex) for fIndex in dualEdges[eIndex - 1]]) for eIndex, e in enumerate(edges, 1) if (vinf not in e))

"""
dualVertices: iterable of (iterables of (vertices on each face))
dualEdges: the ith dual edge should intersect the ith primal edge
vinf: arbitrary vertex
"""
def makeExtendedLp(vertices, edges, dualVertices, dualEdges, vinf, weights=None):
	assert len(edges) == len(dualEdges)
	assert len(vertices) + len(dualVertices) - len(dualEdges) == 2

	import itertools

	# z_ev, e in E, vinf not in e, v in V*, v in e*
	extraVariables = getExtraVariables(edges, dualEdges, vinf)

	return "\n".join(itertools.chain(
["Minimize"],
#Objective
[(' + '.join("{}x{}".format("" if weights == None else weights[e], i) for i,e in enumerate(edges, 1)))],
["subject to"],
#Mixed inequalities
("x{} + {} + {} = 1".format(pair[0], pair[1][0], pair[1][1]) for pair in extraVariables.items()),
#Inequalities with purely additional variables
(" + ".join("z{},{}".format(eIndex, fIndex) for eIndex, e in enumerate(dualEdges, 1) if fIndex in e) + " = 1" for fIndex, f in enumerate(dualVertices, 1) if vinf not in f),
# Degree constraints
(' + '.join("x{}".format(i) for i in constraint[1]) + " = 2" for constraint in degreeConstraints(vertices, edges, True)),
["bounds"],
("x{} >= 0".format(i) for i,e in enumerate(edges, 1)),
("{} >= 0".format(z) for z in itertools.chain(*(extraVariables.values())))
))

"""
e.g. if the final variables are in that order then x1, x2, x3, z3,1, z3,2,
then return

["x1", "x2", "x3", "z3,1", "z3,2"]
"""
def enumerateExtendedLpVariables(vertices, edges, dualVertices, dualEdges, vinf):
	import itertools
	return ["x{}".format(i) for i in range(1, len(edges)+1)] + list(itertools.chain(*(uv for e,uv in sorted(getExtraVariables(edges, dualEdges, vinf).items()))))

"""
Gives rows of Ax <= b that comprise the description of the extended formulation of SEP

Returns: iterable of (a: iterable of real, b: real)
"""
def makeExtendedLpConstraintMatrix(vertices, edges, dualVertices, dualEdges, vinf, includeBounds=False):
	import itertools
	extraVariables = getExtraVariables(edges, dualEdges, vinf)
	noOriginalVariables = len(edges)
	noExtraVariables = 2 * len(extraVariables) 
	noVariables = noOriginalVariables + noExtraVariables

	# Assign indices to the extra variables ze,u's starting after the xi's
	enumerationOfExtraVariables = dict((x,n) for n,x in enumerate(itertools.chain(*(extraVariables.values())), noOriginalVariables + 1))

	ret = []

	# Mixed equalities
	for edgeIndex, edgeExtraVariables in extraVariables.items():
		row = [0] * noVariables
		row[edgeIndex - 1] = row[enumerationOfExtraVariables[edgeExtraVariables[0]] - 1] = row[enumerationOfExtraVariables[edgeExtraVariables[1]] - 1] = 1
		ret.append((row, 1))
		ret.append(([-x for x in row], -1))

	# Pure extra equalities
	for fIndex, f in enumerate(dualVertices, 1):
		if vinf not in f:
			row = [0] * noVariables
			for eIndex, e in enumerate(dualEdges, 1):
				if fIndex in e:
					row[enumerationOfExtraVariables["z{},{}".format(eIndex, fIndex)] - 1] = 1
			ret.append((row, 1))
			ret.append(([-x for x in row], -1))

	# Degree inequalities
	for constraint in degreeConstraints(vertices, edges, True):
		row = [0] * noVariables
		for i in constraint[1]:
			row[i - 1] = 1
		ret.append((row, 2))
		ret.append(([-x for x in row], -2))

	if includeBounds:
			for i in range(noVariables):
				row = [0] * noVariables
				row[i] = -1
				ret.append((row, 0))

	return ret

def makeSparseExtendedLpMatrix(vertices, edges, dualVertices, dualEdges, vinf, includeBounds=False):
	import scipy.sparse

	noOriginalVariables = len(edges)
	variableNames = enumerateExtendedLpVariables(vertices, edges, dualVertices, dualEdges, vinf)
	enumerationOfVariables = dict((b,a) for a,b in enumerate(variableNames))
	noVariables = len(variableNames)
	extraVariables = getExtraVariables(edges, dualEdges, vinf)

	# E - delta(vinf)
	noMixedEqualities = sum(1 for e in edges if vinf not in e)
	# V* - faces with vinf in boundary cycle
	noPureExtraEqualities = sum(1 for f in dualVertices if vinf not in f)
	noDegreeConstraints = len(vertices)
	noBoundsConstraints = noVariables

	noConstraints = (noMixedEqualities  + noPureExtraEqualities + noDegreeConstraints) * 2
	if includeBounds:
		noConstraints += noBoundsConstraints

	ret = scipy.sparse.dok_matrix((noConstraints, noVariables + 1))

	nextConstraintRow = 0

	# Mixed equalities
	for edgeIndex, edgeExtraVariables in extraVariables.items():
		ret[nextConstraintRow, edgeIndex - 1] = ret[nextConstraintRow, enumerationOfVariables[edgeExtraVariables[0]]] = ret[nextConstraintRow, enumerationOfVariables[edgeExtraVariables[1]]] = 1
		ret[nextConstraintRow, noVariables] = 1
		ret[nextConstraintRow + 1, :] = -ret[nextConstraintRow, :]
		nextConstraintRow += 2
	
	# Pure extra equalities
	for fIndex, f in enumerate(dualVertices, 1):
		if vinf not in f:
			ret[nextConstraintRow, noVariables] = 1
			for eIndex, e in enumerate(dualEdges, 1):
				if fIndex in e:
					extraVariableIndex = enumerationOfVariables["z{},{}".format(eIndex, fIndex)]
					ret[nextConstraintRow, extraVariableIndex] = 1
			ret[nextConstraintRow + 1, :] = -ret[nextConstraintRow, :]
			nextConstraintRow += 2

	# Degree equalities
	for constraint in degreeConstraints(vertices, edges, True):
		ret[nextConstraintRow, noVariables] = 2
		for eIndex in constraint[1]:
			ret[nextConstraintRow, eIndex - 1] = 1
		ret[nextConstraintRow + 1, :] = -ret[nextConstraintRow, :]
		nextConstraintRow += 2

	if includeBounds:
			for i in range(noVariables):
				ret[nextConstraintRow, i] = -1
				nextConstraintRow += 1

	assert(nextConstraintRow == noConstraints)

	return ret

"""
Introduce 0-1 variables
b_f for each face f (=1  if f is black)
c_e,u and c_e,v for each dual edge e={u,v} where b_u - b_v <= c_e,u
"""
def makeSparseFaceColourNonnegativityMatrix(V, E, Vstar, Estar, vinf):
	import scipy.sparse
	degreeVinf = sum(1 if vinf in e else 0 for e in E)
	noEsepVariables = 3*len(E) - 2*degreeVinf
	noColourVariables = len(Vstar) + 2*len(Estar)
	noVariables = noEsepVariables + noColourVariables
	noConstraints = noColourVariables 
	ret = scipy.sparse.dok_matrix((noConstraints, noVariables + 1))

	for i in range(noColourVariables):
		ret[i, noEsepVariables + i] = -1

	return ret

def makeSparseFaceColourBidirectionallyBoundedGradientMatrix(V, E, Vstar, Estar, vinf):
	import scipy.sparse
	degreeVinf = sum(1 if vinf in e else 0 for e in E)
	noEsepVariables = 3*len(E) - 2*degreeVinf
	noColourVariables = len(Vstar) + 2*len(Estar)
	noVariables = noEsepVariables + noColourVariables
	noConstraints = len(E)
	ret = scipy.sparse.dok_matrix((noConstraints, noVariables + 1))

	for i in range(len(E)):
		ret[i, i] = -1
		ret[i, (noEsepVariables+len(Vstar)+2*i):(noEsepVariables+len(Vstar)+2*i+2)] = [1,1]

	return ret

def makeSparseFaceColourUnidirectionallyBoundedGradientMatrix(V, E, Vstar, Estar, vinf):
	import scipy.sparse
	degreeVinf = sum(1 if vinf in e else 0 for e in E)
	noEsepVariables = 3*len(E) - 2*degreeVinf
	noColourVariables = len(Vstar) + 2*len(Estar)
	noVariables = noEsepVariables + noColourVariables
	noConstraints = len(Estar) * 2
	ret = scipy.sparse.dok_matrix((noConstraints, noVariables + 1))

	for i,e in enumerate(Estar):
		ret[2*i, noEsepVariables + e[0] - 1] = 1
		ret[2*i, noEsepVariables + e[1] - 1] = -1
		ret[2*i+1, :] = -ret[2*i, :]

	for i in range(2*len(Estar)):
		ret[i, noEsepVariables + len(Vstar) + i] = -1

	return ret

def getFaceColourVariableNames(Vstar, Estar):
	import itertools
	return ["b{}".format(i) for i in range(1, len(Vstar)+1)] + list(itertools.chain(*[["c{},{}".format(e,u), "c{},{}".format(e,v)] for e,(u,v) in enumerate(Estar, 1)]))
