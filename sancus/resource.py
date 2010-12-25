from sancus.exc import HTTPNotFound, HTTPMethodNotAllowed, HTTPMovedPermanently

class WSGIHeadify(object):
    def __init__(self, app):
        self.app = app

    def start_response(self, status, response_headers, exc_info=None):
        self.status = status
        self.headers = response_headers
        self.exc_info = exc_info

    def __call__(self, environ, start_response):
        has_length = False

        environ['REQUEST_METHOD'] = 'GET'
        try:
            app_iter = self.app(environ, self.start_response)
        except:
            environ['REQUEST_METHOD'] = 'HEAD'
            raise

        for k,v in self.headers:
            if k.lower() == 'content-length':
                has_length = True
                break

        if not has_length:
            body = ''.join(app_iter)
            body_len = str(len(body))
            self.headers.append(('Content-Length', body_len))

        environ['REQUEST_METHOD'] = 'HEAD'
        start_response(self.status, self.headers)
        return []

class WSGIResource(object):
    handle404 = HTTPNotFound()
    handle405 = HTTPMethodNotAllowed()

    __methods__ = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    def __method_handler(self, method):
        if method in self.__methods__:
            if hasattr(self, method):
                h = getattr(self, method)
                if callable(h):
                    return h
        return None

    def HEAD(self, environ, start_response):
        h = self.__method_handler('GET')
        if h:
            h = WSGIHeadify(h)
            return h(environ, start_response)

        raise self.handle405

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
        elif path_info == '/' and environ['REQUEST_METHOD'] in ('HEAD','GET'):
            # remove trailing slash for GETs
            h = HTTPMovedPermanently(location = environ['SCRIPT_NAME'])
            qs = environ['QUERY_STRING']
            if len(qs) > 0:
                h.location += "?" + qs
            raise h
        else:
            # don't accept PATH_INFO in leaves
            raise self.handle404
