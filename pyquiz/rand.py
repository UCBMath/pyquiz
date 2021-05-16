# Random numbers and objects

from pyquiz.expr import *
import pyquiz.dynamic
import fractions
import math

__all__ = [
    "seed", "duplicate_random",
    "random", "uniform", "triangular",
    "randint", "randrange", "randint_nonzero", "randrange_nonzero",
    "choice", "sample", "shuffle", "gauss", "normalvariate",
    "rand_matrix", "rand_diagonal_matrix", "rand_invertible_2x2", "rand_unimodular_2x2"
]

def random_gen():
    """Get the random generator from the dynamic scope."""
    g = pyquiz.dynamic.get("random_gen")
    if g == None:
        raise Exception("You need to seed the random number generator.")
    return g

##
## Export methods from the random_gen()
##

def seed(s):
    """Create a random generator with the given seed.

    The random generator is a dynamic variable.  This means if this is
    used inside, for example, a question group, once the question
    group is ended the random generator is destroyed, and if there was
    a random generator defined before the question group started it is
    restored.
    """
    import random
    pyquiz.dynamic.set("random_gen", random.Random(s))

def duplicate_random():
    """Take the current random generator and duplicate it in the current
    dynamic scope.  This can be used to have multiple questions get
    the same random numbers.  (It's not clear exactly why you would
    want to do this, but it's here just in case it might be useful.)
    """
    import random
    g = random.Random()
    g.setstate(random_gen().getstate())
    pyquiz.dynamic.set("random_gen", g)

def random():
    """Give uniform at random float in [0.0, 1.0)"""
    return random_gen().random()

def uniform(a, b):
    """Gives uniform at random float in [a, b]"""
    return random_gen().uniform(a, b)

def triangular(low=0.0, high=1.0, mode=None):
    return random_gen().triangular(low, high, mode)

def randint(a, b):
    """Gives uniform at random integer in [a, b] (including both bounds)."""
    return random_gen().randint(a, b)

def randrange(a, b):
    """Gives uniform at random integer in [a, b) (excluding upper bound)."""
    return random_gen().randrange(a, b)

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

def choice(seq):
    """Chooses a uniform at random element from a given sequence"""
    return random_gen().choice(seq)

def sample(seq, k):
    """sample(seq, k) returns k randomly chosen elements from seq without replacement"""
    return random_gen().sample(seq, k)

def shuffle(x):
    """shuffle(x) shuffles the list x in place"""
    return random_gen().shuffle(x)

def gauss(mu=0.0, sigma=1.0):
    """normal distribution with mean mu and standard deviation sigma"""
    # Note: random.gauss is not thread-safe.  This shouldn't matter, since this
    # is a single-threaded program, but better be safe.
    return random_gen().normalvariate(mu, sigma)

normalvariate = gauss
r"""
A synonym for `gauss`.
"""

# choices = random_gen().choices
# lognormvariate = random_gen().lognormvariate
# expovariate = random_gen().expovariate
# vonmisesvariate = random_gen().vonmisesvariate
# gammavariate = random_gen().gammavariate
# betavariate = random_gen().betavariate
# paretovariate = random_gen().paretovariate
# weibullvariate = random_gen().weibullvariate
# getrandbits = random_gen().getrandbits
# randbytes = random_gen().randbytes

def rand_matrix(n, m, a, b):
    """Generate a random nxm matrix with integer entries in the range [a, b]."""
    return matrix(*[[randint(a, b) for j in range(m)] for i in range(n)])

def rand_diagonal_matrix(n, a, b):
    """Generate a random nxn diagonal matrix with integer entries in the range [a, b]."""
    return matrix(*[[randint(a, b) if i == j else 0 for j in range(n)] for i in range(n)])

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
        if math.gcd(x, y) == 1:
            break

    while True:
        z = randint(a, b)
        w = randint(a, b)
        if x * w - y * z == 1:
            return matrix([x, y],
                          [z, w])
