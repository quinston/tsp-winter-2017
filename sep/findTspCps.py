

def findCps(vertices, edges, dualVertices, dualEdges, vinf, weights=None):
	import sys
	import cplex
	from cplex.exceptions import CplexError
	import cgsep
	import inequalities
	import math

	variableNames = inequalities.enumerateExtendedLpVariables(vertices, edges, dualVertices, dualEdges, vinf)
	# Create a list of pairs omitting zero entries 
	def sparselyLabel(v):
		return [(a,b) for a,b in zip(variableNames, v) if b != 0]

	objectiveFunction = None
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

		polytopeProb.set_results_stream(None)
		polytopeProb.solve()
		if not polytopeProb.solution.is_primal_feasible():
			print('Original subtour polytope is empty, outputing to polytope.lp')
			polytopeProb.write('polytope.lp')
			return

		pointToSeparate = polytopeProb.solution.get_values()
		print('Initial point: {}'.format(sparselyLabel(pointToSeparate)))

		# This function takes care of filling in a_{XX} <- u^T A_{XX} where we had previously omitted a_{XX} variables  from the CG-cut system due to no positive support in pointToSeparate
		def cpVectorFromProb(prob, pointToSeparate, A):
			positiveSupport = set((i+1) for i in range(len(pointToSeparate)) if pointToSeparate[i] > 0)
			u = [prob.solution.get_values('u{}'.format(i)) for i in range(1, len(A)+1)]
			return [(prob.solution.get_values('a{}'.format(i)) if i in positiveSupport else math.floor(sum(u[j] * row[i-1] for j,row in enumerate(A)))) for i in range(1, len(variableNames) + 1)]


		firstTime = True 
		cpViolation = 1e20
		while firstTime or  cpViolation > 1e-5:
			firstTime = False 

			cpProb = cgsep.makeCgLp(pointToSeparate, A, b, 0.01)
			cpProb.write('cg.lp')
	
			cpProb.set_results_stream(None)
			print("Finding a cutting plane...")
			cpProb.solve()
	
			cpVector = [x for x in cpVectorFromProb(cpProb, pointToSeparate, A)]
			cpLabelledVector = sparselyLabel(cpVector)
			cpDistance = cpProb.solution.get_values()[0]

			cpViolation = cpProb.solution.get_objective_value()

			print("Found cutting plane: ", cpLabelledVector)
			# print a0
			print("Found cutting plane: <=", cpDistance)
			# print("Linear combination is: \n{}".format("+".join("{} * np.matrix({})".format(cpProb.solution.get_values("u{}".format(j+1)), row) for j,row in enumerate(A) if cpProb.solution.get_values("u{}".format(j+1)) != 0)))
			# print("Point {} violates it by {}".format(sparselyLabel(pointToSeparate), cpViolation))

			A += [cpVector]
			b += [cpDistance]

			polytopeProb.linear_constraints.add(
					lin_expr = [rowToSparsePair(cpVector)], 
					rhs = [cpDistance],
					senses = 'L')

			polytopeProb.set_results_stream(None)
			polytopeProb.solve()

			if not polytopeProb.solution.is_primal_feasible():
				print("Problem no longer feasible, outputing to polytope.lp")
				polytopeProb.write('polytope.lp')
				break


			pointToSeparate = polytopeProb.solution.get_values()
			print("New point to separate: ", sparselyLabel(pointToSeparate))
			print("Objective value: ", polytopeProb.solution.get_objective_value())

	except CplexError as e:
		print(e, file=sys.stderr)
		raise e

