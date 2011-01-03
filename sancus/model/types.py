# -*- coding: utf-8 -*-
#

from sqlalchemy.types import TypeDecorator, TypeEngine
from sqlalchemy import Column

import sqlalchemy.dialects.postgresql as pg
import sqlalchemy.types as sa

import uuid

class UUID(TypeDecorator):
    impl = TypeEngine   # placeholder

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            t = pg.UUID()
        else:
            t = sa.BLOB(16)

        return dialect.type_descriptor(t)

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        elif isinstance(value,uuid.UUID):
            if dialect.name == 'postgresql':
                return value.hex
            else:
                return value.bytes
        else:
            raise ValueError, "value %s is not a valid UUID" % value

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
