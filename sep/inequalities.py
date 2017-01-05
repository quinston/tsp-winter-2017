	


"""
vertices: of the form range(1, n+1)
edges: list of iterables, each set containing two integers
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

def makeCplex(vertices, edges):
	return """Minimize
{objective}
subject to
{equalities}
{inequalities}
bounds
{bounds}""".format(
equalities='\n'.join(' + '.join("x{}".format(v) for v in constraint[1]) + " = 2" for constraint in degreeConstraints(vertices, edges, True)),
objective=' + '.join("x{}".format(v) for v in vertices),
inequalities='\n'.join(' + '.join("x{}".format(v) for v in constraint[1]) + " >= 2" for constraint in deltas(vertices, edges, True)),
bounds='\n'.join("x{} >= 0".format(v) for v in vertices)
)

def inequalities(vertices, edges):
	pass	

