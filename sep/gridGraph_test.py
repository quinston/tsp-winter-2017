import gridGraph
import unittest

class TestGridGraph(unittest.TestCase):
	def test_gridGraph(self):
		self.maxDiff = None
		self.assertEqual(gridGraph.gridGraph(3),
(
[1,2,3,4,5,6,7,8,9],
[(1,2),(2,3),(1,4),(2,5),(3,6),(4,5),(5,6),(4,7),(5,8),(6,9),(7,8),(8,9)],
[(1,2,4,5), (2,3,5,6), (4,5,7,8), (5,6,8,9), (1,2,3,6,9,8,7,4)],
[(1,5),(2,5),(1,5),(1,2),(2,5),(1,3),(2,4),(3,5),(3,4),(4,5),(3,5),(4,5)]
))

		self.assertEqual(gridGraph.gridGraph(4),
(
[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
[
(1,2),(2,3),(3,4),(1,5),(2,6),(3,7),(4,8),(5,6),(6,7),(7,8),(5,9),(6,10),(7,11),(8,12),(9,10),(10,11),(11,12),(9,13),(10,14),(11,15),(12,16),(13,14),(14,15),(15,16)
],
[(1,2,5,6), (2,3,6,7), (3,4,7,8), (5,6,9,10), (6,7,10,11), (7,8,11,12), (9,10,13,14), (10,11,14,15), (11,12,15,16), (1,2,3,4,8,12,16,15,14,13,9,5)],
[(1,10), (2,10), (3,10),
(1,10), (1,2), (2,3), (3, 10),
(1,4), (2,5), (3,6),
(4,10), (4,5), (5,6), (6,10),
(4, 7), (5,8), (6,9),
(7,10),(7,8),(8,9),(9,10),
(7,10),(8,10),(9,10)]
))

		self.assertEqual(gridGraph.gridGraph(5),
(
list(range(1,25+1)),
[(a,a+1) for a in range(1, 4+1)] + [(a,a+5) for a in range(1,5+1)] +[(a,a+1) for a in range(6,9+1)] +[(a,a+5) for a in range(6,10+1)] +[(a,a+1) for a in range(11, 14+1)] +[(a,a+5) for a in range(11, 15+1)]  +[(a,a+1) for a in range(16,19+1)] + [(a, a+5) for a in range(16,20+1)] +[(a,a+1) for a in range(21, 24+1)], 
[(a,a+1,a+5,a+6) for a in range(1,4+1)] +[(a,a+1,a+5,a+6) for a in range(6, 9+1)] +[(a,a+1,a+5,a+6) for a in range(11,14+1)] +[(a,a+1,a+5,a+6) for a in range(16, 19+1)] +[(1,2,3,4,5,10,15,20,25,24,23,22,21,16,11,6)],
[(a, 17) for a in range(1,4+1)] + [(1,17)] + [(a-1, a) for a in range(2,4+1)] + [(4,17)] + [(a,a+4) for a in range(1,4+1)] + [(5,17)] + [(a-1, a) for a in range(6,8+1)] + [(8,17)] + [(a,a+4) for a in range(5,8+1)] + [(9,17)] + [(a-1, a) for a in range(10,12+1)] + [(12,17)] + [(a,a+4) for a in range(9,12+1)] + [(13,17)] + [(a-1, a) for a in range(14,16+1)] + [(16,17)] + [(a,17) for a in range(13,16+1)]))


	def test_gridGraphEulersFormula(self):
		V, E, Vstar, Estar = gridGraph.gridGraph(5)
		self.assertEqual(len(V), 25)
		self.assertEqual(len(E), 4+5+4+5+4+5+4+5+4)
		self.assertEqual(len(Vstar), 17)
		self.assertEqual(len(Estar), len(E))
		self.assertEqual(len(V)-len(E)+len(Vstar), 2)
