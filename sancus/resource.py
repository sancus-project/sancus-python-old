# -*- coding: utf-8 -*-
from webob import Request, Response
from urllib import quote_plus, unquote_plus

import sancus.exc as exc

import logging

_log = logging.getLogger(__name__)

class BaseResource(Response):
    _methods = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    __param_arg__ = 'param'

    def supported_methods(self):
        try:
            return type(self)._supported_methods
        except:
            l = []

        for method in self._methods:
            # no 'HEAD' if not 'GET'
            if method == 'HEAD' and 'GET' not in l:
                continue
            # self.FOO must exist and be callable
            if callable(getattr(self, method, None)):
                l.append(method)

        type(self)._supported_methods = l
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
            raise exc.HTTPMethodNotAllowed(allow = self.supported_methods())

        pos_args, named_args = environ['wsgiorg.routing_args']
        # remove keys with value None
        named_args = dict((k, v) for k, v in named_args.iteritems() if v is not None)

        param = named_args.get(self.__param_arg__, None)
        if param is None:
            handler_name = method
        else:
            del named_args[self.__param_arg__]

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
            raise exc.HTTPNotFound()
        elif ret == 405:
            raise exc.HTTPMethodNotAllowed(allow = self.supported_methods())
        elif ret == 400:
            raise exc.HTTPBadRequest()
        elif ret == 503:
            raise exc.HTTPServiceUnavailable()
        else:
            _log.warn("%r returned %r" % ret)
            raise exc.HTTPInternalServerError("%d returned from handler not supported" % ret)

class Resource(BaseResource):
    def __init__(self, environ, *d, **kw):
        path_info = environ['PATH_INFO']

        if len(path_info) == 0:
            # move on
            return BaseResource.__init__(self, environ, *d, **kw)
        elif path_info == '/' and environ['REQUEST_METHOD'] in ('HEAD','GET'):
            # remove trailing slash for GETs
            h = exc.HTTPMovedPermanently(location = environ['SCRIPT_NAME'])
            qs = environ['QUERY_STRING']
            if len(qs) > 0:
                h.location += "?" + qs
            raise h
        else:
            # don't accept PATH_INFO in leaves
            return 404

def unicode_to_url(s):
    return quote_plus(s.encode('utf-8'))

def url_to_unicode(s):
    return unicode(unquote_plus(s), 'utf-8')
