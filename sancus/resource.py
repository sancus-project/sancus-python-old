from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed, HTTPMovedPermanently

class WSGIResource(object):
    handle404 = HTTPNotFound()
    handle405 = HTTPMethodNotAllowed()

    __methods__ = ('GET', 'POST', 'PUT', 'DELETE')

    def __method_handler(self, method):
        if method in self.__methods__:
            if hasattr(self, method):
                h = getattr(self, method)
                if callable(h):
                    return h
        return None

    def __call__(self, environ, start_response):
        h = self.__method_handler(environ['REQUEST_METHOD'])
        if h:
            return h(environ, start_response)

        raise self.handle405

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
            raise h
        else:
            # don't accept PATH_INFO in leaves
            raise self.handle404
