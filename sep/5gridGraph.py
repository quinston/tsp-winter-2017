import findTspCps
import gridGraph
import itertools

V, E, Vstar, Estar = gridGraph.gridGraph(5)
vinf = 1

weights = dict(itertools.product(E, (1,)))

findTspCps.findCps(V, E, Vstar, Estar, vinf, weights)
