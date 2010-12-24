from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed, HTTPMovedPermanently

class WSGIResource(object):
    handle404 = HTTPNotFound()
    handle405 = HTTPMethodNotAllowed()

    __methods__ = ('GET', 'POST', 'PUT', 'DELETE')

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        handler = self.handle405

        if method in self.__methods__:
            if hasattr(self, method):
                h = getattr(self, method)
                if callable(h):
                    handler = h

        return handler(environ, start_response)

class WSGILeafResource(WSGIResource):
    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']

        if len(path_info) == 0:
            # move on
            return WSGIResource.__call__(self, environ, start_response)
        elif path_info == '/' and environ['REQUEST_METHOD'] == 'GET':
            # remove trailing slash for GETs
            h = HTTPMovedPermanently(location = environ['SCRIPT_NAME'])
            qs = environ['QUERY_STRING']
            if len(qs) > 0:
                h.location += "?" + qs
            return h(environ, start_response)
        else:
            # don't accept PATH_INFO in leaves
            return self.handle404(environ, start_response)
