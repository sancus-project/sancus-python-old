from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed

class WSGIResource(object):
    handle404 = HTTPNotFound()
    handle405 = HTTPMethodNotAllowed()

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        if method[0] != '_' and hasattr(self, method):
            handler = getattr(self, method)
        else:
            handler = self.handle405
        return handler(environ, start_response)
