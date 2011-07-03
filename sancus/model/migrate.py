# -*- coding: utf-8 -*-
#

def migrate(engine, meta, repo):
    meta.create_all(bind=engine)
