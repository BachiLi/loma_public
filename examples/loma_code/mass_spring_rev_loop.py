class MassSpringConfig:
    mass : float
    length : float
    k : float
    g : float
    n : int

def square(x : In[float]) -> float:
    return x * x

def hamiltonian(q : In[Array[float]], p : In[Array[float]], c : In[MassSpringConfig]) -> float:
    K : float
    i : int = 0
    while (i < 2 * c.n, max_iter := 1000):
        K = K + 0.5 * p[i] * p[i] / c.mass
        i = i + 1

    U : float
    # mass spring potential
    tmp : float
    i = 0
    while (i < c.n - 1, max_iter := 1000):
        tmp = sqrt(square(q[2 * i] - q[2 * i + 2]) + square(q[2 * i + 1] - q[2 * i + 3])) - c.length
        U = U + 0.5 * c.k * tmp * tmp
        i = i + 1

    # gravity potential
    i = 0
    while (i < c.n, max_iter := 1000):
        U = U + c.mass * c.g * q[2 * i + 1]
        i = i + 1

    return K + U

d_hamiltonian = rev_diff(hamiltonian)

def gradH(q : In[Array[float]], p : In[Array[float]], c : In[MassSpringConfig],
          dq : Out[Array[float]], dp : Out[Array[float]]):
    d_c : MassSpringConfig
    d_hamiltonian(q, dq, p, dp, c, d_c, 1.0)
