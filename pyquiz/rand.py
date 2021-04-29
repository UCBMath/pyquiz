# Random numbers and objects

from pyquiz.expr import *
import fractions

# Create a random generator with a specified seed.
# This lets quiz generation be reproducible.
_random_gen = None

def _check_random_initialized():
    if _random_gen == None:
        raise Exception("You need to seed the random number generator.")

##
## Export methods from the _random_gen
##

def seed(s):
    """Set the seed for the random generator."""
    global _random_gen
    import random
    if _random_gen == None:
        _random_gen = random.Random(s)
    else:
        _random_gen.seed(s)

def random():
    """Give uniform at random float in [0.0, 1.0)"""
    _check_random_initialized()
    return _random_gen.random()

def uniform(a, b):
    """Gives uniform at random float in [a, b]"""
    _check_random_initialized()
    return _random_gen.uniform(a, b)

def triangular(low=0.0, high=1.0, mode=None):
    _check_random_initialized()
    return _random_gen.triangular(low, high, mode)

def randint(a, b):
    """Gives uniform at random integer in [a, b] (including both bounds)."""
    _check_random_initialized()
    return _random_gen.randint(a, b)

def randrange(a, b):
    """Gives uniform at random integer in [a, b) (excluding upper bound)."""
    _check_random_initialized()
    return _random_gen.randrange(a, b)

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
    _check_random_initialized()
    return _random_gen.choice(seq)

def sample(seq, k):
    """sample(seq, k) returns k randomly chosen elements from seq without replacement"""
    _check_random_initialized()
    return _random_gen.sample(seq, k)

def shuffle(x):
    """shuffle(x) shuffles the list x in place"""
    _check_random_initialized()
    return _random_gen.shuffle(x)

def gauss(mu=0.0, sigma=1.0):
    """normal distribution with mean mu and standard deviation sigma"""
    _check_random_initialized()
    # Note: _random_gen.gauss is not thread-safe.  This shouldn't matter, since this
    # is a single-threaded program, but better be safe.
    return _random_gen.normalvariate(mu, sigma)

normalvariate = gauss

# choices = _random_gen.choices
# lognormvariate = _random_gen.lognormvariate
# expovariate = _random_gen.expovariate
# vonmisesvariate = _random_gen.vonmisesvariate
# gammavariate = _random_gen.gammavariate
# betavariate = _random_gen.betavariate
# paretovariate = _random_gen.paretovariate
# weibullvariate = _random_gen.weibullvariate
# getrandbits = _random_gen.getrandbits
# randbytes = _random_gen.randbytes

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
        if gcd(x, y) == 1:
            break
    
