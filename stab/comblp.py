import cplex
import argparse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

parser = argparse.ArgumentParser()
parser.add_argument('--no-stable-sets', type=int, help='desired number of stable sets')
parser.add_argument('filename')
args = parser.parse_args()

class Dominoes:
	pass

def getDominoes():
	d = Dominoes()
	d.verticesToContainingDominoes = dict()
	d.dominoToWeight = []
	d.dominoToA = []
	d.dominoToB = []

	with open(args.filename) as f:
		line = f.readline().split()
		V = int(line[0])
		noDominoes = int(line[1])

		for v in range(V):
			d.verticesToContainingDominoes[v] = list()

		numDomino = 0
		for line in f:
			lineSplit = line.split()
			d.dominoToWeight.append(float(lineSplit[0]))

# For each vertex w in the domino T, record T in w's  list 
			#:-1 is to avoid trailing space
			for w in lineSplit[3:-1]:
				d.verticesToContainingDominoes[int(w)].append(numDomino)

			sizeA = int(lineSplit[1])
			d.dominoToA.append(lineSplit[3:sizeA+3])
			d.dominoToB.append(lineSplit[sizeA+3:])
			#logging.info("Domino: {} / {}".format(d.dominoToA[-1], d.dominoToB[-1]))


			numDomino += 1

	return d

d = getDominoes()

try:
	with cplex.Cplex() as cpx:
		noDominoes = len(d.dominoToWeight)
		allDominoVariableNames = ["x{}".format(i) for i in range(noDominoes)]

		logging.info("Adding {} binary variables".format(noDominoes))
		cpx.variables.add(names = allDominoVariableNames, types=cpx.variables.type.binary * noDominoes)

		logging.info("Setting objective")
		cpx.objective.set_sense(cpx.objective.sense.minimize)
		for domino,weight in enumerate(d.dominoToWeight):
			cpx.objective.set_linear("x{}".format(domino), weight)

		logging.info("Adding clique constraints")
		counter = 0
		# The set of dominoes sharing any particular vertex form a clique
		for v,dominoes in d.verticesToContainingDominoes.items():
			# If only one tooth contains a given vertex, the constraint is redundant since the tooth variable is 0-1
			if len(dominoes) > 1:
				# Assume the first however many variables are  domino variables: use indices directly rather than names
				cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=dominoes, val=[1]*len(dominoes))], rhs=[1], senses='L')
			counter += 1
			if counter % 100 == 0:
				logging.info("Added {} constraints".format(counter))
		
		logging.info("Adding parity variable 'k'")
		cpx.variables.add(names = ["k"], types=cpx.variables.type.integer, lb=[0])

		logging.info("Adding parity constraint sum(x) = 2k+3")
		cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=allDominoVariableNames + ["k"], val=([1]*noDominoes) + [-2])], rhs=[3], senses='E')

		cpx.parameters.mip.limits.populate.set(args.no_stable_sets)
		cpx.parameters.mip.limits.nodes.set(10000 * args.no_stable_sets)

		cpx.write('oddstab.lp')

		logging.info("Populating!")
		cpx.populate_solution_pool()

		logging.info("Printing {} solutions:".format(cpx.solution.pool.get_num()))
		for i in range(cpx.solution.pool.get_num()):
			#[:-1] to exclude the value of k
			logging.info("Solution {}: {}".format(i, [j for j,x in enumerate(cpx.solution.pool.get_values(i)[:-1]) if x == 1]))
			logging.info("Objective value {}: {}".format(i, cpx.solution.pool.get_objective_value(i)))

		
except cplex.exceptions.CplexError as e:
	print(e)
	raise e
