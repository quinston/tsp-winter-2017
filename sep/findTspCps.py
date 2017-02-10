import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

# yields pairs (cp, distance, x) where cp*x <= distance is a cutting plane that cuts off x
# cp, x are sparse labelled vectors (i.e. list of 2-ples of label and value)

def findCps(vertices, edges, dualVertices, dualEdges, vinf, weights=None, 
forceXto0=False, forceXpositive=False, forceZto0=False, forceZpositive=False,
sparseCoefficients=True, unboundedCoefficients=False, halfInteger=False):
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
		objectiveFunction = [1] * len(variableNames)
	else:
		objectiveFunction = [weights[e] for e in edges] + [0] * (len(variableNames) - len(edges))

	polytopeProb = cplex.Cplex()
	try:
		polytopeProb.objective.set_sense(polytopeProb.objective.sense.minimize)

		logging.debug("Number of variables: %".format(len(variableNames)))
		
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

		#polytopeProb.set_results_stream(None)
		polytopeProb.write('polytope.lp')

		# For convenience, add binary section for the variables
		with open('polytope.lp', 'a') as f:
			print("Binary", file=f)
			print("\n".join(variableNames), file=f)

		polytopeProb.solve()
		if not polytopeProb.solution.is_primal_feasible():
			logging.error('Original subtour polytope is empty')
			return

		pointToSeparate = polytopeProb.solution.get_values()
		logging.info('Initial point: {}'.format(sparselyLabel(pointToSeparate)))

		def getPositiveSupport(x):
				return set((i+1) for i in range(len(x)) if x[i] > 0)

		# This function takes care of filling in a_{XX} <- u^T A_{XX} where we had previously omitted a_{XX} variables  from the CG-cut system due to no positive support in pointToSeparate
		def cpVectorFromProb(prob, pointToSeparate, A):
			u = [prob.solution.get_values('u{}'.format(i)) for i in range(1, len(A)+1)]
			uA = [(prob.solution.get_values('a{}'.format(i)) if i in getPositiveSupport(pointToSeparate) else sum(u[j] * row[i-1] for j,row in enumerate(A))) for i in range(1, len(variableNames) + 1)]
			floorUA = [math.floor(x) for x in uA]
			logging.debug("Variables that need flooring, and amount to floor: {}".format(sparselyLabel([a - b for a,b in zip(uA, floorUA)])))
			return floorUA


		originalNoEquations = len(A)
		noCuttingPlanes = 0
		cpViolation = 1e20
		d = 0.01
		while noCuttingPlanes == 0 or  cpViolation > d:
			positiveSupport = getPositiveSupport(pointToSeparate)
			cpProb = cgsep.makeCgLp(pointToSeparate, A, b, d)

			# Here we modify the default CGSEP programme for our educational purposes

			# force x_e = u^T A_j = 0 for cutting plane 
			if forceXto0:
				cpProb.linear_constraints.add(
						lin_expr = [cplex.SparsePair(ind=["u{}".format(i) for i in range(1, len(A)+1)], 
							val=[row[j-1] for row in A]) for j in range(1, len(edges)+1)],
						rhs=[0] * len(edges), 
						senses='E' * len(edges))

			# force (-z_e,v <= 0)  z_e,v >= 0
			if forceZpositive:
				cpProb.linear_constraints.add(
						lin_expr = [cplex.SparsePair(ind=["u{}".format(i) for i in range(1, len(A)+1)], 
							val=[row[j-1] for row in A]) for j in range(len(edges)+1, len(variableNames)+1)],
						rhs=[0] * (len(variableNames) - len(edges)), 
						senses='L' * (len(variableNames) - len(edges)))

			# force -x_e <= 0 (x_e >= 0)
			if forceXpositive:
				cpProb.linear_constraints.add(
						lin_expr = [cplex.SparsePair(ind=["u{}".format(i) for i in range(1, len(A)+1)], 
							val=[row[j-1] for row in A]) for j in range(1, len(edges)+1)],
						rhs=[0] * len(edges), 
						senses='L' * len(edges))

			# force  z_e,v = 0
			if forceZto0:
				cpProb.linear_constraints.add(
						lin_expr = [cplex.SparsePair(ind=["u{}".format(i) for i in range(1, len(A)+1)], 
							val=[row[j-1] for row in A]) for j in range(len(edges)+1, len(variableNames)+1)],
						rhs=[0] * (len(variableNames) - len(edges)), 
						senses='E' * (len(variableNames) - len(edges)))

			# only accept rank 1 chvatal cuts
			cuttingPlaneIndices = range(originalNoEquations + 1, originalNoEquations + noCuttingPlanes + 1)
			cpProb.linear_constraints.add(
					lin_expr = [cplex.SparsePair(ind=["u{}".format(i) for i in cuttingPlaneIndices],
						val=[1 for i in cuttingPlaneIndices])],
						rhs=[0],
						senses='E')

			# don't care about sparse combinations
			if sparseCoefficients:
				cpProb.objective.set_linear([("u{}".format(i), 0) for i in range(1, len(A)+1)])

			# allow arbitrary coefficients
			if unboundedCoefficients:
				cpProb.variables.set_upper_bounds([("u{}".format(i), cplex.infinity) for i in range(1, len(A)+1)])

			# only allow half-integer coefficients (0 or 1/2)
			if halfInteger:
				# cpProb.variables.set_upper_bounds([("u{}".format(i), cplex.infinity) for i in range(1, len(A)+1)])
				# Add integer variables v_i, and then let u_i = v_i/2
				cpProb.variables.add(obj = [0] * len(A), types = [cpProb.variables.type.integer] * len(A), names =["v{}".format(i) for i in range(1, len(A)+1)])
				for i in range(1, len(A)+1): 
					cpProb.linear_constraints.add(
						lin_expr = [cplex.SparsePair(ind=["u{}".format(i), "v{}".format(i)],
						val = [1, -0.5])],
						rhs = [0],
						senses = 'E')

			cpProb.write('cg.cut{}.lp'.format(noCuttingPlanes))
	
			#cpProb.set_results_stream(None)
			logging.debug("Finding a cutting plane...")
			cpProb.solve()
	
			cpVector = [x for x in cpVectorFromProb(cpProb, pointToSeparate, A)]
			cpLabelledVector = sparselyLabel(cpVector)
			if len(cpLabelledVector) == 0:
				logging.info("Done")
				yield ([], 0, sparselyLabel(pointToSeparate))
				break
			cpDistance = cpProb.solution.get_values()[0]

			cpViolation = sum([c * x for c,x in zip(cpVector, pointToSeparate)]) - cpDistance 

			logging.info("Found cutting plane: {}".format(cpLabelledVector))
			# print a0
			logging.info("Found cutting plane: <= {}".format(cpDistance))
			logging.info("Linear combination is: \n{}".format("+\n".join("{} * {})".format(cpProb.solution.get_values("u{}".format(j)), sparselyLabel(row)) for j,row in enumerate(A, 1) if cpProb.solution.get_values("u{}".format(j)) != 0)))
			logging.info("Violation: {}".format(cpViolation))

			yield (cpLabelledVector, cpDistance, sparselyLabel(pointToSeparate))


			A += [cpVector]
			b += [cpDistance]

			polytopeProb.linear_constraints.add(
					lin_expr = [rowToSparsePair(cpVector)], 
					rhs = [cpDistance],
					senses = 'L')

			#polytopeProb.set_results_stream(None)
			noCuttingPlanes += 1
			polytopeProb.write('polytope.cut{}.lp'.format(noCuttingPlanes))
			polytopeProb.solve()

			if not polytopeProb.solution.is_primal_feasible():
				logging.error("Problem no longer feasible, outputing to polytope.infeasible.lp")
				polytopeProb.write('polytope.infeasible.lp')
				break


			pointToSeparate = polytopeProb.solution.get_values()
			logging.info("New point to separate: {}".format(sparselyLabel(pointToSeparate)))
			logging.info("Objective value: {}".format(polytopeProb.solution.get_objective_value()))



	except CplexError as e:
		print(e, file=sys.stderr)
		raise e

