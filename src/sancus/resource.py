def key_to_int(d, k, fallback=None):
    """if present, convert key to int(), otherwise set to fallback"""
    v = fallback
    if k in d:
        v = int(d[k])
    d[k] = v

def key_in_enum(d, k, enum, fallback=None):
    """if present, check against the given enum, otherwise set to fallback"""
    if k in d:
        if d[k] not in enum:
            raise ValueError
    else:
        d[k] = fallback
