# -*- coding: utf-8 -*-
#

from sqlalchemy.types import TypeDecorator, BLOB
from sqlalchemy import Column

import uuid

class UUID(TypeDecorator):
    impl = BLOB

    def __init__(self):
        self.impl.length = 16
        TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        elif isinstance(value,uuid.UUID):
            return value.bytes
        else:
            raise ValueError, "value %s is not a valid UUID" % value

    def process_result_value(self, value, dialect):
        if value:
            return uuid.UUID(bytes=value)
        else:
            return None

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
