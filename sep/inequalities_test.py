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
)
		self.assertEqual(
sorted(list(inequalities.deltas(range(1, 4+1),
[(1,2), (1,3), (2,3), (2,4)],
usePlaceholders=True
)),
# first sort by length, then by content
key=lambda x: (len(x[0]), x)),
[
((1,), [1, 2]),
((2,), [1,3,4]),
((3,), [2,3]),
((4,), [4]),
((1,2), [2,3,4]),
((1,3), [1,3]),
((1,4), [1,2,4]),
((2,3), [1,2,4]),
((2,4), [1,3]),
((3,4), [2,3,4]),
((1,2,3), [4]),
((1,2,4), [2,3]),
((1,3,4), [1,3,4]),
((2,3,4), [1,2])
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

if __name__ == '__main__':
	unittest.main()
