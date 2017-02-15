import cplex
import sys
from cplex.exceptions import CplexError
import logging
import scipy.sparse
import numpy

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

"""
Computes if x is in the split closure (pi, p_0)
If the optimum is ngeative, then  alpha^T x >= alpha_0 is 
a cutting plane valid for the split closure.

min alpha^T x - alpha_0 

alpha =  u^T A + s - u_0 pi = v^T A + t + v_0 pi
beta = u^T b - u_0 pi_0 = v^T b - v_0 (pi_0 + 1)
alpha in R^n
alpha_0 in R
u,v in R^m
u_0,v_0 > d
s,t in (x in R: x > d)^n


Note the original poltyop must be Ax=b, x>=0
"""
def makeLiftProjectLp(x, A, b, pi, pi0, d):
	variables = ["alpha0"] + ["alpha{}".format(i) for i in range(1, len(x)+1)]
	# left side of the disjunction
	leftSlackVariables = ["s{}".format(i) for i in range(1, len(x)+1)]
	rightSlackVariables = ["t{}".format(i) for i in range(1, len(x)+1)]
	leftCoefficientVariables = ["u0"] + ["u{}".format(i) for i in range(1, len(A) + 1)]
	rightCoefficientVariables = ["v0"] + ["v{}".format(i) for i in range(1, len(A) + 1)]

	prob = cplex.Cplex()
	try:
		prob.parameters.mip.limits.nodes.set(10000)
		prob.objective.set_sense(prob.objective.sense.minimize)
		prob.variables.add(names = variables + leftSlackVariables + rightSlackVariables + leftCoefficientVariables + rightCoefficientVariables,
			obj = 
# -1 a_0 + sum_j a_j * x_j
[-1] + [xi for xi in x] +
# no slack variables in objective
([0] * (len(leftSlackVariables) + len(rightSlackVariables) + len(leftCoefficientVariables) + len(rightCoefficientVariables))),
			lb = 
# cut variables are free
[-cplex.infinity] * len(variables) +
# slack variables are >= 0
[d] * (len(leftSlackVariables) + len(rightSlackVariables)) +
# coefficient variables are >= 0 
[d] + [d] * (len(leftCoefficientVariables) - 1) + [d] + [d] * (len(rightCoefficientVariables) - 1))

		# alpha equations
		for i in range(1, len(x)+1):
			prob.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["alpha{}".format(i), "s{}".format(i)] + leftCoefficientVariables,
				val = [-1, 1] + [-pi[i-1]] + [row[i-1] for row in A])],
				senses = "E",
				rhs = [0])
			prob.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["alpha{}".format(i), "t{}".format(i)] + rightCoefficientVariables,
				val = [-1, 1] + [+pi[i-1]] + [row[i-1] for row in A])],
				senses = "E",
				rhs = [0])

		# alpha_0 equations
		prob.linear_constraints.add(
			lin_expr = [cplex.SparsePair(ind = ["alpha0"] + leftCoefficientVariables, val = [-1] + [-pi0] + b), 
cplex.SparsePair(ind = ["alpha0"] + rightCoefficientVariables, val = [-1] + [pi0 + 1] + b)],
			senses = "EE",
			rhs = [0,0])

		# regularity condition to prevent unboundedness
		prob.linear_constraints.add(
			lin_expr = [cplex.SparsePair(ind = leftCoefficientVariables + rightCoefficientVariables + leftSlackVariables + rightSlackVariables, val = [1] * (len(leftCoefficientVariables) + len(rightCoefficientVariables) + len(leftSlackVariables) + len(rightSlackVariables)))],
			senses = "E",
			rhs = [1])


		return prob

	except CplexError as e:
		print(e, file=sys.stderr)
		raise e
		return

if __name__ == '__main__':
	import inequalities
	import triangularGridGraph
	import itertools
	vinf = 13
	V, E, Vstar, Estar = triangularGridGraph.triangularGridGraph(3,8)
	Ab = inequalities.makeExtendedLpConstraintMatrix(V, E, Vstar, Estar, vinf)
	# There are pairs of inequalities to represent equations, just take the first one
	A = [row[0] for row in Ab[::2]]
	b = [row[1] for row in Ab[::2]]
	variableNames = inequalities.enumerateExtendedLpVariables(V, E, Vstar, Estar, vinf)

	# The first E-delta(vinf) rows are edges, the first V* minus incident to vinf rows are faces, then the rest are vertices
	# This is for labelling vectors u such that u^T * A is something interesting
	def sparseCoefficientLabel(v):
		edgeLabels = ("e{}".format(i) for i,e in enumerate(E, 1) if vinf not in e)
		faceLabels = ("f{}".format(i) for i,f in enumerate(Vstar, 1) if vinf not in f)
		vertexLabels = ("v{}".format(i) for i,v in enumerate(V, 1))
		# Note that the nonnegativity inequalities are not included

		# Many rows have same label because they represent equations
		# So have to yield same label twice
		# No longer need this since we took out doubled equations
		def stutter(i):
			for x in i:
				yield x
				yield x


		return [(a,b) for a,b in zip(itertools.chain(edgeLabels, faceLabels, vertexLabels), v) if b != 0]

	def sparselyLabel(v):
		return [(a,b) for a,b in zip(variableNames, v) if b != 0]
	sparseX = dict([('x1', 1.0), ('x2', 1.0), ('x3', 1.0), ('x5', 1.0), ('x7', 1.0), ('x8', 1.0), ('x15', 1.0), ('x16', 1.0), ('x18', 1.0), ('x20', 1.0), ('x22', 1.0), ('x24', 1.0), ('x25', 0.5), ('x28', 1.0), ('x30', 1.0), ('x32', 0.5), ('x33', 0.5), ('x35', 0.5), ('x36', 0.5), ('x37', 1.0), ('x44', 1.0), ('x45', 1.0), ('x46', 0.5), ('x47', 1.0), ('x49', 1.0), ('x50', 1.0), ('x51', 1.0), ('z4,29', 1.0), ('z6,12', 1.0), ('z9,1', 1.0), ('z10,2', 1.0), ('z11,3', 1.0), ('z12,4', 1.0), ('z13,5', 1.0), ('z14,6', 1.0), ('z17,10', 1.0), ('z19,11', 1.0), ('z21,14', 1.0), ('z23,16', 1.0), ('z25,20', 0.5), ('z29,13', 1.0), ('z31,15', 1.0), ('z32,17', 0.5), ('z33,18', 0.5), ('z34,18', 0.5), ('z34,19', 0.5), ('z35,19', 0.5), ('z36,20', 0.5), ('z40,25', 1.0), ('z41,26', 1.0), ('z42,27', 1.0), ('z43,28', 1.0), ('z46,17', 0.5), ('z48,21', 1.0)])
	x = [sparseX[variable] if variable in sparseX else 0 for variable in variableNames]
	pi = [1 if variable in ("z32,16", "z33,18", "z46,29") else 0 for variable in variableNames]
	pi0 = 0
	d = 0

	try:
		liftProjectProb = makeLiftProjectLp(x, A, b, pi, pi0, d)

		logging.info("About to solve...")
		liftProjectProb.write("/tmp/bingo2.lp")
		liftProjectProb.solve()
		logging.info("Lift project LP value: {}".format(liftProjectProb.solution.get_objective_value()))
		alphaValues = ["alpha{}".format(i) for i in range(1, len(x)+1)]
		cpVector = liftProjectProb.solution.get_values(["alpha{}".format(i) for i in range(1, len(x)+1)])
		distance = liftProjectProb.solution.get_values("alpha0")

		# Recall that tolist gives us something in the format [[1] [2] [3] [4] ...]
		logging.info("Inequality: {} >= {}".format(sparselyLabel(cpVector), distance))
	

		def multiplyWithAtranspose(v):
			return scipy.sparse.csr_matrix(A).transpose().dot(numpy.matrix(v).transpose()).transpose()

		# The cutting plane for the left side
		leftCoefficients = liftProjectProb.solution.get_values(["u{}".format(i) for i in range(1, len(A)+1)])
		u0 = liftProjectProb.solution.get_values("u0")
		leftCp = multiplyWithAtranspose(leftCoefficients) + numpy.matrix(pi) * (-u0)
		logging.info("Left cutting plane: {}".format(sparselyLabel(leftCp.tolist()[0])))
		logging.info("Left distance: {}".format(numpy.matrix(b) * numpy.matrix(leftCoefficients).transpose() + pi0 * (-u0)))
		logging.info("Left decomposition: {}".format(sparseCoefficientLabel(leftCoefficients)))
		logging.info("...u0: {}".format(u0))
		logging.info("Left perturbation: {}".format(sparselyLabel(liftProjectProb.solution.get_values(["s{}".format(i) for i in range(1, len(x)+1)]))))

		# For the right side
		rightCoefficients = liftProjectProb.solution.get_values(["v{}".format(i) for i in range(1, len(A)+1)])
		v0 = liftProjectProb.solution.get_values("v0")
		rightCp = multiplyWithAtranspose(rightCoefficients) + numpy.matrix(pi) * (v0)
		logging.info("Right cutting plane: {}".format(sparselyLabel(rightCp.tolist()[0])))
		logging.info("Right distance: {}".format(numpy.matrix(b) * numpy.matrix(rightCoefficients).transpose() + (pi0 + 1) * (-v0)))
		logging.info("Right decomposition: {}".format(sparseCoefficientLabel(rightCoefficients)))
		logging.info("...v0: {}".format(v0))
		logging.info("Right perturbation: {}".format(sparselyLabel(liftProjectProb.solution.get_values(["t{}".format(i) for i in range(1, len(x)+1)]))))

	except CplexError as e:
		raise e
