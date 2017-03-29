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
		print("Adding {} binary variables".format(noDominoes))
		cpx.variables.add(names = ["x{}".format(i) for i in range(noDominoes)], types=cpx.variables.type.binary * noDominoes)

		print("Adding constraints")
		# The set of dominoes sharing any particular vertex form a clique
		for v,dominoes in d.verticesToContainingDominoes.items():
			cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind=list(dominoes), val=[1]*len(dominoes))], rhs=[1], senses='L')
		
		cpx.write('aaaa.lp')
except cplex.exceptions.CplexError as e:
	print(e)
	raise e
