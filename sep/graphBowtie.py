import inequalities
import pprint

V = range(1,6+1)
E = [(1,2), (1,3), (1,5), (2,3), (2,6), (3,4), (4,5), (4,6), (5,6)]
Vstar = [(1,2,3), (1,3,4,5), (2,3,4,6), (4,5,6), (1,2,5,6)]
Estar = [(1,5), (1,2), (2,5), (1,3), (3,5), (2,3), (2,4), (3,4), (4,5)]

weights = {(1,2): 10, (1,3): 10, (1,5): 1, (2,3): 10, (2,6): 1, (3,4): 1, (4,5): 10, (4,6): 10, (5,6): 10}
vinf = 5

print(inequalities.makeExtendedLp(V, E, Vstar, Estar, vinf, weights))
print(list(enumerate(inequalities.enumerateExtendedLpVariables(V, E, Vstar, Estar, vinf), 1)))
# [(1, 'x1'), (2, 'x2'), (3, 'x3'), (4, 'x4'), (5, 'x5'), (6, 'x6'), (7, 'x7'), (8, 'x8'), (9, 'x9'), (10, 'z1,1'), (11, 'z1,5'), (12, 'z2,1'), (13, 'z2,2'), (14, 'z4,1'), (15, 'z4,3'), (16, 'z5,3'), (17, 'z5,5'), (18, 'z6,2'), (19, 'z6,3'), (20, 'z8,3'), (21, 'z8,4')]


# A noninteger point for the above weights is [.5, .5, 1, .5, 1, 1, .5, .5, .5]
#z1,1 = z2,1 = z4,3 = z8,3 = .5
tmp = inequalities.makeExtendedLpConstraintMatrix(V, E, Vstar, Estar, vinf)
A = [r[0] for r in tmp]
b = [r[1] for r in tmp]
xMap = {
        'x1': .5,
        'x2': .5,
        'x3': 1,
        'x4': .5,
        'x5': 1,
        'x6': 1,
        'x7': .5,
        'x8': .5,
        'x9': .5,
        'z1,1': .5,
        'z2,1': .5,
        'z4,3': .5,
        'z8,3': .5
        }
x = [(xMap[variableName] if variableName in xMap else 0) for variableName in inequalities.enumerateExtendedLpVariables(V, E, Vstar, Estar, vinf)]


import cgsep
cgsep.solve(x, A, b)
