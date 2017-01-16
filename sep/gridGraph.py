
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

if __name__ == '__main__':
	gridWidth = int(sys.argv[1])
	V, E, Vstar, Estar = gridGraph(gridWidth)
	vinf = int(sys.argv[2])
	weights = dict(itertools.product(E, (1,)))

	def outputGridDisplayerFormat(filename, pt):
		with open(filename, 'w') as f:
			print(gridWidth, file=f)
			print(vinf, file=f)
			print(pt, file=f)

	import findTspCps
	i = 0
	for (cp, _, x) in findTspCps.findCps(V, E, Vstar, Estar, vinf, weights):
		outputGridDisplayerFormat("grid.cp{}".format(i), cp)
		outputGridDisplayerFormat("grid.point{}".format(i), x)

