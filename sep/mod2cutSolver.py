#!/usr/bin/env python
import scipy.sparse
import cplex
from cplex.exceptions import CplexError
import inequalities
import numpy
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)


try:
	xrange
except NameError:
	xrange = range

"""
Ab: (A|b) the constraints and rhs put together in a dok_matrix. Modifies this in-place
"""
def mod2rref(Ab):
	Ab = Ab.todense() % 2


	# Gauss Jordan elimination
	noRows, noColumns = Ab.shape
	currentPivotRow = 0
	# Don't go all the way to the end, that's b
	for numColumn in xrange(noColumns - 1):
		#print("On column {}".format(numColumn))
		for numRow in xrange(currentPivotRow, noRows):
			if Ab[numRow, numColumn] == 1:
				pivot = numRow
				pivotRow = Ab[pivot, :].copy()


				# Add this row to all other rows with 1 in this position
				rowIndicesToAddPivotRowTo = [i for i in xrange(noRows) if i != pivot and Ab[i, numColumn] == 1]

				for index in rowIndicesToAddPivotRowTo:
					Ab[index, :] = (Ab[index, :] + pivotRow) % 2

				# Bring pivot row to top
				Ab[numRow, :] = Ab[currentPivotRow, :]
				Ab[currentPivotRow, :] = pivotRow

				currentPivotRow += 1
				break

	return Ab
	# return scipy.sparse.dok_matrix(Ab)

"""
Returns [a, [b1, b2, ...]]

where a is the affine offset and b1, b2, ... are the bases of the solution space


Returns [] if infeasible
"""
def mod2cpBasis(Ab):
	noRows, noColumns = Ab.shape
	noVariables = noColumns - 1
	Ab = mod2rref(Ab)

	# Check for infeasibility (0s in A, 1 in b)
	isInfeasible = False
	for numRow in xrange(noRows):
		if (not Ab[numRow, :noVariables].any()) and Ab[numRow, noVariables] == 1:
			isInfeasible = True
			break

	if isInfeasible:
		return []

	"""
	Read off the solution like this:
	( .... 1 ... 1 0 1 0 ... | 1 )

	The affine offset is the RHS padded with (noColumns - noRows) many 0s

	Each column with a row-leading one is a pivot variable and has affine offset from RHS
	Each column without a row-leading one is a free variable and has affine offset 0: read down the column to see dependence with the pivot variables; put 1 in place corresponding to free variable
	"""


	pivotVariables = set()
	currentPivotRow = 0
	# Don't go all the way to b
	for i in xrange(noVariables):
		if Ab[currentPivotRow, i] == 1:
			pivotVariables.add(i)
			currentPivotRow += 1
			if currentPivotRow == noRows:
				break

	# Trim the zero rows
	Ab = numpy.resize(Ab, (currentPivotRow, noColumns))

	rhs = Ab[:, noVariables]

	pivotVariablesToRowNumbers = dict((b,a) for a,b in enumerate(sorted(list(pivotVariables))))
	affineOffset = numpy.zeros((noVariables, 1), dtype='b')
	for i in xrange(noVariables):
		if i in pivotVariables:
			affineOffset[i, 0] = rhs[pivotVariablesToRowNumbers[i]]

	basis = []
	noFreeVariables = noVariables - len(pivotVariables)
	for i in xrange(noVariables):
		if i not in pivotVariables:
			base = numpy.zeros((noVariables, 1), dtype='b')
			base[i, 0] = 1
			for numColumn, numRow in pivotVariablesToRowNumbers.items():
				base[numColumn, 0] = Ab[numRow, i]
			basis.append(base)
	
	return [affineOffset, basis]


def mod2cutsLoop(vertices, edges, dualVertices, dualEdges, vinf, weights=None):
	Ab = inequalities.makeSparseExtendedLpMatrix(vertices, edges, dualVertices, dualEdges, vinf, includeBounds=True)

	A = Ab[:, :(Ab.shape[1] - 1)]
	b = Ab[:, (Ab.shape[1] - 1)]

	variableNames = inequalities.enumerateExtendedLpVariables(vertices, edges, dualVertices, dualEdges, vinf)
	noVariables = len(variableNames)

	def sparselyLabel(v):
		return [(a,b) for a,b in zip(variableNames, v) if b != 0]

	def rowToSparsePair(row):
		return cplex.SparsePair(ind = [name for i,name in enumerate(variableNames) if row[i] != 0], val = [x for x in row if x != 0])

	def dokRowToSparsePair(row):
		return cplex.SparsePair(ind = [name for i,name in enumerate(variableNames) if row[0, i] != 0], 
val = [int(row[i]) for i in sorted(row.keys())])

	def matrixRowToSparsePair(row):
		return cplex.SparsePair(ind = [name for i,name in enumerate(variableNames) if row[0, i] != 0],
val = [row[0, i] for i in range(row.shape[1]) if row[0,i] != 0])

	if weights == None:
		objectiveFunction = [1] * len(edges) + [0] * (len(variableNames) - len(edges))
	else:
		objectiveFunction = [weights[e] for e in edges] + [0] * (len(variableNames) - len(edges))

	polytopeProb = cplex.Cplex()
	try:
		polytopeProb.objective.set_sense(polytopeProb.objective.sense.minimize)
		polytopeProb.variables.add(names = variableNames, 
			obj = objectiveFunction,
			lb = [0] * len(variableNames))

		for numRow in range(Ab.shape[0]):
			if numRow % 100 ==0:
				logging.info("Added constraint {}".format(numRow))
			polytopeProb.linear_constraints.add(lin_expr = [dokRowToSparsePair(A[numRow, :])], rhs = [b[numRow, 0]], senses = 'L')
		

		polytopeProb.solve()
		if not polytopeProb.solution.is_primal_feasible():
			logging.info('Original subtour polytope is empty')
			return

		pointToSeparate = polytopeProb.solution.get_values()
		logging.info('Initial point: {}'.format(sparselyLabel(pointToSeparate)))
		logging.info('Objective value: {}'.format(polytopeProb.get_objective_value()))

		""" 
		The equations that x* satisfies tightly are all the equations, and
		all the inequalities where x*_e or z*_e,v is 0

		We will call this the equational support of x*
		"""

		noOriginalConstraints = A.shape[0]
		# This counts the number of equations in the extended formulation, times 2 for <= and >=
		noAlwaysTightInequalities = noOriginalConstraints - noVariables

		while True:
			# This will hold (A|b)^T
			systemAb = scipy.sparse.dok_matrix((A.shape[1] + 1, A.shape[0]))

			systemAb[:, :(noAlwaysTightInequalities // 2)] = scipy.sparse.vstack(
				[
					# ::2 is for skipping all the double inequalities (which lead to equality)
					A[:noAlwaysTightInequalities:2, :].transpose(), 
					b[:noAlwaysTightInequalities:2, :].transpose()
				], format='coo')


			numConstraint = noAlwaysTightInequalities 
			numColumnInSystemAb = noAlwaysTightInequalities // 2
			while numConstraint < noOriginalConstraints:
				# Do not use constraints where x or z is nonzero
				if pointToSeparate[numConstraint - noAlwaysTightInequalities] == 0:
					systemAb[:noVariables, numColumnInSystemAb] = A[numConstraint, :].transpose()
					systemAb[noVariables, numColumnInSystemAb] = b[numConstraint, 0]
					numColumnInSystemAb += 1
				numConstraint += 1

			# Throw away remaining unused columns
			systemAb.resize((systemAb.shape[0], numColumnInSystemAb))

			# Convert to coo
			systemAb = systemAb.tocoo()

			# Add rhs: 0s everywhere except a 1 for b
			systemToSolve = scipy.sparse.hstack([
				systemAb, 
				scipy.sparse.coo_matrix(([1], ([systemAb.shape[0] - 1], [0])), shape=(systemAb.shape[0], 1))
			], format='coo')

			basis = mod2cpBasis(systemToSolve)

			# No more mod-2 cuts
			if basis == []:
				break
			else:

				# Takes a list of the form [0,1,0,0,1,0,1,0]
				# and returns equation/inequality labels
				def labelMod2Cut(v):
					labels = ["e{}".format(i) for i,e in enumerate(edges, 1) if vinf not in e] + ["f{}".format(i) for i,f in enumerate(dualVertices, 1) if vinf not in f] + ["v{}".format(i) for i in range(1, len(vertices) + 1)]+ [xVariable for i,xVariable in enumerate(variableNames) if xVariable[0] == "x" and pointToSeparate[i] == 0] + [zVariable for i,zVariable in enumerate(variableNames) if zVariable[0] == "z" and pointToSeparate[i] == 0]
					return [a for a,b in zip(labels, v) if b != 0]

				logging.info("Making cuts")

				# Add cut from affine offset
				cutAndDistance = systemAb.dot(basis[0])
				cut = cutAndDistance[:noVariables, 0].transpose()
				# round down RHS
				distance = cutAndDistance[noVariables, 0] - 1

				logging.info("{} <= {}".format(sparselyLabel(cut.tolist()), distance))

				logging.info("Decomposition: {}".format(labelMod2Cut(basis[0].transpose().tolist()[0])))
				
				polytopeProb.linear_constraints.add(lin_expr=[rowToSparsePair(cut)], rhs=[distance], senses='L')

				# Add cut for each basis vector
				for basisVector in basis[1]:
					cutAndDistance = systemAb.dot(basis[0] + basisVector)
					cut = cutAndDistance[:noVariables, 0].transpose()
					distance = cutAndDistance[noVariables, 0] - 1

					logging.info("{} <= {}".format(sparselyLabel(cut.tolist()), distance))
					logging.info("Decomposition: {}".format(labelMod2Cut(basisVector.transpose().tolist()[0])))


					polytopeProb.linear_constraints.add(lin_expr=[rowToSparsePair(cut)], rhs=[distance], senses='L')

			polytopeProb.solve()

			if not polytopeProb.solution.is_primal_feasible():
				logging.info('Subtour polytope is empty')
				break

			pointToSeparate = polytopeProb.solution.get_values()
			logging.info('New point is {}'.format(sparselyLabel(pointToSeparate)))
			logging.info('Objective value {}'.format(polytopeProb.solution.get_objective_value()))

		logging.info('No more mod 2 cuts')


			
	except CplexError as e:
		raise e
