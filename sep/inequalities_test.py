import unittest
import inequalities

"""
The test graph is K3 1-sum K2
"""

class TestInequalities(unittest.TestCase):
	def test_deltas(self):
		self.maxDiff = None
		self.assertEqual(
sorted(list(inequalities.deltas(range(1, 4+1),
[(1,2), (1,3), (2,3), (2,4)]
)),
# first sort by length, then by content
key=lambda x: (len(x[0]), x)),
[
((1,2), [(1,3), (2,3), (2,4)]),
((1,3), [(1,2), (2,3)]),
((1,4), [(1,2), (1,3), (2,4)]),
((2,3), [(1,2), (1,3), (2,4)]),
((2,4), [(1,2), (2,3)]),
((3,4), [(1,3), (2,3), (2,4)]),
]
)
		self.assertEqual(
sorted(list(inequalities.deltas(range(1, 4+1),
[(1,2), (1,3), (2,3), (2,4)],
usePlaceholders=True
)),
# first sort by length, then by content
key=lambda x: (len(x[0]), x)),
[
((1,2), [2,3,4]),
((1,3), [1,3]),
((1,4), [1,2,4]),
((2,3), [1,2,4]),
((2,4), [1,3]),
((3,4), [2,3,4]),
]
)

	def test_degreeConstarints(self):
		self.assertEqual(
sorted(list(inequalities.degreeConstraints(range(1, 4+1), [(1,2), (1,3), (2,3), (2,4)], usePlaceholders=True)), key=lambda x:(x[0], x)),
[
((1,), [1, 2]),
((2,), [1,3,4]),
((3,), [2,3]),
((4,), [4])
]
)


		self.assertEqual(
sorted(list(inequalities.degreeConstraints(range(1, 4+1), [(1,2), (1,3), (2,3), (2,4)], usePlaceholders=False)), key=lambda x:(x[0], x)),
[
((1,), [(1,2), (1,3)]),
((2,), [(1,2), (2,3), (2,4)]),
((3,), [(1,3), (2,3)]),
((4,), [(2,4)])
]
)

	def test_makeSepLp(self):
		"""
Here are the constraints for the graph E=[(1,2),(1,3),(2,3),(2,4)]

((1,), [(1,2), (1,3)]),
((2,), [(1,2), (2,3), (2,4)]),
((3,), [(1,3), (2,3)]),
((4,), [(2,4)]),
((1,2), [(1,3), (2,3), (2,4)]),
((1,3), [(1,2), (2,3)]),
((1,4), [(1,2), (1,3), (2,4)]),
((2,3), [(1,2), (1,3), (2,4)]),
((2,4), [(1,2), (2,3)]),
((3,4), [(1,3), (2,3), (2,4)]),
((1,2,3), [(2,4)]),
((1,2,4), [(1,3), (2,3)]),
((1,3,4), [(1,2), (2,3), (2,4)]),
((2,3,4), [(1,2), (1,3)])
]
"""
		self.assertEqual(inequalities.makeSepLp(range(1, 4+1), [(1,2), (1,3), (2,3), (2,4)]),
"""\
Minimize
x1 + x2 + x3 + x4
subject to
x1 + x2 = 2
x1 + x3 + x4 = 2
x2 + x3 = 2
x4 = 2
x2 + x3 + x4 >= 2
x1 + x3 >= 2
x1 + x2 + x4 >= 2
x1 + x2 + x4 >= 2
x1 + x3 >= 2
x2 + x3 + x4 >= 2
bounds
x1 >= 0
x2 >= 0
x3 >= 0
x4 >= 0""")

		"""
Retry with weights: 3.1 3.02 3.04 3.02
		"""

		self.assertEqual(inequalities.makeSepLp(range(1, 4+1), [(1,2), (1,3), (2,3), (2,4)],
{
(1,2): 3.1,
(1,3): 3.02,
(2,3): 3.04,
(2,4): 3.02
}),
"""\
Minimize
3.1x1 + 3.02x2 + 3.04x3 + 3.02x4
subject to
x1 + x2 = 2
x1 + x3 + x4 = 2
x2 + x3 = 2
x4 = 2
x2 + x3 + x4 >= 2
x1 + x3 >= 2
x1 + x2 + x4 >= 2
x1 + x2 + x4 >= 2
x1 + x3 >= 2
x2 + x3 + x4 >= 2
bounds
x1 >= 0
x2 >= 0
x3 >= 0
x4 >= 0""")

		"""Use a graph with V != E"""
		self.assertEqual(inequalities.makeSepLp(range(1, 4+1), [(1,2), (1,3), (2,3), (2,4), (3,4)],
{
(1,2): 3.1,
(1,3): 3.02,
(2,3): 3.04,
(2,4): 3.02,
(3,4): 3
}),
"""\
Minimize
3.1x1 + 3.02x2 + 3.04x3 + 3.02x4 + 3x5
subject to
x1 + x2 = 2
x1 + x3 + x4 = 2
x2 + x3 + x5 = 2
x4 + x5 = 2
x2 + x3 + x4 >= 2
x1 + x3 + x5 >= 2
x1 + x2 + x4 + x5 >= 2
x1 + x2 + x4 + x5 >= 2
x1 + x3 + x5 >= 2
x2 + x3 + x4 >= 2
bounds
x1 >= 0
x2 >= 0
x3 >= 0
x4 >= 0
x5 >= 0""")

	"""
Here is a different graph: K3 2-sum K3

E = 12 13 14 24 34
E* = 13 23 12 13 23
w = 2 2.1 2.05 1.95 1.96

Faces (boundary subgraphs) (boundary vertices):
d1: e1, e3, e4 ; p2, p1, p4
d2: e2, e3, e5 ; p3, p1, p4
d3: e1, e2, e4, e5 : p1, p2, p4, p3

"""
	def test_makeExtendedLp(self):
		self.maxDiff = None
		self.assertEqual(inequalities.makeExtendedLp(
range(1, 4+1), 
[(1,2), (1,3), (1,4), (2,4), (3,4)],
[(1,2,4), (1,3,4), (1,2,3,4)],
[(1,3), (2,3), (1,2), (1,3), (2,3)],
3
),
"""\
Minimize
x1 + x2 + x3 + x4 + x5
subject to
x1 + z1,1 + z1,3 = 1
x3 + z3,1 + z3,2 = 1
x4 + z4,1 + z4,3 = 1
z1,1 + z3,1 + z4,1 = 1
x1 + x2 + x3 = 2
x1 + x4 = 2
x2 + x5 = 2
x3 + x4 + x5 = 2
bounds
x1 >= 0
x2 >= 0
x3 >= 0
x4 >= 0
x5 >= 0
z1,1 >= 0
z1,3 >= 0
z3,1 >= 0
z3,2 >= 0
z4,1 >= 0
z4,3 >= 0""")

	def test_avoidBlankLinesInExtendedLp(self):
		V = range(1, 4+1)
		E = [(1,2),(1,3),(1,4),(2,4),(3,4)]
		Vstar = [(1,2,4), (1,3,4), (1,2,3,4)]
		Estar = [(1,3), (2,3), (1,2), (1,3), (2,3)]
		# avoid blank lines in constraints
		self.assertEqual(inequalities.makeExtendedLp(V, E, Vstar, Estar, 1),
"""\
Minimize
x1 + x2 + x3 + x4 + x5
subject to
x4 + z4,1 + z4,3 = 1
x5 + z5,2 + z5,3 = 1
x1 + x2 + x3 = 2
x1 + x4 = 2
x2 + x5 = 2
x3 + x4 + x5 = 2
bounds
x1 >= 0
x2 >= 0
x3 >= 0
x4 >= 0
x5 >= 0
z4,1 >= 0
z4,3 >= 0
z5,2 >= 0
z5,3 >= 0""")

	def test_makeExtendedLpConstraintMatrix(self):
		self.maxDiff = None

		V = range(1, 4+1) 
		E = [(1,2), (1,3), (1,4), (2,4), (3,4)]
		Vstar = [(1,2,4), (1,3,4), (1,2,3,4)]
		Estar = [(1,3), (2,3), (1,2), (1,3), (2,3)]

		"""\
		Minimize
		x1 + x2 + x3 + x4 + x5
		subject to
		x1 + z1,1 + z1,3 = 1
		x3 + z3,1 + z3,2 = 1
		x4 + z4,1 + z4,3 = 1
		z1,1 + z3,1 + z4,1 = 1
		x1 + x2 + x3 = 2
		x1 + x4 = 2
		x2 + x5 = 2
		x3 + x4 + x5 = 2
		bounds
		x1 >= 0
		x2 >= 0
		x3 >= 0
		x4 >= 0
		x5 >= 0
		z1,1 >= 0
		z1,3 >= 0
		z3,1 >= 0
		z3,2 >= 0
		z4,1 >= 0
		z4,3 >= 0"""


		self.assertEqual(inequalities.makeExtendedLpConstraintMatrix(V, E, Vstar, Estar, 3, includeBounds=True),
[
([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0], 1), # x1 + z1,1 + z1,3 = 1
([-1, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0], -1),
([0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0], 1), # x3 + z3,1 + z3,2 = 1
([0, 0, -1, 0, 0, 0, 0, -1, -1, 0, 0], -1), 
([0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1], 1), # x4 + z4,1 + z4,3 = 1
([0, 0, 0, -1, 0, 0, 0, 0, 0, -1, -1], -1), 
([0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0], 1),# z1,1 + z3,1 + z4,1 = 1
([0, 0, 0, 0, 0, -1, 0, -1, 0, -1, 0], -1),
([1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 2), # x1 + x2 + x3 = 2
([-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0], -2), 
([1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], 2), # x1 + x4 = 2
([-1, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0], -2), 
([0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0], 2), # x2 + x5 = 2
([0, -1, 0, 0, -1, 0, 0, 0, 0, 0, 0], -2), 
([0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0], 2), # x3 + x4 + x5 = 2
([0, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0], -2), 
([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0), # x1 >= 0
([0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0), # x2 >= 0
([0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0], 0), # x3 >= 0
([0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0], 0), # x4 >= 0
([0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0], 0), # x5 >= 0
([0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0], 0), # z1,1 >= 0
([0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0], 0), # z1,3 >= 0
([0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0], 0),# z3,1 >= 0
([0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0], 0),# z3,2 >= 0
([0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0], 0),# z4,1 >= 0
([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], 0) # z4,3 >= 0"""
])

	def test_getExtraVariables(self):
		# Gets rid of the only other face
		self.assertEqual(inequalities.getExtraVariables([(1,2), (1,3), (2,3)], [(1,2), (1,2), (1,2)], 1), {3: ["z3,1", "z3,2"]})
		self.assertEqual(inequalities.getExtraVariables([(1,2), (1,3), (2,3), (2,4), (3,4)], [(1,3), (1,3), (1,2), (2,3), (2,3)], 1), {3: ["z3,1", "z3,2"], 4: ["z4,2", "z4,3"], 5: ["z5,2", "z5,3"]})

	def test_enumerateExtendedLpVariables(self):
		V = range(1, 4+1) 
		E = [(1,2), (1,3), (1,4), (2,4), (3,4)]
		Vstar = [(1,2,4), (1,3,4), (1,2,3,4)]
		Estar = [(1,3), (2,3), (1,2), (1,3), (2,3)]
		vinf = 3

		"""\
		Minimize
		x1 + x2 + x3 + x4 + x5
		subject to
		x1 + z1,1 + z1,3 = 1
		x3 + z3,1 + z3,2 = 1
		x4 + z4,1 + z4,3 = 1
		z1,1 + z3,1 + z4,1 = 1
		x1 + x2 + x3 = 2
		x1 + x4 = 2
		x2 + x5 = 2
		x3 + x4 + x5 = 2
		bounds
		x1 >= 0
		x2 >= 0
		x3 >= 0
		x4 >= 0
		x5 >= 0
		z1,1 >= 0
		z1,3 >= 0
		z3,1 >= 0
		z3,2 >= 0
		z4,1 >= 0
		z4,3 >= 0"""
		
		self.assertEqual(inequalities.enumerateExtendedLpVariables(V, E, Vstar, Estar,vinf), ["x1", "x2", "x3", "x4", "x5", "z1,1", "z1,3", "z3,1", "z3,2", "z4,1", "z4,3"])

	def test_makeSparseExtendedLpMatrix(self):
		import scipy.sparse

		self.maxDiff = None

		V = range(1, 4+1) 
		E = [(1,2), (1,3), (1,4), (2,4), (3,4)]
		Vstar = [(1,2,4), (1,3,4), (1,2,3,4)]
		Estar = [(1,3), (2,3), (1,2), (1,3), (2,3)]
		vinf = 3

		answer = scipy.sparse.dok_matrix([
[1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1], # x1 + z1,1 + z1,3 = 1
[-1, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0, -1],
[0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1], # x3 + z3,1 + z3,2 = 1
[0, 0, -1, 0, 0, 0, 0, -1, -1, 0, 0, -1], 
[0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1], # x4 + z4,1 + z4,3 = 1
[0, 0, 0, -1, 0, 0, 0, 0, 0, -1, -1, -1], 
[0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],# z1,1 + z3,1 + z4,1 = 1
[0, 0, 0, 0, 0, -1, 0, -1, 0, -1, 0, -1],
[1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2], # x1 + x2 + x3 = 2
[-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -2], 
[1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2], # x1 + x4 = 2
[-1, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, -2], 
[0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2], # x2 + x5 = 2
[0, -1, 0, 0, -1, 0, 0, 0, 0, 0, 0, -2], 
[0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 2], # x3 + x4 + x5 = 2
[0, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0, -2], 
[-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # x1 >= 0
[0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # x2 >= 0
[0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0], # x3 >= 0
[0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0], # x4 >= 0
[0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0], # x5 >= 0
[0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0], # z1,1 >= 0
[0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0,  0], # z1,3 >= 0
[0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],# z3,1 >= 0
[0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0],# z3,2 >= 0
[0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0],# z4,1 >= 0
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0] # z4,3 >= 0"""
])

		attempt = inequalities.makeSparseExtendedLpMatrix(V, E, Vstar, Estar, vinf, includeBounds=True)
		self.assertEqual(attempt.shape, answer.shape)
		self.assertEqual((attempt - answer).nnz, 0)

	def test_makeSparseFaceColourNonnegativityMatrix(self):
		import scipy.sparse

		self.maxDiff = None

		# Just a theta graph of two triangles
		V = range(1,4+1)
		E = [(1,2), (1,3), (2,3), (2,4), (3,4)]
		Vstar = [(1,2,3), (2,3,4), (1,2,4,3)]
		Estar = [(1,3), (1,3), (1,2), (2,3), (2,3)]

		vinf = 1

		answer = scipy.sparse.dok_matrix([
			[0,0,0,0,0, 0,0,0,0,0,0, -1,0,0, 0,0,0,0,0,0,0,0,0,0, 0], # d1 >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,-1,0, 0,0,0,0,0,0,0,0,0,0, 0], # d2 >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,-1, 0,0,0,0,0,0,0,0,0,0, 0], # d3 >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, -1,0,0,0,0,0,0,0,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,-1,0,0,0,0,0,0,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,-1,0,0,0,0,0,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,-1,0,0,0,0,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,-1,0,0,0,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,0,-1,0,0,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,0,0,-1,0,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,0,0,0,-1,0,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,0,0,0,0,-1,0, 0], # c >= 0
			[0,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,0,0,0,0,0,-1, 0] # c >= 0
		])
		attempt = inequalities.makeSparseFaceColourNonnegativityMatrix(V, E, Vstar, Estar, vinf)

		self.assertEqual(answer.todense().tolist(), attempt.todense().tolist())

	def test_makeSparseFaceColourBidirectionallyBoundedGradientMatrix(self):
		import scipy.sparse
		self.maxDiff = None
		V = range(1,4+1)
		E = [(1,2), (1,3), (2,3), (2,4), (3,4)]
		Vstar = [(1,2,3), (2,3,4), (1,2,4,3)]
		Estar = [(1,3), (1,3), (1,2), (2,3), (2,3)]

		vinf = 1

		answer = scipy.sparse.dok_matrix([
			[-1,0,0,0,0, 0,0,0,0,0,0, 0,0,0, 1,1,0,0,0,0,0,0,0,0, 0], # c_e1,d1 + c_e1,d3 <= x_e1
			[0,-1,0,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,1,1,0,0,0,0,0,0, 0], # c_e2,d1 + c_e2,d3 <= x_e2
			[0,0,-1,0,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,1,1,0,0,0,0, 0], # c_e3,d1 + c_e3,d2 <= x_e3
			[0,0,0,-1,0, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,0,0,1,1,0,0, 0], # c_e4,d2 + c_e4,d3 <= x_e4
			[0,0,0,0,-1, 0,0,0,0,0,0, 0,0,0, 0,0,0,0,0,0,0,0,1,1, 0] # c_e5,d2 + c_e5,d3 <= x_e5
			])

		self.assertEqual(answer.todense().tolist(), inequalities.makeSparseFaceColourBidirectionallyBoundedGradientMatrix(V, E, Vstar, Estar, vinf).todense().tolist())


	def test_makeSparseFaceColourMatrix(self):
		import scipy.sparse

		self.maxDiff = None

		# Just a theta graph of two triangles
		V = range(1,4+1)
		E = [(1,2), (1,3), (2,3), (2,4), (3,4)]
		Vstar = [(1,2,3), (2,3,4), (1,2,4,3)]
		Estar = [(1,3), (1,3), (1,2), (2,3), (2,3)]

		vinf = 1

		answer = scipy.sparse.dok_matrix([
			[0,0,0,0,0, 0,0,0,0,0,0, 1,0,-1, -1,0,0,0,0,0,0,0,0,0, 0], # bd1 - bd3 <= c_e1,d1
			[0,0,0,0,0, 0,0,0,0,0,0, -1,0,1, 0,-1,0,0,0,0,0,0,0,0, 0], # bd3 - bd1 <= c_e1,d3
			[0,0,0,0,0, 0,0,0,0,0,0, 1,0,-1, 0,0,-1,0,0,0,0,0,0,0, 0], # bd1 - bd3 <= c_e2,d1
			[0,0,0,0,0, 0,0,0,0,0,0, -1,0,1, 0,0,0,-1,0,0,0,0,0,0, 0], # bd3 - bd1 <= c_e2,d3
			[0,0,0,0,0, 0,0,0,0,0,0, 1,-1,0, 0,0,0,0,-1,0,0,0,0,0, 0], # bd1 - bd2 <= c_e3,d1
			[0,0,0,0,0, 0,0,0,0,0,0, -1,1,0, 0,0,0,0,0,-1,0,0,0,0, 0], # bd2 - bd1 <= c_e3,d2
			[0,0,0,0,0, 0,0,0,0,0,0, 0,1,-1, 0,0,0,0,0,0,-1,0,0,0, 0], # bd2 - bd3 <= c_e4,d2
			[0,0,0,0,0, 0,0,0,0,0,0, 0,-1,1, 0,0,0,0,0,0,0,-1,0,0, 0], # bd3 - bd2 <= c_e4,d3
			[0,0,0,0,0, 0,0,0,0,0,0, 0,1,-1, 0,0,0,0,0,0,0,0,-1,0, 0], # bd2 - bd3 <= c_e5,d2
			[0,0,0,0,0, 0,0,0,0,0,0, 0,-1,1, 0,0,0,0,0,0,0,0,0,-1, 0], # bd3 - bd2 <= c_e5,d3
			])

		self.assertEqual(answer.todense().tolist(), inequalities.makeSparseFaceColourUnidirectionallyBoundedGradientMatrix(V, E, Vstar, Estar, vinf).todense().tolist())

	def test_getFaceColourVariableNames(self):
		Vstar = [(1,2,3), (2,3,4), (1,2,4,3)]
		Estar = [(1,3), (1,3), (1,2), (2,3), (2,3)]
		self.assertEqual(inequalities.getFaceColourVariableNames(Vstar, Estar),
				["b1","b2","b3","c1,1","c1,3","c2,1","c2,3","c3,1","c3,2","c4,2","c4,3","c5,2","c5,3"])
		

if __name__ == '__main__':
	unittest.main()
