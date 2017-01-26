import unittest
import mod2cutSolver
import scipy.sparse

class TestMod2CutSolver(unittest.TestCase):
	def test_mod2rref(self):
		self.maxDiff = None

		Ab = scipy.sparse.dok_matrix([[1]])
		answer = scipy.sparse.dok_matrix([[1]])
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)

		Ab = scipy.sparse.dok_matrix([[1], [1]])
		answer = scipy.sparse.dok_matrix([[1], [0]])
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)

		Ab = scipy.sparse.dok_matrix([[1,1,0,1,1], [1,0,1,0,1], [1,0,1,0,0]])
		answer = scipy.sparse.dok_matrix([[1,0,1,0,0], [0,1,1,1,0], [0,0,0,0,1]])
		# See to it that they differ nowhere
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)
	
