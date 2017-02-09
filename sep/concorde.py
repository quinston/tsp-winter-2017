"""
Some tools for working with Concorde
"""

"""
Expects:
E: A list of pairs of one-indexed integers, which represents a vertex
weights: A dictionary from [1.. len(E)] to integer weights

Output format is:

|V| |E|
v1 v2 w(1)
v3 v4 w(2)
...

The weights mutbe integers.

The vertices must start from 0.

More here
http://www.math.uwaterloo.ca/tsp/concorde/downloads/codes/src/970827/README
"""
def produceEdgFormat(V, E, weights, allowNonintegerWeights=False):
	print(len(V), len(E))
	for i,(a,b) in enumerate(E, 1):
		if i not in weights:
			weights[i] = 0
		elif not allowNonintegerWeights and weights[i] != int(weights[i]):
			raise NotImplementedError("Noninteger weight {} for edge {}".format(weights[i], (a,b)))
		print(a-1, b-1, weights[i])

