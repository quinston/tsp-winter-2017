import inequalities
import pprint

V = range(1,6+1)
E = [(1,2), (1,3), (1,5), (2,3), (2,6), (3,4), (4,5), (4,6), (5,6)]
Vstar = [(1,2,3), (1,3,4,5), (2,3,4,6), (4,5,6), (1,2,5,6)]
Estar = [(1,5), (1,2), (2,5), (1,3), (3,5), (2,3), (2,4), (3,4), (4,5)]

weights = {(1,2): 10, (1,3): 10, (1,5): 1, (2,3): 10, (2,6): 1, (3,4): 1, (4,5): 10, (4,6): 10, (5,6): 10}
vinf = 1

print(inequalities.makeExtendedLp(V, E, Vstar, Estar, vinf, weights))
print(list(enumerate(inequalities.enumerateExtendedLpVariables(V, E, Vstar, Estar, vinf), 1)))

# A noninteger point for the above weights is [.5, .5, 1, .5, 1, 1, .5, .5, .5]
# z4,3 = z7,4 = z8,3 = z9,4 = 0.5
tmp = inequalities.makeExtendedLpConstraintMatrix(V, E, Vstar, Estar, vinf)
A = [r[0] for r in tmp]
b = [r[1] for r in tmp]
x = [.5, .5, 1, .5, 1, 1, .5, .5, .5, 
# extra variables
.5, 0, 0, 0, 0, 0, .5, .5, 0, .5, 0, 0
]

print(pprint.pformat(A), b)

import cgsep
cgsep.solve(x, A, b)
