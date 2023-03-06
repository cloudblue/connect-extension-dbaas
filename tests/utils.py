# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from unittest.mock import ANY

from connect.eaas.core.inject.models import Context


class _ANYContext(ANY.__class__):
    def __eq__(self, other):
        return isinstance(other, Context)


ANYContext = _ANYContext()
