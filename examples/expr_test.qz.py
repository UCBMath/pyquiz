from pyquiz.expr import *

# This file does not contain a quiz.  Instead, it demonstrates using expressions.

a = var("a")

print(a**2 + 3*a + 1)
print(a**2 + 3*a + 1 - 2*a)

print((a + 1)**2)
print(expand((a + 1)**2))

print(replace((a + 1)**2, (a, 5)))

print(rf"\( (a+1)^2 = {expand((a + 1)**2)} \)")

print(rf"\( \frac{{(a+1)^2}}{{ {expand((a + 1)**2)} }} = 1 \)")

A = matrix([1, 2, 3],
           [4, 5, 6],
           [7, 8, a])
print(A)
print(A @ A)
print(replace(A @ A, (a, 9)))
