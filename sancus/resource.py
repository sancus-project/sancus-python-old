from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed

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
