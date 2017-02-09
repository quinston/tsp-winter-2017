import itertools
# k rows, l columns
def triangularGridGraph(k,l):
	V = list(range(1, k*l+1))
	E = list(itertools.chain(*[
[(a,a+1) for a in range(i*l + 1, (i+1)*l)] + [(a,b) for a,b in itertools.product(range(i*l+1, (i+1)*l+1), range((i+1)*l+1, (i+2)*l+1)) if (b-a) in [l,l+1]]
for i in range(k-1)
],
# last row
[(a,a+1) for a in range((k-1)*l + 1, k*l)]
))
	Vstar = list(itertools.chain(*[
list(itertools.chain(*[[(a, a+l, a+l+1), (a, a+1, a+l+1)] for a in range(i*l+1, (i+1)*l)]))
for i in range(k-1)
])) + [tuple(list(range(1,l+1)) + list(range(2*l, k*l+1, l)) + list(range(k*l-1, (k-1)*l, -1)) + list(range((k-2)*l + 1, 1, -l)))]

	infiniteFace = (k-1)*(2*(l-1)) + 1
	Estar = list(itertools.chain(*[
[(a, a-(2*l-1)) for a in range(2*(l-1)*i + 2, 2*(l-1)*(i+1) + 2, 2)] + [(2*(l-1)*i + 1, infiniteFace)] + [(a,a+1) for a in range(2*(l-1)*i + 1, 2*(l-1)*(i+1))] + [(2*(l-1)*(i+1), infiniteFace)]
for i in range(k-1)
],
[(a, infiniteFace) for a in range(2*(l-1)*(k-2) + 1, 2*(l-1)*(k-1), 2)]))
	# replace negative faces with infinteface (we were lazy)
	Estar = [(a,b) if b > 0 else (a,infiniteFace) for a,b in Estar]

	assert(len(Vstar)+len(V)-len(E)==2)
	assert(len(E) ==len(Estar))

	return (V,E,Vstar, Estar)

if __name__ == '__main__':
	import sys
	height = int(sys.argv[1])
	width = int(sys.argv[2])
	vinf = int(sys.argv[3])
	V,E,Vstar,Estar = triangularGridGraph(height, width)

	import random
	random.seed(0)

	weights = dict((e, random.randint(1, 10)) for i,e in enumerate(E, 1))

	import findTspCps
	for _,_,x in findTspCps.findCps(V,E,Vstar,Estar,vinf,weights):
		import concorde
		# Turn this [("x1", 0.3), ("x2", 0.4) ...] into {1: 0.3, 2: 0.4}
		concorde.produceEdgFormat(V, E, dict((int(a[1:]), b) for a,b in x if a[0] == "x"), allowNonintegerWeights=True)
		break

	"""
	import concorde
	concorde.produceEdgFormat(V, E, weights)
	"""
