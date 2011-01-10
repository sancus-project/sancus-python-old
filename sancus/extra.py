# -*- coding: utf-8 -*-

class Table(dict):
    def __getattr__(self, key, default=None):
        """Maps dict items to attributes"""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __setattr__(self, key, value):
        """Maps attributes to dict items"""
        self.__setitem__(key, value)
