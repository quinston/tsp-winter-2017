

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
		polytopeProb.write('polytope.lp')
		polytopeProb.solve()
		if not polytopeProb.solution.is_primal_feasible():
			print('Original subtour polytope is empty')
			return

		pointToSeparate = polytopeProb.solution.get_values()
		print('Initial point: {}'.format(sparselyLabel(pointToSeparate)))

		def getPositiveSupport(x):
				return set((i+1) for i in range(len(x)) if x[i] > 0)

		# This function takes care of filling in a_{XX} <- u^T A_{XX} where we had previously omitted a_{XX} variables  from the CG-cut system due to no positive support in pointToSeparate
		def cpVectorFromProb(prob, pointToSeparate, A):
			u = [prob.solution.get_values('u{}'.format(i)) for i in range(1, len(A)+1)]
			return [(prob.solution.get_values('a{}'.format(i)) if i in getPositiveSupport(pointToSeparate) else math.floor(sum(u[j] * row[i-1] for j,row in enumerate(A)))) for i in range(1, len(variableNames) + 1)]


		noCuttingPlanes = 0
		cpViolation = 1e20
		d = 0.01
		while noCuttingPlanes == 0 or  cpViolation > d:
			positiveSupport = getPositiveSupport(pointToSeparate)
			cpProb = cgsep.makeCgLp(pointToSeparate, A, b, d)

			# Here we modify the default CGSEP programme for our educational purposes


			# force x_e = u^T A_j = 0 for cutting plane 
			cpProb.linear_constraints.add(
					lin_expr = [cplex.SparsePair(ind=["u{}".format(i) for i in range(1, len(A)+1)], 
						val=[row[j-1] for row in A]) for j in range(1, len(edges)+1)],
					rhs=[0] * len(edges), 
					senses='E' * len(edges))

			# force (-z_e,v <= 0)  z_e,v >= 0
			cpProb.linear_constraints.add(
					lin_expr = [cplex.SparsePair(ind=["u{}".format(i) for i in range(1, len(A)+1)], 
						val=[row[j-1] for row in A]) for j in range(len(edges)+1, len(variableNames)+1)],
					rhs=[0] * (len(variableNames) - len(edges)), 
					senses='L' * (len(variableNames) - len(edges)))


			"""
			# disincentivize original variables x_e, incentivize new variables z_e,v
			# when a_k is negative, it gets floored to a nonzero negative number, which
			# becomes positive when we flip the inequality
			# when a_k is positive, it gets floored to 0
			cpProb.variables.add(names=["v{}".format(i) for i in positiveSupport], 
					obj=[(-1e-3 if i <= len(edges) else +1e-5) for i in positiveSupport],
					types=[cpProb.variables.type.binary] * len(positiveSupport))
			for i in positiveSupport:
				cpProb.indicator_constraints.add(indvar="v{}".format(i),
						lin_expr=cplex.SparsePair(ind=["a{}".format(i)], val=[1]),
						rhs = -d,
						sense="L")
			"""
                                

			cpProb.write('cg.lp')
	
			cpProb.set_results_stream(None)
			print("Finding a cutting plane...")
			cpProb.solve()
	
			cpVector = [x for x in cpVectorFromProb(cpProb, pointToSeparate, A)]
			cpLabelledVector = sparselyLabel(cpVector)
			if len(cpLabelledVector) == 0:
				print("Done")
				break
			cpDistance = cpProb.solution.get_values()[0]

			cpViolation = sum([c * x for c,x in zip(cpVector, pointToSeparate)]) - cpDistance 

			print("Found cutting plane: ", cpLabelledVector)
			# print a0
			print("Found cutting plane: <=", cpDistance)
			#print("Linear combination is: \n{}".format("+".join("{} * {})".format(cpProb.solution.get_values("u{}".format(j)), sparselyLabel(row)) for j,row in enumerate(A, 1) if cpProb.solution.get_values("u{}".format(j)) != 0)))
			# print("Point {} violates it by {}".format(sparselyLabel(pointToSeparate), cpViolation))

			A += [cpVector]
			b += [cpDistance]

			polytopeProb.linear_constraints.add(
					lin_expr = [rowToSparsePair(cpVector)], 
					rhs = [cpDistance],
					senses = 'L')

			polytopeProb.set_results_stream(None)
			noCuttingPlanes += 1
			polytopeProb.write('polytope.cut{}.lp'.format(noCuttingPlanes))
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

