	


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
dualVertices: iterable of (iterables of (vertices on each face))
dualEdges: the ith dual edge should intersect the ith primal edge
vinf: arbitrary vertex
"""
def makeExtendedLp(vertices, edges, dualVertices, dualEdges, vinf, weights=None):
	assert len(edges) == len(dualEdges)
	assert len(vertices) + len(dualVertices) - len(dualEdges) == 2

	import itertools

	# z_ev, e in E, vinf not in e, v in V*, v in e*
	extraVariables = dict((eIndex, ["z{},{}".format(eIndex, fIndex) for fIndex in dualEdges[eIndex - 1]]) for eIndex, e in enumerate(edges, 1) if (vinf not in e))

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
