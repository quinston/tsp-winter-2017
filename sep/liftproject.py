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
[d] + [d] * (len(leftCoefficientVariables) - 1) + [d] + [d] * (len(rightCoefficientVariables) - 1))

		# alpha equations
		for i in support:
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
	vinf = 13
	V, E, Vstar, Estar = triangularGridGraph.triangularGridGraph(10, 15)
	Ab = inequalities.makeExtendedLpConstraintMatrix(V, E, Vstar, Estar, vinf)
	A = [row[0] for row in Ab]
	b = [row[1] for row in Ab]
	variableNames = inequalities.enumerateExtendedLpVariables(V, E, Vstar, Estar, vinf)

	def sparselyLabel(v):
		return [(a,b) for a,b in zip(variableNames, v) if b != 0]
	sparseX = dict([('x1', 1.0), ('x2', 1.0), ('x3', 1.0), ('x6', 1.0), ('x7', 1.0), ('x9', 1.0), ('x11', 1.0), ('x13', 1.0), ('x14', 1.0), ('x15', 1.0), ('x22', 1.0), ('x23', 1.0), ('x24', 1.0), ('x26', 1.0), ('x30', 1.0), ('x32', 1.0), ('x34', 1.0), ('x36', 1.0), ('x38', 1.0), ('x39', 1.0), ('x43', 1.0), ('x45', 1.0), ('x46', 1.0), ('x49', 1.0), ('x51', 0.5), ('x52', 0.5), ('x54', 1.0), ('x57', 1.0), ('x58', 1.0), ('x60', 0.5), ('x61', 0.5), ('x64', 1.0), ('x72', 1.0), ('x73', 0.5), ('x76', 0.5), ('x85', 1.0), ('x88', 0.5), ('x91', 1.0), ('x93', 1.0), ('x95', 0.5), ('x98', 1.0), ('x100', 0.25), ('x101', 1.0), ('x104', 1.0), ('x106', 1.0), ('x108', 1.0), ('x110', 1.0), ('x112', 1.0), ('x113', 1.0), ('x118', 1.0), ('x120', 1.0), ('x121', 1.0), ('x122', 1.0), ('x123', 0.25), ('x124', 0.75), ('x126', 1.0), ('x127', 0.75), ('x128', 1.0), ('x129', 0.75), ('x131', 1.0), ('x134', 1.0), ('x137', 1.0), ('x138', 1.0), ('x141', 0.75), ('x145', 1.0), ('x147', 1.0), ('x151', 1.0), ('x158', 0.5), ('x159', 0.5), ('x169', 0.5), ('x171', 0.25), ('x172', 0.25), ('x175', 1.0), ('x177', 1.0), ('x178', 1.0), ('x180', 0.5), ('x182', 1.0), ('x183', 0.5), ('x184', 1.0), ('x186', 0.5), ('x187', 1.0), ('x188', 1.0), ('x190', 1.0), ('x194', 1.0), ('x199', 0.5), ('x200', 0.5), ('x202', 1.0), ('x204', 1.0), ('x206', 1.0), ('x208', 0.5), ('x209', 0.5), ('x212', 1.0), ('x213', 1.0), ('x215', 1.0), ('x217', 1.0), ('x219', 1.0), ('x221', 1.0), ('x222', 0.5), ('x225', 1.0), ('x231', 1.0), ('x236', 1.0), ('x240', 1.0), ('x244', 1.0), ('x246', 1.0), ('x252', 1.0), ('x254', 1.0), ('x255', 1.0), ('x258', 1.0), ('x260', 1.0), ('x262', 0.5), ('x264', 1.0), ('x267', 1.0), ('x268', 1.0), ('x270', 1.0), ('x273', 1.0), ('x274', 1.0), ('x277', 1.0), ('x279', 0.5), ('x281', 0.5), ('x282', 1.0), ('x285', 1.0), ('x288', 1.0), ('x294', 1.0), ('x300', 1.0), ('x301', 1.0), ('x303', 1.0), ('x305', 1.0), ('x311', 1.0), ('x313', 1.0), ('x314', 1.0), ('x316', 1.0), ('x323', 0.5), ('x324', 0.5), ('x326', 1.0), ('x328', 1.0), ('x330', 1.0), ('x331', 1.0), ('x332', 1.0), ('x334', 1.0), ('x336', 1.0), ('x343', 1.0), ('x346', 1.0), ('x347', 1.0), ('x355', 1.0), ('x356', 0.5), ('x359', 1.0), ('x362', 1.0), ('x365', 1.0), ('x368', 1.0), ('x370', 1.0), ('x372', 1.0), ('x374', 1.0), ('x377', 0.5), ('x378', 0.5), ('x382', 0.5), ('x383', 0.5), ('x384', 1.0), ('x385', 1.0), ('x386', 1.0), ('x387', 1.0), ('x388', 1.0), ('x389', 1.0), ('x391', 1.0), ('x392', 1.0), ('x394', 1.0), ('x396', 1.0), ('x397', 0.5), ('x398', 1.0), ('x399', 1.0), ('z4,8', 1.0), ('z5,10', 1.0), ('z8,16', 1.0), ('z10,20', 1.0), ('z16,1', 0.5), ('z16,2', 0.5), ('z17,2', 0.5), ('z17,3', 0.5), ('z18,3', 0.5), ('z18,4', 0.5), ('z19,4', 0.5), ('z19,5', 0.5), ('z20,5', 0.5), ('z20,6', 0.5), ('z21,6', 0.5), ('z21,7', 0.5), ('z25,11', 1.0), ('z27,12', 1.0), ('z28,13', 0.5), ('z28,14', 0.5), ('z29,14', 0.5), ('z29,15', 0.5), ('z31,17', 1.0), ('z33,18', 1.0), ('z35,21', 1.0), ('z37,22', 1.0), ('z41,27', 1.0), ('z42,28', 1.0), ('z44,30', 0.5), ('z44,1', 0.5), ('z47,36', 0.5), ('z47,7', 0.5), ('z48,9', 1.0), ('z50,42', 0.5), ('z50,13', 0.5), ('z51,15', 0.5), ('z52,46', 0.5), ('z53,19', 1.0), ('z55,23', 1.0), ('z56,54', 1.0), ('z59,29', 1.0), ('z60,30', 0.5), ('z61,31', 0.5), ('z62,32', 1.0), ('z63,34', 1.0), ('z65,35', 1.0), ('z66,36', 0.5), ('z66,37', 0.5), ('z67,37', 0.5), ('z67,38', 0.5), ('z68,38', 0.5), ('z68,39', 0.5), ('z69,39', 0.5), ('z69,40', 0.5), ('z70,40', 0.5), ('z70,41', 0.5), ('z71,41', 0.5), ('z71,42', 0.5), ('z73,43', 0.5), ('z74,44', 1.0), ('z75,45', 1.0), ('z76,46', 0.5), ('z77,47', 1.0), ('z78,48', 1.0), ('z79,49', 1.0), ('z80,50', 1.0), ('z81,51', 1.0), ('z82,52', 1.0), ('z83,53', 1.0), ('z84,55', 1.0), ('z86,56', 1.0), ('z87,58', 1.0), ('z88,31', 0.5), ('z89,33', 1.0), ('z90,64', 1.0), ('z92,68', 1.0), ('z94,72', 0.5), ('z94,43', 0.5), ('z95,74', 0.5), ('z96,76', 1.0), ('z97,78', 1.0), ('z99,82', 1.0), ('z100,84', 0.75), ('z102,57', 1.0), ('z103,59', 1.0), ('z105,60', 1.0), ('z107,62', 1.0), ('z109,65', 1.0), ('z111,66', 1.0), ('z114,69', 0.5), ('z114,70', 0.5), ('z115,70', 0.5), ('z115,71', 0.5), ('z116,71', 0.5), ('z116,72', 0.5), ('z117,73', 1.0), ('z119,74', 0.5), ('z119,75', 0.5), ('z123,79', 0.75), ('z124,80', 0.25), ('z125,80', 0.75), ('z125,81', 0.25), ('z127,83', 0.25), ('z129,84', 0.25), ('z130,86', 1.0), ('z132,61', 1.0), ('z133,63', 1.0), ('z135,67', 1.0), ('z136,98', 0.5), ('z136,69', 0.5), ('z139,104', 0.5), ('z139,75', 0.5), ('z140,77', 1.0), ('z141,79', 0.25), ('z142,110', 0.25), ('z142,81', 0.75), ('z143,112', 0.25), ('z143,83', 0.75), ('z144,85', 1.0), ('z146,87', 1.0), ('z148,88', 1.0), ('z149,89', 1.0), ('z150,90', 1.0), ('z152,92', 1.0), ('z153,93', 1.0), ('z154,94', 1.0), ('z155,95', 1.0), ('z156,96', 1.0), ('z157,97', 1.0), ('z158,98', 0.5), ('z159,99', 0.5), ('z160,100', 1.0), ('z161,101', 1.0), ('z162,102', 1.0), ('z163,103', 1.0), ('z164,104', 0.5), ('z164,105', 0.5), ('z165,105', 0.5), ('z165,106', 0.5), ('z166,106', 0.5), ('z166,107', 0.5), ('z167,107', 0.5), ('z167,108', 0.5), ('z168,108', 0.5), ('z168,109', 0.5), ('z169,109', 0.5), ('z170,110', 0.75), ('z170,111', 0.25), ('z171,111', 0.75), ('z172,112', 0.75), ('z173,114', 1.0), ('z174,116', 1.0), ('z176,91', 1.0), ('z179,126', 1.0), ('z180,99', 0.5), ('z181,130', 1.0), ('z183,134', 0.5), ('z185,138', 1.0), ('z186,140', 0.5), ('z189,115', 1.0), ('z191,117', 1.0), ('z192,118', 1.0), ('z193,119', 1.0), ('z195,120', 1.0), ('z196,121', 0.5), ('z196,122', 0.5), ('z197,122', 0.5), ('z197,123', 0.5), ('z198,123', 0.5), ('z198,124', 0.5), ('z199,124', 0.5), ('z200,125', 0.5), ('z201,127', 1.0), ('z203,128', 1.0), ('z205,131', 1.0), ('z207,132', 1.0), ('z208,134', 0.5), ('z209,135', 0.5), ('z210,135', 0.5), ('z210,136', 0.5), ('z211,136', 0.5), ('z211,137', 0.5), ('z214,139', 0.5), ('z214,140', 0.5), ('z216,113', 1.0), ('z218,146', 1.0), ('z220,150', 0.5), ('z220,121', 0.5), ('z222,125', 0.5), ('z223,156', 1.0), ('z224,129', 1.0), ('z226,133', 1.0), ('z227,164', 1.0), ('z228,166', 0.5), ('z228,137', 0.5), ('z229,168', 0.5), ('z229,139', 0.5), ('z230,141', 1.0), ('z232,142', 1.0), ('z233,143', 1.0), ('z234,144', 1.0), ('z235,145', 1.0), ('z237,147', 0.5), ('z237,148', 0.5), ('z238,148', 0.5), ('z238,149', 0.5), ('z239,149', 0.5), ('z239,150', 0.5), ('z241,151', 1.0), ('z242,152', 1.0), ('z243,154', 1.0), ('z245,155', 1.0), ('z247,157', 1.0), ('z248,158', 1.0), ('z249,159', 1.0), ('z250,160', 1.0), ('z251,162', 1.0), ('z253,163', 1.0), ('z256,166', 0.5), ('z256,167', 0.5), ('z257,167', 0.5), ('z257,168', 0.5), ('z259,170', 1.0), ('z261,174', 1.0), ('z262,147', 0.5), ('z263,178', 1.0), ('z265,153', 1.0), ('z266,184', 1.0), ('z269,161', 1.0), ('z271,165', 1.0), ('z272,196', 1.0), ('z275,171', 1.0), ('z276,172', 1.0), ('z278,173', 1.0), ('z279,175', 0.5), ('z280,175', 0.5), ('z280,176', 0.5), ('z281,176', 0.5), ('z283,179', 1.0), ('z284,180', 1.0), ('z286,182', 1.0), ('z287,183', 1.0), ('z289,185', 1.0), ('z290,186', 1.0), ('z291,187', 1.0), ('z292,188', 1.0), ('z293,189', 1.0), ('z295,190', 1.0), ('z296,191', 1.0), ('z297,192', 1.0), ('z298,193', 1.0), ('z299,194', 1.0), ('z302,169', 1.0), ('z304,202', 1.0), ('z306,177', 1.0), ('z307,208', 1.0), ('z308,181', 1.0), ('z309,212', 1.0), ('z310,214', 1.0), ('z312,218', 1.0), ('z315,195', 1.0), ('z317,197', 1.0), ('z318,198', 1.0), ('z319,199', 1.0), ('z320,200', 1.0), ('z321,201', 1.0), ('z322,203', 1.0), ('z323,204', 0.5), ('z324,204', 0.5), ('z325,206', 1.0), ('z327,207', 1.0), ('z329,210', 1.0), ('z333,213', 1.0), ('z335,216', 1.0), ('z337,217', 1.0), ('z338,219', 1.0), ('z339,220', 1.0), ('z340,221', 1.0), ('z341,222', 1.0), ('z342,223', 1.0), ('z344,224', 1.0), ('z345,226', 1.0), ('z348,232', 1.0), ('z349,205', 1.0), ('z350,236', 1.0), ('z351,209', 1.0), ('z352,211', 1.0), ('z353,242', 1.0), ('z354,215', 1.0), ('z356,248', 0.5), ('z357,250', 1.0), ('z358,252', 1.0), ('z360,225', 1.0), ('z361,227', 1.0), ('z363,228', 1.0), ('z364,230', 1.0), ('z366,231', 1.0), ('z367,233', 1.0), ('z369,234', 1.0), ('z371,237', 1.0), ('z373,238', 1.0), ('z375,240', 1.0), ('z376,241', 1.0), ('z377,243', 0.5), ('z378,244', 0.5), ('z379,244', 0.5), ('z379,245', 0.5), ('z380,245', 0.5), ('z380,246', 0.5), ('z381,246', 0.5), ('z381,247', 0.5), ('z382,247', 0.5), ('z383,248', 0.5), ('z390,229', 1.0), ('z393,235', 1.0), ('z395,239', 1.0), ('z397,243', 0.5), ('z400,249', 1.0), ('z401,251', 1.0)])
	x = [sparseX[variable] if variable in sparseX else 0 for variable in variableNames]
	support = [(i+1) for i in range(len(x)) if x[i] > 0]
	# out degree of face 31 should be 0 or geq 1
	pi = [1 if variable in ("z60,30", "z61,32", "z88,60") else 0 for variable in variableNames]
	pi0 = 0
	d = 0

	try:
		liftProjectProb = makeLiftProjectLp(x, A, b, pi, pi0, d)

		logging.info("About to solve...")
		liftProjectProb.write("/tmp/bingo2.lp")
		liftProjectProb.solve()
		logging.info("Lift project LP value: {}".format(liftProjectProb.solution.get_objective_value()))
		alphaValues = ["alpha{}".format(i) for i in support]
		cpVector = scipy.sparse.csr_matrix(A).transpose().dot(numpy.matrix(liftProjectProb.solution.get_values(["u{}".format(i) for i in range(1, len(A)+1)])).transpose()).transpose()
		distance = liftProjectProb.solution.get_values("alpha0")

		# Recall that tolist gives us something in the format [[1] [2] [3] [4] ...]
		logging.info("Inequality: {} >= {}".format(sparselyLabel(cpVector.tolist()[0]), distance))
	
	except CplexError as e:
		pass
