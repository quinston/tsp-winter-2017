import cplex
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('noTeeth', type=int, help='number of teeth per stable set')
parser.add_argument('noStableSets', type=int, help='desired number of stable sets')
parser.add_argument('filename')
args = parser.parse_args()

class Dominoes:
	pass

def getDominoes():
	d = Dominoes()
	d.verticesToContainingDominoes = dict()
	d.dominoToWeight = []
	with open(args.filename) as f:
		line = f.readline().split()
		V = int(line[0])
		noDominoes = int(line[1])

		for v in range(V):
			d.verticesToContainingDominoes[v] = set()

		numDomino = 0
		for line in f:
			lineSplit = line.split()
			d.dominoToWeight.append(float(lineSplit[0]))
			# For each vertex w in the domino T, record T in w's  list 
			#:-1 is to avoid trailing space
			for w in lineSplit[3:-1]:
				d.verticesToContainingDominoes[int(w)].add(numDomino)
			numDomino += 1

	return d

d = getDominoes()
print(d.verticesToContainingDominoes)

try:
	with cplex.Cplex() as cpx:
		noDominoes = len(d.dominoToWeight)
		allDominoVariableNames = ["x{}".format(i) for i in range(noDominoes)]

		print("Adding {} binary variables".format(noDominoes))
		cpx.variables.add(names = allDominoVariableNames, types=cpx.variables.type.binary * noDominoes)

		print("Setting objective")
		cpx.objective.set_sense(cpx.objective.sense.minimize)
		for var in allDominoVariableNames:
			cpx.objective.set_linear(var, 1)

		print("Adding clique constraints")
		# The set of dominoes sharing any particular vertex form a clique
		for v,dominoes in d.verticesToContainingDominoes.items():
			# If only one tooth contains a given vertex, the constraint is redundant since the tooth variable is 0-1
			if len(dominoes) > 1:
				cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=["x{}".format(i) for i in dominoes], val=[1]*len(dominoes))], rhs=[1], senses='L')
		
		print("Adding parity variable 'k'")
		cpx.variables.add(names = ["k"], types=cpx.variables.type.integer)

		print("Adding parity constraint sum(x) = 2k+1")
		cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=allDominoVariableNames + ["k"], val=([1]*noDominoes) + [-2])], rhs=[1], senses='E')

		cpx.write('oddstab.lp')
		
except cplex.exceptions.CplexError as e:
	print(e)
	raise e
