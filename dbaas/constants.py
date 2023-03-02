class DBWorkload:
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    @classmethod
    def all(cls):
        return cls.SMALL, cls.MEDIUM, cls.LARGE


class DBStatus:
    REVIEWING = 'reviewing'
    ACTIVE = 'active'
    RECONFIGURING = 'reconfiguring'
    DELETED = 'deleted'
