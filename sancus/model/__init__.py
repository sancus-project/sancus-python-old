# -*- coding: utf-8 -*-
#

from sqlalchemy import create_engine as __create_engine

def create_engine(engine, **kw):
    # file?
    try:
        f = open(engine, mode='r')
        engine = f.readline()
        if len(engine) > 0 and engine[-1] == '\n':
            engine = engine[:-1]
        f.close()
    except IOError:
        pass

    return __create_engine(engine, **kw)
