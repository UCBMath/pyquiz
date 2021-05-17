r"""(Internal) A "dynamic variable" is global state that can be saved
and restored in a standard way.  This is used to make certain
configurations (like for tex output) only affect certain questions,
question groups, or quizzes."""

DYNAMIC_VARIABLES = [{}]
r"""This is a list of dictionaries of values of dynamic variables at a particular level."""

def reset():
    """(internal) Reset the state of the entire dynamic variable system."""
    DYNAMIC_VARIABLES.clear()
    DYNAMIC_VARIABLES.append({})

def enter():
    """(internal) Enter a new dynamic variable scoping level."""
    DYNAMIC_VARIABLES.append({})

def leave():
    """(internal) Leave the current dynamic variable scoping level."""
    if len(DYNAMIC_VARIABLES) <= 1:
        raise Exception("(internal error) Cannot leave top level dynamic scope")
    DYNAMIC_VARIABLES.pop()

def get(name, default=None):
    """(internal) Get the current value of the dynamic variable with name
    `name`.  If there is no such dynamic variable, return `default`."""
    for scope in reversed(DYNAMIC_VARIABLES):
        try:
            return scope[name]
        except KeyError:
            pass
    return default

def set(name, val):
    """(internal) Set the value of the dynamic variable with name `name`
    to `val` in the current scope."""
    DYNAMIC_VARIABLES[-1][name] = val
