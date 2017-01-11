import findTspCps

V= range(1,16+1)

E = [(a,a+1) for a in range(1, 4+1)] + [(a,a+5) for a in range(1,5+1)] +[(a,a+1) for a in range(6,9+1)] +[(a,a+5) for a in range(6,10+1)] +[(a,a+1) for a in range(11, 14+1)] +[(a,a+5) for a in range(11, 15+1)] +[(a,a+5) for a in range(11,15+1)] +[(a,a+1) for a in range(16,19+1)] +[(a,a+1) for a in range(21, 24+1)] 

Vstar = [(a,a+1,a+5,a+6) for a in range(1,4+1)] +[(a,a+1,a+5,a+6) for a in range(6, 9+1)] +[(a,a+1,a+5,a+6) for a in range(11,14+1)] +[(a,a+1,a+5,a+6) for a in range(16, 19+1)] +[(1,2,3,4,5,10,15,20,25,24,23,22,21,16,11,6)]

Estar = [(a, 17) for a in range(1,4+1)] + [(1,17)] + [(a, a-1) for a in range(2,4+1)] + [(4,17)] + [(a,a+4) for a in range(1,4+1)] + [(5,17)] + [(a, a-1) for a in range(6,8+1)] + [(8,17)] + [(a,a+4) for a in range(5,8+1)] + [(9,17)] + [(a, a-1) for a in range(10,12+1)] + [(12,17)] + [(a,a+4) for a in range(9,12+1)] + [(13,17)] + [(a, a-1) for a in range(14,16+1)] + [(16,17)] + [(a,17) for a in range(13,16+1)]

vinf = 1

import itertools
weights = dict(itertools.product(E, (1,)))

findTspCps.findCps(V, E, Vstar, Estar, vinf, weights)
