import cplex
import argparse
import logging
from igraph import Graph
import itertools
import deap
from deap import creator,base,tools,algorithms
import random
import math

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

parser = argparse.ArgumentParser()
parser.add_argument('--no-stable-sets', type=int, help='desired number of stable sets')
parser.add_argument('dom_filename', help='dominos')
parser.add_argument('x_filename', help='LP solution')
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

"""
1. Contract each domino side (Ai, Bi) to a node
2. Randomly contract edges except edges that have Ai on
one side and Bi on the other side. While running the algorithm,
you need to keep track of whether any randomly chosen edge 
has two sides of one domino on either side of the edge
3. Continue until just one edge

Karger-Stein: Contract to size n/sqrt(2), then continue twice from this stage,
then take the best one
"""
def findHandleByModifiedKargers(dominoes, graph, teethIndices):
	shrunkenDominoesGraph = graph.copy()
	# Give each node a "contents" attribute: a contraction of multiple nodes will have a "contents" attribute of length greater than one
	for u in shrunkenDominoesGraph.vs:
		u["contents"] = set([u.index])

	def shrink(graph, vertexIndices):
		# len(set is necessary in case vertexIndices includes duplicates
		newNoVertices = len(graph.vs) - len(set(vertexIndices)) + 1
		vertexIndices = set(vertexIndices)
		mapping = []

		currentVertex = 0
		for i in range(len(graph.vs)):
			if i in vertexIndices:
				mapping.append(newNoVertices - 1)
			else:
				mapping.append(currentVertex)
				currentVertex += 1

		def combineSupervertices(attrs):
			contents = attrs[0]
			for S in attrs[1:]:
				contents |= S
			return contents

		def onlyKeepNameIfSingleton(attrs):
			if len(attrs) > 1:
				return None
			elif len(attrs) == 1:
				return attrs[0]

		graph.contract_vertices(mapping, combine_attrs={"contents": combineSupervertices, "name": onlyKeepNameIfSingleton})
		return graph.vs[newNoVertices - 1]

	# Contract each domino side to a point
	# In order to avoid updating the indices each time we contract a set, 
	# we will have to contract all the domino sides at once
	toothIndexToSize = dict((i, len(dominoes.dominoToA[i]) + len(dominoes.dominoToB[i])) for i in teethIndices)
	noNonToothVertices = len(shrunkenDominoesGraph.vs) - sum(toothIndexToSize.values())
	sideAtoNewVertexId = dict(zip(teethIndices, range(noNonToothVertices, noNonToothVertices + len(teethIndices))))
	sideBtoNewVertexId = dict(zip(teethIndices, range(noNonToothVertices + len(teethIndices), noNonToothVertices + 2*len(teethIndices))))
	
	mapping = []
	currentVertex = 0
	for i in range(len(shrunkenDominoesGraph.vs)):
		toothToWhichVertexBelongs = set(dominoes.verticesToContainingDominoes[i]).intersection(teethIndices)
		if len(toothToWhichVertexBelongs) == 0:
			mapping.append(currentVertex)
			currentVertex += 1
		else:
			t = toothToWhichVertexBelongs.pop()
			if i in dominoes.dominoToA[t]:
				mapping.append(sideAtoNewVertexId[t])
			else:
				mapping.append(sideBtoNewVertexId[t])

	# For vertices that are not being merged: keep their contents attribute
	# For vertices being merged, discard it since we are going to replace it with
	# the domino side label
	def f(x):
		if len(x) > 1:
			return None
		else:
			return x[0]
		
	shrunkenDominoesGraph.contract_vertices(mapping, combine_attrs={"contents": f})

	# Replace the combined contents with a single label describing the domino side
	# Also give them names to easily access them after contracting
	for i in teethIndices:
		a = shrunkenDominoesGraph.vs[sideAtoNewVertexId[i]]
		a["contents"] = set(["a{}".format(i)])
		a["name"] = "a{}".format(i)
		b = shrunkenDominoesGraph.vs[sideBtoNewVertexId[i]]
		b["contents"] = set(["b{}".format(i)])
		b["name"] = "b{}".format(i)


	"""
	Detects if s and t contain two sides of a domino, in which case they must not be merged
	"""
	def isSemicutEdge(graph, s, t):
		S1 = graph.vs[s]["contents"]
		S2 = graph.vs[t]["contents"]
		for i in teethIndices:
			if ("a{}".format(i) in S1 and "b{}".format(i) in S2) or ("a{}".format(i) in S2 and "b{}".format(i) in S1):
				return True
		return False

	"""
	Returns a set of X
	where X is either:
	- aXX or bXX
	- a numeric index for the vertices in the ORIGINAL graph PRIOR TO DOMINO SHRINKING

	It derives the numeric index from whatever is in the "contents" attribute of the vertex of 
the input graph. So you must make this beforehand.
	"""
	def modifiedKargers(graph):
		graph = graph.copy()
		# Manually eep copy all attributes
		for u in graph.vs:
			u["contents"] = set(u["contents"])


		# First create a domino assignment
		# Pick one of the domino sides, and keep contracting it
		# with one of its domino side 
		# neighbours that is not in the same domino
		# Contract the opposite side of the root with the opposite
		# side of the chosen neighbour domino
		# Do this (p-1) times where p is the number of dominoes

		root = graph.vs.select(name="a{}".format(teethIndices[0]))[0]

		otherDominoSides = set(["a{}".format(i) for i in teethIndices[1:]] + ["b{}".format(i) for i in teethIndices[1:]])
		def other(t, x1):
			if t[0] == x1:
				return t[1]
			else:
				return t[0]

		for i in range(len(teethIndices) - 1):
			logging.debug("Remainign domino sides: {}".format(otherDominoSides))
			logging.debug("Contents: {}".format(graph.vs["contents"]))
			otherDominoSidesVertexIndices = set(graph.vs.select(name=x)[0].index for x in otherDominoSides)
			nonzeroEdgesToDominoSides = [e for e in graph.es if root.index in e.tuple and other(e.tuple, root.index) in otherDominoSidesVertexIndices]

			if len(nonzeroEdgesToDominoSides) > 0:
				neighbouringDominoSideToContract = weighted_choice([other(e.tuple, root.index) for e in nonzeroEdgesToDominoSides], [e["weight"] for e in nonzeroEdgesToDominoSides])
			else:
				# Choose uniormly at random amongst 0-weight edges
				neighbouringDominoSideToContract = random.choice(tuple(otherDominoSidesVertexIndices))

			logging.debug("Taking domino side {}".format(graph.vs[neighbouringDominoSideToContract]["name"]))
			incomingToothIndex = graph.vs[neighbouringDominoSideToContract]["name"][1:]

			# Update the root for next shrinking
			root = shrink(graph, (root.index, neighbouringDominoSideToContract))
			# Remove this domino from future selection
			otherDominoSides = set(x for x in otherDominoSides if incomingToothIndex != x[1:])


		while len(graph.vs) > 2:
			currentSize = len(graph.vs)
			logging.debug("Current supernodes {}".format(graph.vs["contents"]))

			nonzeroNonSemicutEdges = [e for e in graph.es if not isSemicutEdge(graph, e.source, e.target) and e.source != e.target]

			if len(nonzeroNonSemicutEdges) > 0:
				edgeToContract = weighted_choice(nonzeroNonSemicutEdges, [e["weight"] for e in nonzeroNonSemicutEdges])

				logging.debug("Shrinking two things on a weight-{} edge {}".format(graph[edgeToContract.tuple], [graph.vs[i]["contents"] for i in edgeToContract.tuple]))

				shrink(graph, edgeToContract.tuple)

			else:
				nonSemicutEdges = [(u,v) for u,v in itertools.combinations(graph.vs, 2) if not isSemicutEdge(graph, u.index, v.index) and u!=v]
				edgeToContract = random.choice(nonSemicutEdges)
				logging.debug("Shrinking two things on a void edge {}".format([u["contents"] for u in edgeToContract]))
				shrink(graph, [u.index for u in edgeToContract])


			logging.debug("Graph went from {} to {} nodes".format(currentSize, len(graph.vs)))
			assert(len(graph.vs) < currentSize)
			


		if len(graph.vs[graph.es[0].source]["contents"]) <= len(graph.vs[graph.es[0].target]["contents"]):
			return graph.vs[graph.es[0].source]["contents"]
		else:
			return graph.vs[graph.es[0].target]["contents"]

	NO_VERTICES = len(graph.vs)
	NO_ITERATIONS = int(NO_VERTICES*(NO_VERTICES-1)/2*math.log(NO_VERTICES))
	bestCut = None
	bestCutValue = None
	for i in range(NO_ITERATIONS):
		if i % 1000 == 0:
			logging.info("Karger #{}".format(i))
		logging.debug("Contents before doing Kargers: {}".format(shrunkenDominoesGraph.vs["contents"]))
		logging.debug("Names before doing Kargers: {}".format(shrunkenDominoesGraph.vs["name"]))
		cut = modifiedKargers(shrunkenDominoesGraph)
		logging.debug("Got cut {}".format(cut))

		# Replace string identifiers with domino side contents
		expandedCut = set()
		for u in cut:
			if type(u) == int:
				expandedCut.add(u)
			elif type(u) == str:
				toothIndex = int(u[1:])
				if u[0] == 'a':
					expandedCut.update(dominoes.dominoToA[toothIndex])
				else:
					expandedCut.update(dominoes.dominoToB[toothIndex])

		# Note: we're counting edges and vertices over the original graph now, not shrunkenDominoesGraph
		cutValue = sum(e["weight"] for e in graph.es if len(expandedCut.intersection((e.source, e.target))) == 1)

		if bestCutValue == None or cutValue < bestCutValue:
			bestCut = expandedCut 
			bestCutValue = cutValue
			logging.info("New best cut: {}".format(bestCut))
			logging.info("New best cut value: {}".format(bestCutValue))

	return (bestCutValue, bestCut)

if __name__ == '__main__':
	d = getDominoes()
	g = getSupportGraph()
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
	
			logging.info("Add objective value <= 1 constraint to aid enumeration")
			cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=allDominoVariableNames, val=d.dominoToWeight)], rhs=[1], senses='L')
	
			cpx.parameters.mip.limits.populate.set(args.no_stable_sets)
			cpx.parameters.mip.limits.nodes.set(10000 * args.no_stable_sets)
	
			logging.info("Populating!")
			cpx.populate_solution_pool()
	
			logging.info("Obtained {} solutions".format(cpx.solution.pool.get_num()))
			for i in range(cpx.solution.pool.get_num()):
				#[:-1] to exclude the value of k
				teethIndices = [j for j,x in enumerate(cpx.solution.pool.get_values(i)[:-1]) if x == 1]
				noTeeth = 2*cpx.solution.pool.get_values(i, "k") + 3
	
				# Sanity check
				if len(teethIndices) % 2 == 1:
					logging.info("Teeth {}: {}".format(i, teethIndices))
					logging.info("Objective value {}: {}".format(i, cpx.solution.pool.get_objective_value(i)))
	
					# For a set of vertices S, compute the sum of all edges uv for u,v in S 
					def gamma(S):
						return sum(g[u,v] for u,v in itertools.combinations(S, 2))
	
					teeth = [d.dominoToA[i] + d.dominoToB[i] for i in teethIndices]
					teethDeltas = sum(2 * (len(tooth) - gamma(tooth)) for tooth in teeth)
					logging.info("Sum of teeth cuts {}: {}".format(i, teethDeltas))
	
					handleCutValue, handle = findHandleByModifiedKargers(d, g, teethIndices)
					logging.info("Handle {}: {}".format(i, handle))
					logging.info("Handle cut {}: {}".format(i, handleCutValue))
					logging.info("Comb violation {} (positive is good): {}".format(i, (3*noTeeth+1) - (teethDeltas + handleCutValue)))
				else:
					logging.warning("Ignored even size comb {}".format(i))
	
	
			
	except cplex.exceptions.CplexError as e:
		print(e)
		raise e
