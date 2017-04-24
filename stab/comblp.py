import cplex
import argparse
import logging
from igraph import Graph
import itertools
import deap
from deap import creator,base,tools,algorithms
import random
import math
import concurrent.futures
import threading
import pprint

# Randomly select one item from s according to weights
def weighted_choice(s, weights):
	if len(s) != len(weights):
		raise ValueError("Size mismatch between sequence and weights")
	if len(s) == 0:
		raise IndexError("Choosing from empty sequence")
	
	total = sum(weights)
	r = random.uniform(0, total)
	choice = s[0]
	x = 0
	for i in range(len(weights)):
		if x+weights[i] > r:
			return choice
		else:
			choice = s[i+1]
			x += weights[i]

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

pp = pprint.PrettyPrinter(indent = 2)

parser = argparse.ArgumentParser()
parser.add_argument('--no-stable-sets', type=int, help='desired number of stable sets')
parser.add_argument('--no-karger-iterations', type=int, help='number of attempts at finding a handle')
parser.add_argument('dom_filename', help='dominos')
parser.add_argument('x_filename', help='LP solution')
parser.add_argument('handle', help='handle vertices', nargs='+')
args = parser.parse_args()
print(args)

class Dominoes:
	pass


def getDominoes():
	d = Dominoes()
	d.verticesToContainingDominoes = dict()
	d.dominoToWeight = []
	d.dominoToA = []
	d.dominoToB = []

	with open(args.dom_filename) as f:
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
			for w in lineSplit[3:]:
				d.verticesToContainingDominoes[int(w)].append(numDomino)

			sizeA = int(lineSplit[1])
			d.dominoToA.append([int(x) for x in lineSplit[3:sizeA+3]])
			d.dominoToB.append([int(x) for x in lineSplit[sizeA+3:]])
			#logging.info("Domino: {} / {}".format(d.dominoToA[-1], d.dominoToB[-1]))


			numDomino += 1

	return d

# handle: list of vertex indices
def getDominoesWithRespectToHandle(handle):
	handle = frozenset(handle)

	d = Dominoes()
	d.verticesToContainingDominoes = dict()
	d.dominoToWeight = []
	d.dominoToA = []
	d.dominoToB = []
	d.dominoLineNumbers = []
	
	with open(args.dom_filename) as f:
		line = f.readline().split()
		V = int(line[0])
		noDominoes = int(line[1])

		for v in range(V):
			d.verticesToContainingDominoes[v] = list()

		numDomino = 0
		numLine = 1
		for line in f:
			numLine += 1

			lineSplit = line.split()
			sizeA = int(lineSplit[1])
			sideA = frozenset(int(x) for x in lineSplit[3:sizeA+3])
			sideB = frozenset(int(x) for x in lineSplit[sizeA+3:])
			handleRespectsDomino = ((sideA <= handle) and sideB.isdisjoint(handle)) or ((sideB <= handle) and sideA.isdisjoint(handle)) 

			if handleRespectsDomino:
				d.dominoToWeight.append(float(lineSplit[0]))
				d.dominoLineNumbers.append(numLine)

				# For each vertex w in the domino T, record T in w's  list 
				for w in lineSplit[3:]:
					d.verticesToContainingDominoes[int(w)].append(numDomino)

				d.dominoToA.append(list(sideA))
				d.dominoToB.append(list(sideB))
				#logging.info("Domino: {} / {}".format(d.dominoToA[-1], d.dominoToB[-1]))

				numDomino += 1

	return d


def getSupportGraph():
	with open(args.x_filename) as f:
		line = f.readline().split()
		V = int(line[0])
		E = int(line[1])

		g = Graph()
		g.add_vertices(V)

		for line in f:
			lineSplit = line.split()
			u,v = [int(x) for x in lineSplit[:2]]
			weight = float(lineSplit[2])
			g.add_edge(u, v)
			g.es[g.get_eid(u,v)]["weight"] = weight

		return g


"""
Given indices to teeth, finds min cut containing union of the smallest sides
of each domino

shouldPickSideA: Int -> Bool, i |-> whether or not ot pick side A of domino i to be on side "s"
of the cut. What being on side "s" means is
not important as long as shouldPickSideA is consistent in some sense
"""
def findHandle(dominoes, graph, teethIndices, shouldPickSideA):
	INFINITY = len(graph.es)

	graph.add_vertex(name="s")
	graph.add_vertex(name="t")

	for i in teethIndices:
		if shouldPickSideA(i):
			sSide = dominoes.dominoToA[i] 
			tSide = dominoes.dominoToB[i]
		else:
			sSide = dominoes.dominoToB[i] 
			tSide = dominoes.dominoToA[i]
		for v in sSide:
			graph.add_edge(v, "s")
			graph.es[g.get_eid(v, "s")]["weight"] = INFINITY
		for v in tSide:
			graph.add_edge(v, "t")
			graph.es[g.get_eid(v, "t")]["weight"] = INFINITY

	# A Cut object
	cut = graph.st_mincut("s", "t", capacity="weight")
	smallerSide = cut.partition[0] if len(cut.partition[0]) <= len(cut.partition[1]) else cut.partition[1]
	# Get rid of s or t
	smallerSide = smallerSide[:-1]
	handleCutValue = cut.value

	graph.delete_vertices(["s", "t"])

	return (handleCutValue, smallerSide)

def geneticallyFindBestHandle(dominoes, graph, teethIndices):
	"""
	Find the best assignment of domino sides, where an assignment
is just a 0-1 vector of length p where there are p teeth
	"""
	# Reminder: we want to maximize the violation, so we need to minimize the handle's cut capacity
	deap.creator.create("HandleCapacityMin", deap.base.Fitness, weights=(-1,))
	deap.creator.create("Individual", list, fitness=deap.creator.HandleCapacityMin)

	toolbox = deap.base.Toolbox()
	toolbox.register("random_bit", random.randint, 0, 1)
	toolbox.register("individual", deap.tools.initRepeat, deap.creator.Individual, toolbox.random_bit, len(teethIndices))
	toolbox.register("population", deap.tools.initRepeat, list, toolbox.individual)

	toolbox.register("mate", deap.tools.cxTwoPoint)
	toolbox.register("mutate", deap.tools.mutFlipBit, indpb=0.5)
	toolbox.register("select", deap.tools.selTournament, tournsize=8)

	def assignmentToHandle(bits):
		return findHandle(dominoes, graph, teethIndices, lambda i: dict(zip(teethIndices, bits))[i]==True)

	def evaluate(x):
		value, side = assignmentToHandle(x)
		return (value,)

	toolbox.register("evaluate", evaluate)

	pop = toolbox.population(n=20)
	hof = deap.tools.HallOfFame(1)
	deap.algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=500, halloffame=hof, verbose=False)

	return assignmentToHandle(hof[0])


if __name__ == '__main__':
	g = getSupportGraph()
	# For a set of vertices S, compute the sum of all edges uv for u,v in S 
	def gamma(S):
		return sum(g[u,v] for u,v in itertools.combinations(S, 2))

	def delta(S):
		return 2*(len(S) - gamma(S))

	handle = [int(x) for x in args.handle]
	handleCutValue = delta(handle) 

	d = getDominoesWithRespectToHandle(handle)
	logging.info("List of dominoes -> line numbers: {}".format(pp.pformat(list(enumerate(d.dominoLineNumbers)))))

	try:
		with cplex.Cplex() as cpx:
			noDominoes = len(d.dominoToWeight)
			allDominoVariableNames = ["x{}".format(i) for i in range(noDominoes)]
	
			logging.info("Adding {} binary variables".format(noDominoes))
			cpx.variables.add(names = allDominoVariableNames, types=cpx.variables.type.binary * noDominoes)
	
	
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
			
			logging.info("Adding parity variable 'm'")
			cpx.variables.add(names = ["m"], types=cpx.variables.type.integer, lb=[0])
	
			logging.info("Adding parity constraint sum(x) = 2m+3")
			cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=allDominoVariableNames + ["m"], val=([1]*noDominoes) + [-2])], rhs=[3], senses='E')

			logging.info("Add objective value <= x(delta(H)) - 1 constraint to aid enumeration")
			epsilon = 1e-6
			cpx.variables.add(names = ["v"], lb=[-cplex.infinity])
			# Set objective value to equal variable v
			cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=allDominoVariableNames + ["v"], val=[3-delta(d.dominoToA[domino] + d.dominoToB[domino]) for domino in range(len(d.dominoToA))] + [-1])], rhs=[0], senses='E')
			# Now set v = 3k - delta(T) > delta(H) - 1, where k=2m+3
			cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=["v"], val=[1])], rhs=[delta(handle) - 1+epsilon], senses='G')
	
			logging.info("Setting objective: 3k - x(delta(T))")
			# 3(sum x_i) + 1 - (sum delta(T_i)x_i)
			cpx.objective.set_sense(cpx.objective.sense.maximize)
			cpx.objective.set_linear("v", 1)

			cpx.parameters.mip.limits.populate.set(args.no_stable_sets)
	
			logging.info("Populating!")
			cpx.populate_solution_pool()
	
			logging.info("Obtained {} solutions".format(cpx.solution.pool.get_num()))
			for i in range(cpx.solution.pool.get_num()):
				#[:-2] to exclude the value of m and v
				teethIndices = [j for j,x in enumerate(cpx.solution.pool.get_values(i)[:-2]) if x == 1]
				noTeeth = 2*cpx.solution.pool.get_values(i, "m") + 3

				#logging.info("Variables {}: {}".format(i, pprint.pformat(list(zip(cpx.variables.get_names(), cpx.solution.pool.get_values(i))))))
	
				# Sanity check
				if len(teethIndices) % 2 == 1:
					logging.info("Teeth {}: {}".format(i, teethIndices))
					logging.info("Objective value {}: {}".format(i, cpx.solution.pool.get_objective_value(i)))
	
	
					teeth = [d.dominoToA[i] + d.dominoToB[i] for i in teethIndices]
					teethDeltas = sum(2 * (len(tooth) - gamma(tooth)) for tooth in teeth)
					logging.info("Sum of teeth cuts {}: {}".format(i, teethDeltas))
	

					logging.info("Handle {}: {}".format(i, handle))
					logging.info("Handle cut {}: {}".format(i, delta(handle)))
					logging.info("Comb violation {} (positive is good): {}".format(i, cpx.solution.pool.get_objective_value(i) - delta(handle) + 1))
				else:
					logging.warning("Ignored even size-{} comb {}".format(len(teethIndices), i))
					logging.warning("m for faulty comb {}: {}".format(i, cpx.solution.pool.get_values(i, "m"))) 
					logging.warning("Teeth for faulty comb {}: {}".format(i, teethIndices))
	
			
	except cplex.exceptions.CplexError as e:
		print(e)
		raise e
