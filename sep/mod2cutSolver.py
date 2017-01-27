#!/usr/bin/env python
import scipy.sparse
import cplex
from cplex.exceptions import CplexError
import inequalities

try:
	xrange
except NameError:
	xrange = range

"""
Ab: (A|b) the constraints and rhs put together in a dok_matrix. Modifies this in-place
"""
def mod2rref(Ab):
	# Reduce whole matrix mod 2
	for key in list(Ab.keys()):
		Ab[key] = Ab[key] % 2

	# Gauss Jordan elimination
	noRows, noColumns = Ab.shape
	currentPivotRow = 0
	# Don't go all the way to the end, that's b
	for numColumn in xrange(noColumns - 1):
		for numRow in xrange(currentPivotRow, noRows):
			if Ab[numRow, numColumn] == 1:
				pivot = numRow
				pivotRow = Ab.getrow(pivot)

				# Add this row to all other rows with 1 in this position
				# Recall + mod 2 is xor
				rowIndicesToAddPivotRowTo = [i for i in xrange(noRows) if i != pivot and Ab[i, numColumn] == 1]

				def symmetricDifference(row1, row2):
					try:
						return set(row1.keys()) ^ set(row2.keys())
					except AttributeError as e:
						print(dir(row1))
						print(dir(row2))
						raise e


				for index in rowIndicesToAddPivotRowTo:
					newRow = symmetricDifference(Ab[index, :], pivotRow)
					# Clear teh row
					Ab[index, :] = 0

					# Fill the row
					for k in newRow:
						Ab[index, k[1]] = 1

				# Bring pivot row to top
				Ab[numRow, :] = Ab[currentPivotRow, :]
				Ab[currentPivotRow, :] = pivotRow

				currentPivotRow += 1
				break

	return Ab

"""
Returns [a, [b1, b2, ...]]

where a is the affine offset and b1, b2, ... are the bases of the solution space


Returns [] if infeasible
"""
def mod2cpBasis(Ab):
	noRows, noColumns = Ab.shape
	noVariables = noColumns - 1
	mod2rref(Ab)

	# Check for infeasibility (0s in A, 1 in b)
	isInfeasible = False
	for numRow in xrange(noRows):
		if Ab[numRow, :noVariables].nnz == 0 and Ab[numRow, noVariables] == 1:
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
	Ab.resize((currentPivotRow, noColumns))

	rhs = Ab[:, noVariables]

	pivotVariablesToRowNumbers = dict((b,a) for a,b in enumerate(sorted(list(pivotVariables))))
	affineOffset = scipy.sparse.dok_matrix((noVariables, 1), 0, dtype='b')
	for i in xrange(noVariables):
		if i in pivotVariables:
			affineOffset[i, 0] = rhs[pivotVariablesToRowNumbers[i], 0]

	basis = []
	noFreeVariables = noVariables - len(pivotVariables)
	for i in xrange(noVariables):
		if i not in pivotVariables:
			base = scipy.sparse.dok_matrix((noVariables, 1), 0, dtype='b')
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

	Alol = [dokRowToSparsePair(A[i, :]) for i in xrange(A.shape[0])]
	bList = [int(b[i, 0]) for i in range(b.shape[0])]

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

		polytopeProb.linear_constraints.add(lin_expr = Alol, rhs = bList, senses = 'L' * len(bList))
		

		polytopeProb.solve()
		if not polytopeProb.solution.is_primal_feasible():
			print('Original subtour polytope is empty')
			return

		pointToSeparate = polytopeProb.solution.get_values()
		print('Initial point: {}'.format(sparselyLabel(pointToSeparate)))

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

			systemAb[:, :noAlwaysTightInequalities] = scipy.sparse.vstack(
				[
					A[:noAlwaysTightInequalities, :].transpose(), 
					b[:noAlwaysTightInequalities, :].transpose()
				], format='dok')

			numConstraint = noAlwaysTightInequalities
			numColumnInSystemAb = noAlwaysTightInequalities
			while numConstraint < noOriginalConstraints:
				# Do not use constraints where x or z is nonzero
				if pointToSeparate[numConstraint - noAlwaysTightInequalities] == 0:
					systemAb[:noVariables, numColumnInSystemAb] = A[numConstraint, :].transpose()
					systemAb[noVariables, numColumnInSystemAb] = b[numConstraint, 0]
					numColumnInSystemAb += 1
				numConstraint += 1

			# Throw away remaining unused columns
			systemAb.resize((systemAb.shape[0], numColumnInSystemAb))

			# Add rhs: 0s everywhere except a 1 for b
			systemToSolve = scipy.sparse.hstack([
				systemAb, 
				scipy.sparse.coo_matrix(([1], ([systemAb.shape[0] - 1], [0])), shape=(systemAb.shape[0], 1))
			], format='dok')

			basis = mod2cpBasis(systemToSolve)

			# No more mod-2 cuts
			if basis == []:
				break
			else:
				listOfLhs = []
				rhs = []

				# Add cut from affine offset
				cutAndDistance = systemAb.dot(basis[0])
				cut = cutAndDistance[:noVariables, 0].transpose()
				# round down RHS
				distance = cutAndDistance[noVariables, 0] - 1
				
				listOfLhs.append(matrixRowToSparsePair(cut))
				rhs.append(distance)

				# Add cut for each basis vector
				for basisVector in basis[1]:
					cutAndDistance = systemAb.dot(basis[0] + basisVector)
					cut = cutAndDistance[:noVariables, 0].transpose()
					distance = cutAndDistance[noVariables, 0] - 1

					listOfLhs.append(matrixRowToSparsePair(cut))
					rhs.append(distance)

			polytopeProb.linear_constraints.add(lin_expr=listOfLhs, rhs=rhs, senses='L' * len(rhs))
			polytopeProb.solve()

			if not polytopeProb.solution.is_primal_feasible():
				print('Subtour polytope is empty')

			pointToSeparate = polytopeProb.solution.get_values()
			print('New point is {}'.format(sparselyLabel(pointToSeparate)))


			
	except CplexError as e:
		raise e
