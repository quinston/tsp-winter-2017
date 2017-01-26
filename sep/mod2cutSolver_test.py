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
		answer = scipy.sparse.dok_matrix([[1], [1]])
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)

		Ab = scipy.sparse.dok_matrix([[1, 1], [1, 0]])
		answer = scipy.sparse.dok_matrix([[1, 1], [0, 1]])
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)

		Ab = scipy.sparse.dok_matrix([[1,1,0,1,1], [1,0,1,0,1], [1,0,1,0,0]])
		answer = scipy.sparse.dok_matrix([[1,0,1,0,1], [0,1,1,1,0], [0,0,0,0,1]])
		# See to it that they differ nowhere
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)

		Ab = scipy.sparse.dok_matrix([[1,1,0,1,1], [1,1,0,1,0], [1,0,0,0,0], [1,0,0,0,0]])
		answer = scipy.sparse.dok_matrix([[1,0,0,0,0], [0,1,0,1,1], [0,0,0,0,1], [0,0,0,0,0]])
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)

		Ab = scipy.sparse.dok_matrix([[1,0,1,1,1],[1,0,1,0,1],[1,0,0,1,1]])
		answer = scipy.sparse.dok_matrix([[1,0,0,0,1],[0,0,1,0,0],[0,0,0,1,0]])
		self.assertEqual((mod2cutSolver.mod2rref(Ab.copy()) - answer).nnz, 0)
	
	def test_mod2cpBasis(self):
		self.maxDiff = None
		
		Ab = scipy.sparse.dok_matrix([[1,0,0,0,0], [0,1,0,1,0], [0,0,0,0,1], [0,0,0,0,0]])
		answer = []
		self.assertEqual(mod2cutSolver.mod2cpBasis(Ab), [])

		Ab = scipy.sparse.dok_matrix([[1,0,0,0,0,1,1],[0,1,0,1,0,0,1],[0,0,0,0,1,1,1]], dtype='b')
		answer = [scipy.sparse.dok_matrix([[1,1,0,0,1,0]], dtype='b').transpose(),
[
	scipy.sparse.dok_matrix([[0,0,1,0,0,0]], dtype='b').transpose(),
	scipy.sparse.dok_matrix([[0,1,0,1,0,0]], dtype='b').transpose(), 
	scipy.sparse.dok_matrix([[1,0,0,0,1,1]], dtype='b').transpose()
]]
		output = mod2cutSolver.mod2cpBasis(Ab)
		print output[1]

		self.assertEqual((output[0] - answer[0]).nnz, 0)
		self.assertEqual((output[1][0] - answer[1][0]).nnz, 0)
		self.assertEqual((output[1][1] - answer[1][1]).nnz, 0)
		self.assertEqual((output[1][2] - answer[1][2]).nnz, 0)
