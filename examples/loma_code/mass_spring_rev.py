class MassSpringConfig:
    mass : float
    length : float
    k : float
    g : float

def hamiltonian(q : In[Array[float]], p : In[Array[float]], c : In[MassSpringConfig]) -> float:
    K : float
    K = K + 0.5 * p[0] * p[0] / c.mass
    K = K + 0.5 * p[1] * p[1] / c.mass
    K = K + 0.5 * p[2] * p[2] / c.mass
    K = K + 0.5 * p[3] * p[3] / c.mass
    K = K + 0.5 * p[4] * p[4] / c.mass
    K = K + 0.5 * p[5] * p[5] / c.mass
    K = K + 0.5 * p[6] * p[6] / c.mass
    K = K + 0.5 * p[7] * p[7] / c.mass
    K = K + 0.5 * p[8] * p[8] / c.mass
    K = K + 0.5 * p[9] * p[9] / c.mass

    U : float
    # mass spring potential
    tmp : float = sqrt((q[0] - q[2]) * (q[0] - q[2]) + (q[1] - q[3]) * (q[1] - q[3])) - c.length
    U = U + 0.5 * c.k * tmp * tmp
    tmp = sqrt((q[2] - q[4]) * (q[2] - q[4]) + (q[3] - q[5]) * (q[3] - q[5])) - c.length
    U = U + 0.5 * c.k * tmp * tmp
    tmp = sqrt((q[4] - q[6]) * (q[4] - q[6]) + (q[5] - q[7]) * (q[5] - q[7])) - c.length
    U = U + 0.5 * c.k * tmp * tmp
    tmp = sqrt((q[6] - q[8]) * (q[6] - q[8]) + (q[7] - q[9]) * (q[7] - q[9])) - c.length
    U = U + 0.5 * c.k * tmp * tmp
    # gravity potential
    U = U + c.mass * c.g * q[1]
    U = U + c.mass * c.g * q[3]
    U = U + c.mass * c.g * q[5]
    U = U + c.mass * c.g * q[7]
    U = U + c.mass * c.g * q[9]

    return K + U

d_hamiltonian = rev_diff(hamiltonian)

def gradH(q : In[Array[float]], p : In[Array[float]], c : In[MassSpringConfig],
          dq : Out[Array[float]], dp : Out[Array[float]]):
    d_c : MassSpringConfig
    d_hamiltonian(q, dq, p, dp, c, d_c, 1.0)
