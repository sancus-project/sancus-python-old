import pyramid.httpexceptions as exc

from sancus.resource import key_to_int, key_in_enum

class Resource(object):
    def supported_methods(self):
        try:
            return type(self)._supported_methods
        except:
            l = []

        for method in ('GET', 'HEAD', 'POST', 'PUT', 'DELETE'):
            # no 'HEAD' if not 'GET'
            if method == 'HEAD' and 'GET' not in l:
                continue

            # self.FOO must exist and be callable
            if callable(getattr(self, method, None)):
                l.append(method)

        l = tuple(l)
        type(self)._supported_methods = l
        return l

    def __init__(self, req):
        environ = req.environ
        method = environ['REQUEST_METHOD']
        
        if method not in self.supported_methods():
            raise exc.HTTPMethodNotAllowed(allow = self.supported_methods())

        named_args = dict((k, v) for k, v in req.matchdict.iteritems() if v is not None)

        handler_name = method
        h = getattr(self, handler_name, None)

        environ['sancus.handler_name'] = handler_name
        environ['sancus.handler'] = h
        environ['sancus.args'] = named_args

        self.request = req

    def __call__(self):
        h = self.request.environ['sancus.handler']
        kw = self.request.environ['sancus.args']
        return h(**kw)

    # placeholders
    def HEAD(self, *d, **kw):
        return self.GET(*d, **kw)
