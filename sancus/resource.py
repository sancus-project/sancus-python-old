# -*- coding: utf-8 -*-
from webob import Request, Response
from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed, HTTPMovedPermanently, HTTPInternalServerError

class BaseResource(Response):
    __methods = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    __param_arg = 'param'

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

    # placeholders
    #
    def HEAD(self, req, *d, **kw):
        return self.GET(req, *d, **kw)

    def __before__(self, req):
        pass

    def __after__(self, req):
        pass

    # meta functions
    #
    def __init__(self, environ, *d, **kw):
        method = environ['REQUEST_METHOD']
        if method not in self.supported_methods():
            raise HTTPMethodNotAllowed(allow = self.supported_methods())

        pos_args, named_args = environ['wsgiorg.routing_args']
        # remove keys with value None
        named_args = dict((k, v) for k, v in named_args.iteritems() if v is not None)

        param = named_args.get(self.__param_arg, None)
        if param is None:
            handler_name = method
        else:
            del named_args[self.__param_arg]

            handler_name = "%s_%s" % (method, param)
            if method == 'HEAD':
                if not hasattr(self, handler_name):
                    handler_name = "GET_%s" % param

        h = getattr(self, handler_name, None)
        if not h:
            ret = 404
        else:
            req = Request(environ)

            Response.__init__(self, *d, request=req, **kw)
            self.allow = self.supported_methods()

            ret = self.__before__(req)
            if ret is None:
                try:
                    ret = h(req, **named_args)
                except:
                    self.__after__(req)
                    raise

                self.__after__(req)

        if ret is None:
            pass
        elif ret == 404:
            raise HTTPNotFound()
        else:
            raise HTTPInternalServerError("%d returned from handler not supported" % ret)

class Resource(BaseResource):
    def __init__(self, environ, *d, **kw):
        path_info = environ['PATH_INFO']

        if len(path_info) == 0:
            # move on
            return BaseResource.__init__(self, environ, *d, **kw)
        elif path_info == '/' and environ['REQUEST_METHOD'] in ('HEAD','GET'):
            # remove trailing slash for GETs
            h = HTTPMovedPermanently(location = environ['SCRIPT_NAME'])
            qs = environ['QUERY_STRING']
            if len(qs) > 0:
                h.location += "?" + qs
            raise h
        else:
            # don't accept PATH_INFO in leaves
            return 404
