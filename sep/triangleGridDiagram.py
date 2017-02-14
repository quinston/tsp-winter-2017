"""
PUts weights on the edges that label the whole graph
"""

import triangularGridGraph
import inequalities
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('height', type=int, help='Number of vertices on the vertical')
parser.add_argument('width', type=int, help='Number of vertices on the horzitonal')
parser.add_argument('vinf', type=int, help='One-indexed number identifying v_inf')
args = parser.parse_args()

height, width, vinf = (args.height, args.width, args.vinf)


V,E,Vstar,Estar = triangularGridGraph.triangularGridGraph(height, width)
vinf = 13

"""
Give x???  a weight of ???
Give z??,## a weight of ??? + ## * 0.001
"""

data = dict((name, int(name[1:]) if name[0] == "x" else float(name[1:name.find(",")]) + float(name[name.find(",")+1:]) * 0.001) for name in inequalities.enumerateExtendedLpVariables(V, E, Vstar, Estar, vinf))
print(data)

import trigridDisplayer

trigridDisplayer.displayTriangularGrid(height, width, vinf, data)
