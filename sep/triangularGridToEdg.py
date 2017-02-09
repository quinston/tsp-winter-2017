import triangularGridGraph
import concorde

if __name__ == '__main__':
	height = int(input('height'))
	width = int(input('width'))
	vinf = int(input('vinf'))
	data = dict(eval(input('data ')))
	V, E, _, _ = triangularGridGraph.triangularGridGraph(height, width)
	concorde.produceEdgFormat(V, E, dict((int(a[1:]), b) for a,b in data if a[0] == "x"), allowNonintegerWeights=True)
