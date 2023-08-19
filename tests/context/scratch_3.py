from sympy import Interval, FiniteSet, Union, ProductSet

# als ProductSet aus Intervals
x1 = Interval(1, 2)
y1 = Interval(1, 2)
z1 = Interval(1, 2)

x2 = Interval(1, 1)
y2 = Interval(1, 1)
z2 = Interval(1, 1)

# als ProductSet aus FiniteSets
x3 = FiniteSet(1, 2, 3, 4)
y3 = FiniteSet(1, 2, 5, 6)
z3 = FiniteSet(1, 7, 8)

x4 = FiniteSet(2, 3, 4)
y4 = FiniteSet(1, 6)
z4 = FiniteSet(1)

x5 = FiniteSet(3, 4, 7)
y5 = FiniteSet(1, 6)
z5 = FiniteSet(1)

box1 = ProductSet(x1, y1, z1)
box2 = ProductSet(x2, y2, z2)

assert box2.is_subset(box1)

box3 = ProductSet(x3, y3, z3)
box4 = ProductSet(x4, y4, z4)
box5 = ProductSet(x5, y5, z5)

assert box4.is_subset(box3)
assert not box5.is_subset(box3)

# Hier funktionieren also Multidimensionale Sets. Mit einer einzigen Instanz eines Multidimensionalen Sets
#  lässt sich eine Menge aus Merkmalskombinationen abbilden: ein n-dimensionales ProductSet kann Merkmalsmengen
#  von n Variablen abbilden.
#  Dies funktioniert mit einem einzelnen Set jedoch nur, wenn Disjunktionen ausschließlich innerhalb einer Variable
#  und Konjunktionen ausschließlich zwischen verschiedenen Variablen auftreten.

# Beispiel:
x6 = FiniteSet(1, 2, 3, 4)
y6 = FiniteSet(1, 2, 3, 4)
z6 = FiniteSet(1, 2, 3)

# für den Ausdruck "(x == 2 | x == 3 | x == 4)" lässt sich das ProductSet:
x6a = FiniteSet(2, 3, 4)
y6a = y6
z6a = z6
box6a = ProductSet(x6a, y6a, z6a)
#  bilden.

# für den Ausdruck "(y == 2) & (x == 2 | x == 3 | x == 4)" lässt sich das ProductSet:
x6b = FiniteSet(2, 3, 4)
y6b = FiniteSet(2)
z6b = z6
box6b = ProductSet(x6b, y6b, z6b)
#  bilden.

# ######################################################
# ######################################################


# für den Ausdruck "(y == 2) | (x == 1)" müssen zwei ProductSets gebildet werden:
x6c1 = x6
y6c1 = FiniteSet(2)
z6c1 = z6
box6c1 = ProductSet(x6c1, y6c1, z6c1)

x6c2 = FiniteSet(1)
y6c2 = y6
z6c2 = z6
box6c2 = ProductSet(x6c2, y6c2, z6c2)

union6c = box6c1.union(box6c2)
# >>> Union(ProductSet({1}, {1, 2, 3, 4}, {1, 2, 3}), ProductSet({1, 2, 3, 4}, {2}, {1, 2, 3}))


# ######################################################
# ######################################################


# für den Ausdruck "((y == 2) & (x == 2 | x == 3 | x == 4)) | ((y == 3) & (x == 1))" müssen zwei ProductSets gebildet
#  werden:
x6d1 = FiniteSet(2, 3, 4)
y6d1 = FiniteSet(2)
z6d1 = z6
box6d1 = ProductSet(x6d1, y6d1, z6d1)

x6d2 = FiniteSet(1)
y6d2 = FiniteSet(3)
z6d2 = z6
box6d2 = ProductSet(x6d2, y6d2, z6d2)

union6d = box6d1.union(box6d2)
# >>> Union(ProductSet({1}, {3}, {1, 2, 3}), ProductSet({2, 3, 4}, {2}, {1, 2, 3}))


# #####
# #####

# Für die Evaluation eines booleschen Ausdrucks müsste dann:
#  1. Eine Union von ProductSets erstellt werden, die den Ausdruck abbilden
#  2. Evaluationen eines weiteren Ausdrucks ... ?


a1 = union6c.intersection(union6d)
# >>> Union(ProductSet({1}, {3}, {1, 2, 3}), ProductSet({2, 3, 4}, {2}, {1, 2, 3}))

# ######################################################
# ######################################################

