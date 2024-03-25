class PendulumConfig:
    mass : float
    radius : float
    g : float

def hamiltonian(q : In[float], p : In[float], c : In[PendulumConfig]) -> float:
    K : float = p * p / (c.mass * c.radius * c.radius)
    y : float = -c.radius * cos(q)
    U : float = c.mass * c.g * y
    return K + U

d_hamiltonian = fwd_diff(hamiltonian)

def dHdq(q : In[float], p : In[float], c : In[PendulumConfig]) -> float:
    d_q : Diff[float]
    d_q.val = q
    d_q.dval = 1.0
    d_p : Diff[float]
    d_p.val = p
    d_p.dval = 0.0
    # dvals are automatically initialized to zero
    d_c : Diff[PendulumConfig]
    d_c.mass.val = c.mass
    d_c.radius.val = c.radius
    d_c.g.val = c.g
    return d_hamiltonian(d_q, d_p, d_c).dval

def dHdp(q : In[float], p : In[float], c : In[PendulumConfig]) -> float:
    d_q : Diff[float]
    d_q.val = q
    d_q.dval = 0.0
    d_p : Diff[float]
    d_p.val = p
    d_p.dval = 1.0
    # dvals are automatically initialized to zero
    d_c : Diff[PendulumConfig]
    d_c.mass.val = c.mass
    d_c.radius.val = c.radius
    d_c.g.val = c.g
    return d_hamiltonian(d_q, d_p, d_c).dval
