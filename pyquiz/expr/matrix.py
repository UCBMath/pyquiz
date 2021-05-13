r"""
Functions for matrices and vectors.
"""

from .core import *
from .manipulate import *

__all__ = [
    "vector", "matrix", "is_vector",
    "nrows", "ncols", "rows", "cols",
    "transpose", "matrix_with_cols", "matrix_with_rows",
    "diagonal_matrix", "identity_matrix",
    "row_reduce", "rank", "nullity",
    "det"
]

def vector(*elts):
    """Example: `vector(1,2,3)` returns `matrix([1], [2], [3])`"""
    if len(elts) == 0:
        raise ValueError("We require vectors to have at least one row.")
    return Expr("matrix", [[elt] for elt in elts])
def matrix(*rows):
    """Example: `matrix([1,2],[3,4])` for a matrix with rows `[1,2]` and `[3,4]`."""
    if len(rows) == 0:
        raise ValueError("We require matrices to have at least one row and column.")
    if any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Not all rows in the matrix have the same length.")
    return Expr("matrix", rows)

def diagonal_matrix(*entries):
    """`diagonal_matrix(a11, a22, ..., ann)` gives an nxn matrix whose diagonal is given by these n expressions."""
    if not entries:
        raise ValueError("We require matrices to have at least one row and column.")
    return matrix(*([entries[i] if i == j else 0 for j in range(len(entries))] for i in range(len(entries))))


def identity_matrix(n):
    """Returns the n by n identity matrix."""
    assert isinstance(n, int)
    if n <= 0:
        raise ValueError("We require matrices to have at least one row and column.")
    return matrix(*[[1 if i == j else 0 for j in range(n)] for i in range(n)])

def is_vector(e):
    """A vector is a matrix whose rows each have one entry."""
    return head(e) == "matrix" and ncols(e) == 1

def nrows(e):
    """Gives the number of rows in the matrix."""
    if head(e) != "matrix":
        raise ValueError("expecting a matrix")
    return len(e.args)

def ncols(e):
    """Gives the number of columns in the matrix."""
    if head(e) != "matrix":
        raise ValueError("expecting a matrix")
    return len(e.args[0])

def rows(e):
    """Returns a list of the rows of the matrix as column vectors."""
    if head(e) != "matrix":
        raise ValueError("expecting a matrix")
    return [vector(*row) for row in e.args]

def cols(e):
    """Returns a list of the columns of the matrix as column vectors."""
    if head(e) != "matrix":
        raise ValueError("expecting a matrix")
    return [vector(*col) for col in zip(*e.args)]

def transpose(e):
    """Returns the transpose of the matrix."""
    return matrix(*(list(col) for col in zip(*e.args)))

def matrix_with_cols(*cols):
    """Returns a matrix with the columns given by the column vectors.
    More generally, accepts matrices all with the same number of rows,
    and produces a block matrix of the matrices horizontally
    concatenated.

    Identity: `A == matrix_with_cols(*cols(A))`

    Example: `matrix_with_cols(A, v)` is an augmented matrix.

    """

    if len(cols) == 0:
        raise ValueError("Matrices must have at least one column.")
    if not all(head(c) == "matrix" for c in cols):
        raise ValueError("Not all the arguments are matrices")
    m = nrows(cols[0])
    if not all(m == nrows(c) for c in cols):
        raise ValueError("Not all the matrices have the same number of rows.")

    rows = []
    for i in range(m):
        row = []
        rows.append(row)
        for c in cols:
            row.extend(c.args[i])
    return Expr("matrix", rows)

def matrix_with_rows(*rows):
    """Returns a matrix with the rows given by the row vectors.  More
    generally, accepts matrices all with the same number of columns,
    and produces a block matrix of the matrices vertically
    concatenated.
    """

    if len(rows) == 0:
        raise ValueError("Matrices must have at least one row.")
    if not all(head(r) == "matrix" for r in rows):
        raise ValueError("Not all the arguments are matrices")
    n = ncols(rows[0])
    if not all(n == ncols(r) for r in rows):
        raise ValueError("Not all the matrices have the same number of columns.")

    mrows = []
    for r in rows:
        mrows.extend(r.args)
    return Expr("matrix", mrows)

@downvalue("Part")
def rule_part_vector(e, idx):
    """Extract a Part of a vector using a single index.  Uses 1-indexing."""
    if head(e) != "matrix" or isinstance(idx, Expr):
        raise Inapplicable
    if type(idx) != int:
        raise ValueError(f"Expecting integer for index, not {idx}")
    if ncols(e) != 1:
        raise ValueError(f"Need two indices to index a matrix, not one.")
    if not (1 <= idx <= nrows(e)):
        raise ValueError(f"Index {idx} is out of bounds for vector of length {nrows(e)}.")
    return e.args[idx - 1][0]

@downvalue("Part")
def rule_part_matrix(e, idx1, idx2):
    """Extract a Part of a matrix using two indices.  Uses 1-indexing."""
    if head(e) != "matrix" or isinstance(idx1, Expr) or isinstance(idx2, Expr):
        raise Inapplicable
    if type(idx1) != int:
        raise ValueError(f"Expecting integer for first index, not {idx}")
    if type(idx2) != int:
        raise ValueError(f"Expecting integer for second index, not {idx}")
    if not (1 <= idx1 <= nrows(e)):
        raise ValueError(f"First index {idx1} is out of bounds for matrix with {nrows(e)} rows.")
    if not (1 <= idx2 <= ncols(e)):
        raise ValueError(f"Second index {idx2} is out of bounds for matrix with {ncols(e)} columns.")
    return e.args[idx1 - 1][idx2 - 1]

@downvalue("det", def_expr=True)
def det(e):
    """Computes the determinant of the given matrix"""
    if head(e) != "matrix":
        raise Inapplicable
    def expand(rows):
        if len(rows) == 1:
            assert len(rows[0]) == 1
            return rows[0][0]
        # Expand along the first column
        acc = 0
        for i in range(len(rows)):
            submatrix = [row[1:] for row in rows[:i] + rows[i+1:]]
            acc += (-1) ** i * rows[i][0] * expand(submatrix)
        return acc

    r = expand(e.args)
    return r

@downvalue("Times")
def rule_scalar_multiplication(s, *args):
    """Scalar multiplication of matrices.  This rule should come *after*
    the generic Times rule so that multiplying by 0 doesn't give the
    scalar 0."""
    if head(s) != "number":
        raise Inapplicable
    for i, a in enumerate(args):
        if head(a) == "matrix":
            a2 = Expr("matrix", [[s * x for x in row] for row in a.args])
            return expr("Times", *args[:i], a2, *args[i+1:])
    raise Inapplicable

@downvalue("Plus")
def rule_matrix_addition(*args):
    """Addition of vectors and matrices of compatible size.  Raises a `ValueError` if incompatible."""
    for i in range(len(args) - 1):
        if head(args[i]) != "matrix":
            continue
        for j in range(i + 1, len(args)):
            if head(args[j]) != "matrix":
                continue
            if nrows(args[i]) != nrows(args[j]):
                raise ValueError("The added matrices have different numbers of rows.")
            if ncols(args[i]) != ncols(args[j]):
                raise ValueError("The added matrices have different numbers of columns.")
            a2 = Expr("matrix", [[ci + cj for ci, cj in zip(rowi, rowj)]
                                 for rowi, rowj in zip(args[i].args, args[j].args)])
            return expr("Plus", *args[:i], a2, *args[i+1:j], *args[j+1:])
    raise Inapplicable

# TODO make this an "expansion" that doesn't apply during evaluation?
@downvalue("MatTimes")
def reduce_matmul(A, B):
    if head(A) != "matrix" or head(B) != "matrix":
        raise Inapplicable
    if ncols(A) != nrows(B):
        raise ValueError("Number of columns of first argument does not equal number of rows of second argument")
    C = []
    for i in irange(nrows(A)):
        row = []
        C.append(row)
        for j in irange(ncols(B)):
            x = 0
            for k in irange(ncols(A)):
                x += A[i,k] * B[k,j]
            row.append(x)
    return matrix(*C)

@downvalue("adj", def_expr=True)
def adj(e):
    """Computes the adjugate matrix"""
    if head(e) != "matrix":
        raise Inapplicable
    rows = e.args
    if len(rows) != len(rows[0]):
        raise ValueError("expecting square matrix")
    n = len(rows)
    def C(i0, j0):
        """(i,j) cofactor"""
        rows2 = [[v for j,v in enumerate(row) if j != j0] for i,row in enumerate(rows) if i != i0]
        return det(matrix(*rows2))
    return matrix(*[[(-1)**(i + j) * C(j, i) for j in range(n)] for i in range(n)])

@downvalue("Pow")
def reduce_matrix_inverse(A, n):
    if head(A) != "matrix" or n != -1:
        raise Inapplicable

    if nrows(A) != ncols(A):
        raise ValueError("Taking the inverse of a non-square matrix")

    d = det(A)
    a = adj(A)
    return matrix(*[[frac(v, d) for v in row] for row in a.args])

def row_reduce(e, rref=True, steps_out=None):
    """Puts the matrix into row echelon form.

    * If `rref=True` then gives the reduced row echelon form.

    * If `rref=False` then gives row echelon form.

    Follows the algorithm in Lay.

    If `steps_out` if set to a list of your choosing, then it will be
    populated with TeX for each rule that was applied.
    ```python
    steps = []
    row_reduce(A, steps_out=steps)
    print(",".join(steps))
    ```
    """
    if head(e) != "matrix":
        raise ValueError("expecting matrix")

    # copy the matrix
    mat = [[v for v in row] for row in e.args]

    rows = len(mat)
    cols = len(mat[0])
    def swap(i, j):
        # R_i <-> R_j
        mat[i], mat[j] = mat[j], mat[i]
        if steps_out != None:
            steps_out.append(rf"R_{i} \leftrightarrow R_{j}")
    def scale(i, c):
        # c * R_i -> R_i
        for k in range(cols):
            mat[i][k] *= c
        if steps_out != None:
            Ri = var(f"R_{i}")
            steps_out.append(rf"{c * Ri} \rightarrow {Ri}")
    def replace(i, j, c):
        # R_i + c * R_j -> R_i
        for k in range(cols):
            mat[i][k] += c * mat[j][k]
        if steps_out != None:
            Ri = var(f"R_{i}")
            Rj = var(f"R_{j}")
            steps_out.append(rf"{Ri + c * Rj} \rightarrow {Ri}")
    def is_zero(i):
        # whether row i is a zero row
        return all(mat[i][k] == 0 for k in range(cols))

    i = 0
    j = 0
    last_nz = rows - 1
    while last_nz >= 0 and is_zero(last_nz):
        last_nz -= 1
    while i < rows and j < cols:
        if is_zero(i):
            if i >= last_nz:
                break
            swap(i, last_nz)
            last_nz -= 1
        if mat[i][j] == 0:
            for k in range(i + 1, last_nz + 1):
                if mat[k][j] != 0:
                    swap(i, k)
                    break
        if mat[i][j] == 0:
            j += 1
            continue
        if mat[i][j] != 1:
            scale(i, frac(1, mat[i][j]))
        for k in range(i + 1, last_nz + 1):
            if mat[k][j] != 0:
                replace(k, i, -mat[k][j])
        i += 1
        j += 1
    if rref:
        for i in range(last_nz, -1, -1):
            for j in range(cols):
                if mat[i][j] != 0:
                    # in fact, the entry is 1
                    for k in range(i - 1, -1, -1):
                        if mat[k][j] != 0:
                            replace(k, i, -mat[k][j])
                    break
    return matrix(*mat)


@downvalue("rank", def_expr=True)
def rank(e):
    """Gives the rank of the matrix"""
    if head(e) != "matrix":
        raise Inapplicable
    e = row_reduce(e, rref=False)
    assert head(e) == "matrix"
    return sum(1 for row in e.args if not all(v == 0 for v in row))

@downvalue("nullity", def_expr=True)
def nullity(e):
    """Gives the nullity of the matrix"""
    if head(e) != "matrix":
        raise Inapplicable
    return ncols(e) - rank(e)
