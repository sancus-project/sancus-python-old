from webob import Request, Response
from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed, HTTPMovedPermanently

class BaseResource(Response):
    __methods = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    HTTPMovedPermanently = HTTPMovedPermanently
    HTTPNotFound = HTTPNotFound

    def HTTPMethodNotAllowed(self, *d, **kw):
        return HTTPMethodNotAllowed(allow = self.supported_methods(), *d, **kw)

    def supported_methods(self):
        try:
            return type(self).__supported_methods
        except:
            l = []

        for method in self.__methods:
            # no 'HEAD' if not 'GET'
            if method == 'HEAD' and 'GET' not in l:
                continue
            # self.FOO must exist and be callable
            if callable(getattr(self, method, None)):
                l.append(method)

        type(self).__supported_methods = l
        return l

    def HEAD(self, req, *d, **kw):
        self.GET(req, *d, **kw)

    def __init__(self, environ, *d, **kw):
        method = environ['REQUEST_METHOD']
        if method not in self.supported_methods():
            raise self.HTTPMethodNotAllowed()

        Response.__init__(self, *d, **kw)
        self.allow = self.supported_methods()

        h = getattr(self, method)
        req = Request(environ)

        pos_params, named_params = environ['wsgiorg.routing_args']
        # remove keys with value None
        named_params = dict((k, v) for k, v in named_params.iteritems() if v is not None)

        h(req, **named_params)

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
