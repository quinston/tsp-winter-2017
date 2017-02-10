import cplex
import sys
from cplex.exceptions import CplexError

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

"""
def makeLiftProjectLp(x, A, b, pi, pi0, d):
	support = [(i+1) for i in range(len(x)) if x[i] > 0]
	variables = ["alpha0"] + ["alpha{}".format(i) for i in support]
	# left side of the disjunction
	leftSlackVariables = ["s{}".format(i) for i in support]
	rightSlackVariables = ["t{}".format(i) for i in support]
	leftCoefficientVariables = ["u0"] + ["u{}".format(i) for i in range(1, len(A) + 1)]
	rightCoefficientVariables = ["v0"] + ["v{}".format(i) for i in range(1, len(A) + 1)]

	prob = cplex.Cplex()
	try:
		prob.parameters.mip.limits.nodes.set(10000)
		prob.objective.set_sense(prob.objective.sense.minimize)
		prob.variables.add(names = variables + leftSlackVariables + rightSlackVariables + leftCoefficientVariables + rightCoefficientVariables,
			obj = 
# -1 a_0 + sum_j a_j * x_j
[-1] + [x[i-1] for i in support] +
# no slack variables in objective
([0] * (len(leftSlackVariables) + len(rightSlackVariables) + len(leftCoefficientVariables) + len(rightCoefficientVariables))),
			lb = 
# cut variables are free
[-cplex.infinity] * len(variables) +
# slack variables are > 0
[d] * (len(leftSlackVariables) + len(rightSlackVariables)) +
# coefficient variables are free except for u_0, v_0
[d] + [-cplex.infinity] * (len(leftCoefficientVariables) - 1) + [d] + [-cplex.infinity] * (len(rightCoefficientVariables) - 1))

		# alpha equations
		prob.linear_constraints.add(
			lin_expr = [cplex.SparsePair(ind = ["alpha{}".format(i), "s{}".format(i)] + leftCoefficientVariables,
val = [-1, 1] + [-pi[i-1]] + [row[i-1] for row in A]) for i in support] +
[cplex.SparsePair(ind = ["alpha{}".format(i), "t{}".format(i)] + rightCoefficientVariables,
val = [-1, 1] + [+pi[i-1]] + [row[i-1] for row in A]) for i in support],
senses = ["E"] * len(support) * 2,
rhs = [0] * len(support) * 2)

		# alpha_0 equations
		prob.linear_constraints.add(
			lin_expr = [cplex.SparsePair(ind = ["alpha0"] + leftCoefficientVariables, val = [-1] + [-pi0] + b), 
cplex.SparsePair(ind = ["alpha0"] + rightCoefficientVariables, val = [-1] + [pi0 + 1] + b)],
			senses = "EE",
			rhs = [0,0])


		return prob

	except CplexError as e:
		print(e, file=sys.stderr)
		raise e
		return

makeLiftProjectLp([1,2,3], [[1,2,3],[4,3,2],[1,32,1],[3,2,1]], [0,1,2,3], [10,20,30,40], -4, 0.01)
