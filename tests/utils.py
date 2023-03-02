from unittest.mock import ANY

from connect.eaas.core.inject.models import Context


class _ANYContext(ANY.__class__):
    def __eq__(self, other):
        return isinstance(other, Context)


ANYContext = _ANYContext()
