

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

		pointToSeparate = polytopeProb.solution.get_values()

		# This function takes care of filling in 0s where we have no aXX variables due to lack of support in pointToSeparate
		def cpVectorFromProb(prob, pointToSeparate):
			positiveSupport = set((i+1) for i in range(len(pointToSeparate)) if pointToSeparate[i] > 0)
			return [(prob.solution.get_values('a{}'.format(i)) if i in positiveSupport else 0) for i in range(1, len(variableNames) + 1)]

		# Create a list of pairs omitting zero entries 
		def sparselyLabel(v):
			return [(a,b) for a,b in zip(variableNames, v) if b != 0]

		firstTime = True 
		cpViolation = 1e20
		while firstTime or  cpViolation > 1e-5:
			firstTime = False 

			cpProb = cgsep.makeCgLp(pointToSeparate, A, b, 0.01)
	
			cpProb.set_results_stream(None)
			cpProb.solve()
			cpProb.write('cg.lp')
	
			cpVector = [x for x in cpVectorFromProb(cpProb, pointToSeparate)]
			cpLabelledVector = sparselyLabel(cpVector)
			cpDistance = cpProb.solution.get_values()[0]

			if cpProb.solution.get_objective_value() >  cpViolation:
				print("Violation went up...")
				break

			cpViolation = cpProb.solution.get_objective_value()

			print("Found cutting plane: ", cpLabelledVector)
			# print a0
			print("Found cutting plane: <=", cpDistance)
			print("Point {} violates it by {}".format(sparselyLabel(pointToSeparate), cpViolation))

			A += [cpVector]
			b += [cpDistance]

			polytopeProb.linear_constraints.add(
					lin_expr = [rowToSparsePair(cpVector)], 
					rhs = [cpDistance],
					senses = 'L')

			polytopeProb.set_results_stream(None)
			polytopeProb.solve()

			if not polytopeProb.solution.is_primal_feasible():
				print("Problem no longer feasible, outputing to bowtie.lp")
				polytopeProb.write('bowtie.lp')
				break


			pointToSeparate = polytopeProb.solution.get_values()
			print("New point to separate: ", sparselyLabel(pointToSeparate))
			print("Objective value: ", polytopeProb.solution.get_objective_value())

	except CplexError as e:
		print(e, file=sys.stderr)

