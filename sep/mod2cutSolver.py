#!/usr/bin/env python
import scipy.sparse
import cplex
from cplex.exceptions import CplexError
import inequalities

"""
Ab: (A|b) the constraints and rhs put together in a dok_matrix. Modifies this in-place
"""
def mod2rref(Ab):
	# Reduce whole matrix mod 2
	for key, value in Ab.iteritems():
		Ab[key] = value % 2

	# Gauss Jordan elimination
	noRows, noColumns = Ab.shape
	currentPivotRow = 0
	for numColumn in range(noColumns):
		for numRow in range(currentPivotRow, noRows):
			if Ab[numRow, numColumn] == 1:
				pivot = numRow
				pivotRow = Ab.getrow(pivot)

				# Add this row to all other rows with 1 in this position
				# Recall + mod 2 is xor
				rowIndicesToAddPivotRowTo = [i for i in range(noRows) if i != pivot and Ab[i, numColumn] == 1]

				def symmetricDifference(row1, row2):
					return set(row1.iteritems()) ^ set(row2.iteritems())


				for index in rowIndicesToAddPivotRowTo:
					newRow = symmetricDifference(Ab[index, :], pivotRow)
					# Clear teh row
					Ab[index, :] = scipy.sparse.dok_matrix((1, noColumns))

					# Fill the row
					for k,v in newRow:
						Ab[index, k[1]] = 1

				# Bring pivot row to top
				Ab[numRow, :] = Ab[currentPivotRow, :]
				Ab[currentPivotRow, :] = pivotRow

				currentPivotRow += 1
				break

	return Ab



def mod2cutsLoop(vertices, edges, dualVertices, dualEdges, vinf, weights=None):
	Ab = inequalities.makeExtendedLpConstraintMatrix(vertices, edges, dualVertices, dualEdges, vinf)
	A = [row[0] for row in Ab]
	b = [row[1] for row in Ab]

	variableNames = inequalities.enumerateExtendedLpVariables(vertices, edges, dualVertices, dualEdges, vinf)

	def sparselyLabel(v):
		return [(a,b) for a,b in zip(variableNames, v) if b != 0]

	def rowToSparsePair(row):
		return cplex.SparsePair(ind = [name for i,name in enumerate(variableNames) if row[i] != 0], val = [x for x in row if x != 0])

	Alol = [rowToSparsePair(row) for row in A]

	if weights == None:
		objectiveFunction = [1] * len(edges)
	else:
		objectiveFunction = [weights[e] for e in edges] + [0] * (len(variableNames) - len(edges))

	polytopeProb = cplex.Cplex()
	try:
		polytopeProb.objective.set_sense(polytopeProb.objective.sense.minimize)
		polytopeProb.variables.add(names = variableNames, 
			obj = objectiveFunction,
			lb = [0] * len(variableNames))
		polytopeProb.linear_constraints.add(lin_expr = Alol, rhs = b, senses = 'L' * len(b))
		
		polytopeProb.solve()
		if not polytopeProb.solution.is_primal_feasible():
			print('Original subtour polytope is empty')
			return

		pointToSeparate = polytopeProb.solution.get_values()
		print('Initial point: {}'.format(sparselyLabel(pointToSeparate)))
		
		while True:
			pass
	except CplexError as e:
		raise e
