from urllib import quote_plus, unquote_plus

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

def url_to_unicode(s):
    """url encode a unicode string"""
    return unicode(unquote_plus(s), 'utf-8')

def unicode_to_url(s):
    """url decode a unicode string"""
    return quote_plus(s.encode('utf-8'))
