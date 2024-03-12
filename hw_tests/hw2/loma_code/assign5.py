def assign5(x : float, y : float) -> float:
    z : float = x * y
    w : float = z
    z = x + y
    w = w + z * z
    z = 2.0 * x
    z = z + 1.0
    z = 3.0 * z * z + w

    # t : Array[float, 5]
    # z : float = x * y
    # w : float = z
    
    # t[0] = z
    # z = x + y

    # t[1] = w    
    # w = w + z * z

    # t[2] = z
    # z = 2 * x
    
    # t[3] = z
    # z = z + 1

    # t[4] = z
    # z = 3.0 * z * z + w

    # dz = dreturn
    # # z = 3.0 * z * z + w
    # z = t[4]
    # new_dw = dz
    # new_dz = 2 * 3 * z * dz
    # dz = 0
    # dw += dz
    # dz += new_dz
    # ...
    return z

d_assign5 = rev_diff(assign5)
