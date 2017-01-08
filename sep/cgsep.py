import sys

import cplex
from cplex.exceptions import CplexError


"""
Let x* be a point we are trying to separate.
Let J(x*) = {j: x*_j > 0} be the positive support of x*

The MIP is

Note A is the m-by-n constraint matrix, but a_i are real variables, not columns/rows of A


max (sum_{j\in J(x*)} a_j x*_j) - a_0
f_j = u^T A_j - a_j, j \in J(x*)
f_0 = u^Tb - a_0
0 <= f_j <= 1 - d, j = 0 or j \in J(x*)
0 <= u_i <= 1 - d, i = 1, 2, ..., m
a_j integer, j = 0 or j \in J(x*)
"""

def makeCgLp(x, A, b, d):
	support = [(i+1) for i in range(len(x)) if x[i] > 0]

	variables = ["a0"] + ["a{}".format(i) for i in support] 
	slackVariables = ["f0"] + ["f{}".format(i) for i in support]
	coefficientVariables = ["u{}".format(i) for i in range(1, len(A) + 1)]

	prob = cplex.Cplex()
	try:
		prob.objective.set_sense(prob.objective.sense.maximize)
		prob.variables.add(names = variables + slackVariables + coefficientVariables, 
			obj = 
# -1 * a0, aj *  x^*_j, ... 
[-1] + [x[i-1] for i in support] + 
# slack and coefficient variables don't appear in objective
([0] * (len(slackVariables) + len(coefficientVariables))),
			types = 
# cut variables are integer
[prob.variables.type.integer] * len(variables) + 
# slack and coefficient variables are free
[prob.variables.type.continuous] * (len(slackVariables) + len(coefficientVariables)),
			lb =
# cut variables are free
[-cplex.infinity] * len(variables) +
# coefficient variables and slack variables are >=0
[0] * (len(slackVariables) + len(coefficientVariables)),
			ub = 
# cut variables are free
[cplex.infinity] * len(variables) +
# slack and coefficient varaibels are <= 1-d
[1-d] * (len(slackVariables) + len(coefficientVariables)),
)

		# Set up slack variables
		prob.linear_constraints.add(
			lin_expr = [
# f0 = u^Tb - a0 iff -f0 -a0 + u^Tb = 0
cplex.SparsePair(ind = ["f0", "a0"] + coefficientVariables, val = [-1, -1] + b),
] +
[cplex.SparsePair(ind = ["f{}".format(i), "a{}".format(i)] + coefficientVariables, val = [-1, -1] + [row[i-1] for row in A]) for i in support],
			senses = ["E"] * len(slackVariables),
			rhs = [0] * len(slackVariables)
)

		return prob

	except CplexError as e:
		print(e, file=sys.stderr)
		return

"""
Take a point to separate x and a matrix-vector pair (A,b)

A is most likely a list of rows

This is kind of unfortuante since we have to read A by columns
"""
def solve(x, A, b, d):

	try:
		prob = makeCgLp(x, A, b, d)
		prob.solve()

		print("Problem status: ", prob.solution.status[prob.solution.get_status()])
		print("Primal values: ", list(zip(prob.variables.get_names(), prob.solution.get_values())))
		print("Objective value: ", prob.solution.get_objective_value())

	except CplexError as e:
		print(e, file=sys.stderr)
		return

