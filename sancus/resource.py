from webob import Request, Response
from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed, HTTPMovedPermanently

class BaseResource(Response):
    __methods = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    __param_arg = 'param'

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

        pos_args, named_args = environ['wsgiorg.routing_args']
        # remove keys with value None
        named_args = dict((k, v) for k, v in named_args.iteritems() if v is not None)

        param = named_args.get(self.__param_arg, None)
        if param is None:
            handler_name = method
        else:
            del named_args[self.__param_arg]
            handler_name = "%s_%s" % (method, param)

        h = getattr(self, handler_name, None)
        if not h:
            raise self.HTTPNotFound()

        Response.__init__(self, *d, **kw)
        self.allow = self.supported_methods()

        req = Request(environ)
        h(req, **named_args)

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
