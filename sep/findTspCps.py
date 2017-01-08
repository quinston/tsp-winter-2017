

def findCps(vertices, edges, dualVertices, dualEdges, vinf, weights=None):
	import sys
	import cplex
	from cplex.exceptions import CplexError
	import cgsep
	import inequalities

	variableNames = inequalities.enumerateExtendedLpVariables(vertices, edges, dualVertices, dualEdges, vinf)

	objectiveFunction = None
	if weights == None:
		objectiveFunction = [1] * len(edges)
	else:
		objectiveFunction = [weights[e] for e in edges] + [0] * (len(variableNames) - len(edges))

	polytopeProb = cplex.Cplex()
	try:
		polytopeProb.objective.set_sense(polytopeProb.objective.sense.minimize)
		
		polytopeProb.variables.add(names = variableNames,
				obj = objectiveFunction)
		Ab = inequalities.makeExtendedLpConstraintMatrix(vertices, edges, dualVertices, dualEdges, vinf)
		A = [row[0] for row in Ab]
		
		"""
		Turns a vector (row of constraint matrix) into a sparse pair
		"""
		def rowToSparsePair(row):
			return cplex.SparsePair(ind = [name for i,name in enumerate(variableNames) if row[i] != 0], val = [x for x in row if x != 0])

		Alol = [rowToSparsePair(row) for row in A]
		b = [row[1] for row in Ab]

		polytopeProb.linear_constraints.add(lin_expr = Alol, rhs = b, senses = 'L' * len(b)) 

		polytopeProb.solve()

		pointToSeparate = polytopeProb.solution.get_values()

		cpProb = cgsep.makeCgLp(pointToSeparate, A, b, 0.01)
		cpViolation = 1e20

		cpProb.solve()
		
		cpVector = cpProb.solution.get_values()[1:len(variableNames) + 1]
		# The variables for the cutting plane are of the form "a1, a2, ..., a10",
		# so just take the suffix and map it to a legible name
		# Also skip a0
		cpLabelledVector = list(zip([variableNames[int(internalVariableName[1:]) - 1] for internalVariableName in cpProb.variables.get_names()[1:] if internalVariableName[0] == 'a'],
				cpVector))
		cpDistance = cpProb.solution.get_values()[0]
		cpViolation = cpProb.solution.get_objective_value()

		while cpViolation > 1e-5:
			print("Found cutting plane: ", cpLabelledVector)
			# print a0
			print("Found cutting plane: <=", cpDistance)
			print("Point {} violates it by {}".format(pointToSeparate, cpViolation))

			# Returned cutting  plane is ax >= b, so we need to flip sign
			# if we want <=
			A += [[-x for x in cpVector]]
			b += [-cpDistance]
			polytopeProb.linear_constraints.add(
					lin_expr = [rowToSparsePair([-x for x in cpVector])], 
					rhs = [-cpDistance],
					senses = 'L')

			polytopeProb.solve()
			pointToSeparate = polytopeProb.solution.get_values()
			print("New point to separate: ", pointToSeparate)
			print("Objective value: ", polytopeProb.solution.get_objective_value())

			cpProb = cgsep.makeCgLp(pointToSeparate, A, b, 0.01)
			cpProb.solve()

			cpVector = cpProb.solution.get_values()[1:len(variableNames) + 1]
			# The variables for the cutting plane are of the form "a1, a2, ..., a10",
			# so just take the suffix and map it to a legible name
			# Also skip a0
			cpLabelledVector = list(zip([variableNames[int(internalVariableName[1:]) - 1] for internalVariableName in cpProb.variables.get_names()[1:] if internalVariableName[0] == 'a'],
					cpVector))
			cpDistance = cpProb.solution.get_values()[0]
			cpViolation = cpProb.solution.get_objective_value()

			print("Gap: ", cpViolation)




	except CplexError as e:
		print(e, file=sys.stderr)

