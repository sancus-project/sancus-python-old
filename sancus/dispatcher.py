# -*- coding: utf-8 -*-
#
from sancus.exc import HTTPNotFound
import re

class WSGIMapper(object):
    def __init__(self, handle404 = None, reset = False):
        self.patterns = []
        self.reset_routing_args = reset
        self.handle404 = handle404

    def __call__(self, environ, start_response):
        app = self.find_handler(environ)
        if app:
            if app[0]:
                # factory
                app = app[1](environ)
            else:
                # direct
                app = app[1]

            return app(environ, start_response)
        elif self.handle404:
            return self.handle404(environ, start_response)
        else:
            raise HTTPNotFound()

    def find_handler(self, environ):
        raise NotImplementedError("weak method")

    def add_regex(self, expr, handler, factory=True):
        handler = (factory, handler)
        self.patterns.append((re.compile(expr), handler))

    # decorators
    #
    def class_dec_add(self, pattern):
        def wrap(cls):
            self.add_regex(pattern, cls)
            return cls
        return wrap

class PathMapper(WSGIMapper):

    def find_handler(self, environ):
        # based on the code at http://wsgi.org/wsgi/Specifications/routing_args
        #
        script_name = environ.get('SCRIPT_NAME', '')
        path_info = environ.get('PATH_INFO', '')
        for regex, handler in self.patterns:
            match = regex.match(path_info)
            if not match:
                continue

            extra_path_info = path_info[match.end():]
            if extra_path_info and not extra_path_info.startswith('/'):
                # Not a very good match
                continue

            if self.reset_routing_args:
                cur_pos, cur_named = (), {}
            else:
                cur_pos, cur_named = environ.get('wsgiorg.routing_args', ((), {}))

            pos_args = match.groups()
            named_args = match.groupdict()

            new_pos = list(cur_pos) + list(pos_args)
            new_named = cur_named.copy()
            new_named.update(named_args)
            environ['wsgiorg.routing_args'] = (new_pos, new_named)
            environ['SCRIPT_NAME'] = script_name + path_info[:match.end()]
            environ['PATH_INFO'] = extra_path_info
            return handler

        return None
