# -*- coding: utf-8 -*-

class Table(object):
    def __init__(self, **kw):
        self._fields = dict((k, v) for k, v in kw.iteritems() if v is not None)

    def __getattr__(self, key, default=None):
        """Maps dict items to attributes"""
        return self._fields.get(key, default)

    def __setattr__(self, key, value):
        """Maps attributes to dict items"""
        d = self._fields
        if key == '_fields':
            object.__setattr__(self, key, value)
        elif value is not None:
            d[key] = value
        elif key in d:
            del d[key]

    def copy(self):
        return type(self)(**self._fields)

    def __repr__(self):
        data = []
        for k,v in self._fields.iteritems():
            data.append("%s = %r" % (k,v))

        data = ', '.join(data)

        return ''.join(("Table(", data, ")"))
