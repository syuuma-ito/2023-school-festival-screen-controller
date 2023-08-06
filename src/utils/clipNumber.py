def clipNumber(n, min, max):
    if min < n < max:
        return n
    elif min > n:
        return min
    else:
        return max
