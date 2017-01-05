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

	def test_makeCplex(self):
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
		self.assertEqual(inequalities.makeCplex(range(1, 4+1), [(1,2), (1,3), (2,3), (2,4)]),
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

		self.assertEqual(inequalities.makeCplex(range(1, 4+1), [(1,2), (1,3), (2,3), (2,4)],
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

if __name__ == '__main__':
	unittest.main()
