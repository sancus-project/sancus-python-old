# -*- coding: utf-8 -*-
#
from sancus.exc import HTTPNotFound, HTTPMovedPermanently, HTTPMethodNotAllowed
from sancus.urlparser import TemplateCompiler

import re
import logging

logger = logging.getLogger('sancus.dispatcher')

class WSGIMapper(object):
    compile = TemplateCompiler()

    def __init__(self, handle404 = None, reset = False):
        self.patterns = []
        self.reset_routing_args = reset
        self.handle404 = handle404

    def __call__(self, environ, start_response):
        app = self.find_handler(environ)
        if app:
            logger.info("%s %s (%s?%s) %r", environ["REQUEST_METHOD"],
                    environ["SCRIPT_NAME"], environ["PATH_INFO"],
                    environ["QUERY_STRING"], app[1])

            if 'wsgiorg.routing_args' not in environ:
                environ['wsgiorg.routing_args'] = ((), {})

            environ['wsgiorg.routing_args'][1].update(app[2])

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

    def add_regex(self, expr, handler, factory=True, **kw):
        logger.debug("add_regex(r'%s', %r, %r, %d)" % (expr, handler, factory, len(kw)))
        handler = (factory, handler, kw)
        self.patterns.append((re.compile(expr), handler))

    def add(self, template, handler, **kw):
        logger.debug("add(%r, %r, ...)" % (template, handler))
        expr = self.compile(template)
        return self.add_regex(expr, handler, **kw)

    def redirect(self, template, location, **methods):
        if not methods.has_key('GET'):
            methods['GET'] = True
        if not methods.has_key('HEAD') and methods.has_key('GET') == True:
            methods['HEAD'] = True

        methods = tuple(k for k, v in methods.iteritems() if v is True)
        def redirector(environ, start_response):
            if environ['REQUEST_METHOD'] in methods:
                raise HTTPMovedPermanently(location=location)
            else:
                raise HTTPMethodNotAllowed(allow = methods)

        self.add(template, redirector, factory=False)

    # decorators
    #
    def class_dec_add(self, pattern, **kw):
        def wrap(cls):
            self.add(pattern, cls, **kw)
            return cls
        return wrap

class PathMapper(WSGIMapper):

    def find_handler(self, environ):
        script_name = environ.get('SCRIPT_NAME', '')
        path_info = environ.get('PATH_INFO', '')
        for regex, handler in self.patterns:
            match, pos_args, named_args, matched_path_info, extra_path_info = self.compile.match(regex, path_info)
            if not match:
                # Not a match
                continue
            if extra_path_info and not extra_path_info.startswith('/'):
                # Not a very good match
                continue

            if self.reset_routing_args:
                cur_pos, cur_named = (), {}
            else:
                cur_pos, cur_named = environ.get('wsgiorg.routing_args', ((), {}))

            new_pos = list(cur_pos) + list(pos_args)
            new_named = cur_named.copy()
            new_named.update(named_args)

            environ['wsgiorg.routing_args'] = (new_pos, new_named)
            environ['SCRIPT_NAME'] = script_name + matched_path_info
            environ['PATH_INFO'] = extra_path_info
            return handler

        return None
