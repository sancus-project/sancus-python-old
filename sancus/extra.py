# -*- coding: utf-8 -*-

class Enum(object):
    def __init__(self, *d):
        for i in range(len(d)):
            setattr(self, d[i], i)

class Table(object):
    def __init__(self, **kw):
        self._fields = dict((k, v) for k, v in kw.iteritems() if v is not None)

    def __getattr__(self, key, default=None):
        """Maps dict items to attributes"""
        return self._fields.get(key, default)

    def __setattr__(self, key, value):
        """Maps attributes to dict items"""
        if key == '_fields':
            object.__setattr__(self, key, value)
        elif value is not None:
            self._fields[key] = value
        else:
            try:
                del self._fields[key]
            except KeyError:
                pass

    def __setitem__(self, key, value):
        """Also act as a dict"""
        if value is not None:
            self._fields[key] = value
        else:
            try:
                del self._fields[key]
            except KeyError:
                pass

    def __getitem__(self, key, default=None):
        """Also act as a dict"""
        return self._fields.get(key, default)

    def copy(self):
        return type(self)(**self._fields)

    def __iter__(self):
        return self._fields.iteritems()

    def __repr__(self):
        data = []
        for k,v in self._fields.iteritems():
            data.append("%s = %r" % (k,v))

        data = ', '.join(data)

        return "Table(%s)" % data

def Tablify(o):
    if isinstance(o, Table):
        pass
    elif isinstance(o, dict):
        o = Table(**o)
    elif isinstance(o, tuple) or isinstance(o, list):
        for i in range(len(o)):
            o[i] = Tablify(o[i])
    else:
        return o

    for k,v in o:
        o[k] = Tablify(v)

    return o
