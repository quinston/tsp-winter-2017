
import itertools
import sys

"""
Makes a grid graph of dimension k by k
"""
def gridGraph(k):
	lastFace = (k-1)**2 + 1
	return (
		list(range(1, k*k+1)),
		list(itertools.chain(*[itertools.chain(*[
# left to right edges
			[(a, a+1) for a in range(k*i + 1, k*i + (k-1) + 1)],
# upper to lower edges
			[(a, a+k) for a in range(k*i + 1, k*i + k + 1)]
]) for i in range(k-1)])) + [(a, a+1) for a in range(k*(k-1)+1, k*(k-1) + (k-1) + 1)],
# don't forgrt the infinite face with vertices in clockwise order
		list(itertools.chain(*[[(a,a+1,a+k,a+k+1) for a in range(k*i + 1, k*i + (k-1) + 1)] for i in range(k-1)])) + [tuple(itertools.chain(range(1, k+1), range(k*2, k*(k-1)+1, k), range(k*k, (k-1)*k, -1), range((k-2)*k + 1, k, -k)))],
		list(itertools.chain(
# top to infinite face
[(a, lastFace) for a in range(1, (k-1)+1)],
# left to infinite face, left face to right face, right to infinite face
[(1, lastFace)] + [(a, a+1) for a in range(1, (k-2)+1)] + [(k-1, lastFace)],
# k-2 rows in between
*[
[(b-(k-1), b) for b in range(a, a + (k-1-1) + 1)] + [(a, lastFace)] + [(b, b+1) for b in range(a, a + (k-2-1) + 1)] + [(a + (k-2), lastFace)]
for a in range((k-1)+1, (k-1)*(k-1), k-1)
],
# bottom to infinite face
[(a, lastFace) for a in range((k-2) * (k-1) + 1, (k-1)*(k-1) + 1)]
))
)

"""
k rows by l columns
"""
def rectangularGridGraph(k, l):
	lastFace = (k-1)*(l-1) + 1
	return (
		list(range(1, k*l+1)),
		list(itertools.chain(*[itertools.chain(*[
# left to right edges
			[(a, a+1) for a in range(l*i + 1, l*i + (l-1) + 1)],
# upper to lower edges
			[(a, a+l) for a in range(l*i + 1, l*i + l + 1)]
]) for i in range(k-1)])) + [(a, a+1) for a in range(l*(k-1)+1, l*(k-1) + (l-1) + 1)],
# don't forgrt the infinite face with vertices in clockwise order
		list(itertools.chain(*[[(a,a+1,a+l,a+l+1) for a in range(l*i + 1, l*i + (l-1) + 1)] for i in range(k-1)])) + [tuple(itertools.chain(range(1, l+1), range(l*2, l*(k-1)+1, l), range(k*l, (k-1)*l, -1), range((k-2)*l + 1, l, -l)))],
		list(itertools.chain(
# top to infinite face
[(a, lastFace) for a in range(1, (l-1)+1)],
# left to infinite face, left face to right face, right to infinite face
[(1, lastFace)] + [(a, a+1) for a in range(1, (l-2)+1)] + [(l-1, lastFace)],
# k-2 rows in between
*[
[(b-(l-1), b) for b in range(a, a + (l-1-1) + 1)] + [(a, lastFace)] + [(b, b+1) for b in range(a, a + (l-2-1) + 1)] + [(a + (l-2), lastFace)]
for a in range((l-1) + 1, (k-1)*(l-1) + 1, l-1)
],
# bottom to infinite face
[(a, lastFace) for a in range((k-2) * (l-1) + 1, (k-1)*(l-1) + 1)]
))
)

if __name__ == '__main__':
	gridHeight = int(sys.argv[1])
	gridWidth = int(sys.argv[2])
	V, E, Vstar, Estar = rectangularGridGraph(gridHeight, gridWidth) 
	vinf = int(sys.argv[3])
	# weights = dict(itertools.product(E, (1,)))
	# weights[(1,2)] = weights[(1, gridWidth + 1)] = weights[(2, gridWidth + 2)] = weights[(gridWidth + 1, gridWidth + 2)] = 10

	import random
	weights = dict((e, random.random()) for e in E)

	print(weights)

	def outputGridDisplayerFormat(filename, pt):
		with open(filename, 'w') as f:
			print(gridHeight, file=f)
			print(gridWidth, file=f)
			print(vinf, file=f)
			print(pt, file=f)

	import findTspCps
	i = 0
	for (cp, _, x) in findTspCps.findCps(V, E, Vstar, Estar, vinf, weights, forceXpositive=True, forceZpositive=True):
		outputGridDisplayerFormat("grid.cp{}".format(i), [(a,-b) for a,b in cp])
		outputGridDisplayerFormat("grid.point{}".format(i), x)
		i += 1

