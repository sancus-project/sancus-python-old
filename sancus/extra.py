# -*- coding: utf-8 -*-

class Table(object):
    def __init__(self, **kw):
        self._fields = kw.copy()

    def __getattr__(self, key, default=None):
        """Maps dict items to attributes"""
        return self._fields.get(key, default)

    def __setattr__(self, key, value):
        """Maps attributes to dict items"""
        if key == '_fields':
            object.__setattr__(self, key, value)
        else:
            self._fields[key] = value

    def copy(self):
        return type(self)(**self._fields)

    def __repr__(self):
        data = []
        for k,v in self._fields.iteritems():
            data.append("%s = %r" % (k,v))

        data = ', '.join(data)

        return ''.join(("Table(", data, ")"))
