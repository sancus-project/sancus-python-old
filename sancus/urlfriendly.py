# -*- coding: utf-8 -*-
import string
from unidecode import unidecode

_valid = string.ascii_lowercase + string.digits + "._-"
def urlfriendlyname(s, white='_'):
    s = unidecode(s).lower()

    s = ''.join(c if c in _valid else white for c in s).strip(white)
    if len(s) > 0:
        return s
    else:
        return None
