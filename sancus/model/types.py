# -*- coding: utf-8 -*-
#

from sqlalchemy.types import TypeDecorator, TypeEngine
from sqlalchemy import Column

import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa

import uuid
import string

if sa.__version__ == '0.7.1':
    # 0.7.1 doesn't like TypeEngine as impl
    TypeEngine = sa.String

class SafeFilename(TypeDecorator):
    impl = sa.Unicode
    _valid_chars = string.ascii_lowercase + string.digits + "._-"
    _white = '_'

    def process_bind_param(self, value, dialect):
        if value is not None:
            s = value.lower()
            s = ''.join(c if c in type(self)._valid_chars else type(self)._white for c in s).strip(type(self)._white)
            if len(s) > 0:
                return s
        return None

class BLOB(TypeDecorator):
    impl = TypeEngine

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            t = pg.BYTEA
        else:
            t = sa.BLOB

        return dialect.type_descriptor(t)

class UUID(TypeDecorator):
    impl = TypeEngine

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            t = pg.UUID()
        else:
            t = sa.BLOB(16)

        return dialect.type_descriptor(t)

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        elif not isinstance(value,uuid.UUID):
            value = uuid.UUID(value)

        if dialect.name == 'postgresql':
            return value.hex
        else:
            return value.bytes

    def process_result_value(self, value, dialect):
        if not value:
            return None
        elif len(value) == 16:
            return uuid.UUID(bytes=value)
        else:
            return uuid.UUID(value)

    def is_mutable(self):
        return False


def UUID_PK_Column(name=None, node=None, clock_seq=None):
    # sqlalchemy passes self to the default function, so we need
    # a wrapper to protect it, and we take the chance to allow arguments
    def UUID1_Generator(self):
        return uuid.uuid1(node, clock_seq)

    if name:
        return Column(name, UUID(), primary_key=True, default=UUID1_Generator)
    else:
        return Column(UUID(), primary_key=True, default=UUID1_Generator)
