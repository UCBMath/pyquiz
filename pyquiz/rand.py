# Random numbers and objects

import random
from pyquiz.expr import *
import fractions

# Create a random generator with a specified seed.
# This lets quiz generation be reproducible.
_random_gen = random.Random(1)

##
## Export methods from the _random_gen
##

# Set the seed for the random generator
seed = _random_gen.seed
# Get the internal state of the random generator
getstate = _random_gen.getstate
# Set the internal state of the random generator (obtained from getstate)
setstate = _random_gen.setstate

# Give uniform at random float in [0.0, 1.0)
random = _random_gen.random
# Gives uniform at random float in [a, b]
uniform = _random_gen.uniform
triangular = _random_gen.triangular

# Gives uniform at random integer in [a, b]
randint = _random_gen.randint
# Gives uniform at random integer in [a, b)
randrange = _random_gen.randrange

def randint_nonzero(a, b):
    """Returns a uniform at random integer in [a,b]-{0}."""
    if a == b == 0:
        raise ValueError
    while True:
        val = randint(a, b)
        if val != 0:
            return val
def randrange_nonzero(a, b):
    """Returns a uniform at random integer in [a,b)-{0}."""
    if a == 0 and b == 1:
        raise ValueError
    while True:
        val = randrange(a, b)
        if val != 0:
            return val


# Chooses a uniform at random element from a given sequence
choice = _random_gen.choice
# sample(seq, k) returns k randomly chosen elements from seq without replacement
sample = _random_gen.sample
# shuffle(list) shuffles the list in place
shuffle = _random_gen.shuffle
choices = _random_gen.choices
normalvariate = _random_gen.normalvariate
lognormvariate = _random_gen.lognormvariate
expovariate = _random_gen.expovariate
vonmisesvariate = _random_gen.vonmisesvariate
gammavariate = _random_gen.gammavariate
gauss = _random_gen.gauss
betavariate = _random_gen.betavariate
paretovariate = _random_gen.paretovariate
weibullvariate = _random_gen.weibullvariate
getrandbits = _random_gen.getrandbits
randbytes = _random_gen.randbytes

def rand_invertible_2x2(a, b):
    """Generate a random 2x2 matrix with integer entries and nonzero determinant,
    where all entries are in the range [a, b]."""

    while True:
        x = randint(a, b)
        y = randint(a, b)
        z = randint(a, b)
        w = randint(a, b)
        if x * w - y * z != 0:
            return matrix([x, y],
                          [z, w])

def rand_unimodular_2x2(a, b):
    """Generate a random 2x2 matrix with determinant=1, where all the
    entries are in the range [a, b].

    Warning: might infinite loop there are no such matrices!"""

    # We generate them uniformly at random from the set of all matrices whose
    # entries are drawn from [a, b].
    
    # [[x, y], [z, w]]
    x = randint(a, b)
    while True:
        y = randint(a, b)
        if gcd(x, y) == 1:
            break
    
