from webob import Request, Response
from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed, HTTPMovedPermanently

class BaseResource(Response):
    __methods__ = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    HTTPMovedPermanently = HTTPMovedPermanently
    HTTPNotFound = HTTPNotFound

    def HTTPMethodNotAllowed(self, *d, **kw):
        return HTTPMethodNotAllowed(allow = self.allowed_methods(), *d, **kw)

    def allowed_methods(self):
        try:
            return type(self).__allowed_methods__
        except:
            l = []

        for method in self.__methods__:
            # no 'HEAD' if not 'GET'
            if method == 'HEAD' and 'GET' not in l:
                continue
            # self.FOO must exist and be callable
            if callable(getattr(self, method, None)):
                l.append(method)

        type(self).__allowed_methods__ = l
        return l

    def HEAD(self, req):
        self.GET(req)

    def __init__(self, environ, *d, **kw):
        method = environ['REQUEST_METHOD']
        if method not in self.allowed_methods():
            raise self.HTTPMethodNotAllowed()

        h = getattr(self, method)

        Response.__init__(self, *d, **kw)
        self.allow = self.allowed_methods()

        h(Request(environ))

class Resource(BaseResource):
    def __init__(self, environ, *d, **kw):
        path_info = environ['PATH_INFO']

        if len(path_info) == 0:
            # move on
            return BaseResource.__init__(self, environ, *d, **kw)
        elif path_info == '/' and environ['REQUEST_METHOD'] in ('HEAD','GET'):
            # remove trailing slash for GETs
            h = self.HTTPMovedPermanently(location = environ['SCRIPT_NAME'])
            qs = environ['QUERY_STRING']
            if len(qs) > 0:
                h.location += "?" + qs
            raise h
        else:
            # don't accept PATH_INFO in leaves
            raise self.HTTPNotFound()
