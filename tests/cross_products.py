from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *
seed(100)

for i in range(100):
    u = rand_matrix(3, 1, -10, 10)
    v = rand_matrix(3, 1, -10, 10)
    w = rand_matrix(3, 1, -10, 10)
    assert dot(cross(u, v), w) == det(matrix_with_cols(u, v, w))
