# -*- coding: utf-8 -*-
#
from __future__ import absolute_import

from migrate.versioning import api as v
from migrate.exceptions import InvalidRepositoryError

from os.path import abspath, join

def migrate(engine, meta, repo):
    if not isinstance(repo, basestring):
        repo = abspath(join(*repo))

    try:
        repo_version = v.version(repo)
    except InvalidRepositoryError:
        v.create(repo, 'magic_migrate')
        v.manage(join(repo, 'manage.py'),
                url=str(engine.url),
                repository=repo)
        repo_version = -1

    meta.create_all(bind=engine)
