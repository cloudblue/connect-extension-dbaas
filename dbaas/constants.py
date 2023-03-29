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


class ContextCallTypes:
    ADMIN = 'admin'
    USER = 'user'


class DBAction:
    CREATE = 'create'
    DELETE = 'delete'
    UPDATE = 'update'


DB_HELPDESK_CASE_SUBJECT_TPL = 'Infra {db_id} {action} {db_name}'
DB_HELPDESK_CASE_DESCRIPTION_TPL = """
ID: {db_id}
Name: {db_name}
Action: {action}
Workload: {db_workload}
Region: {region_id}
Contact: {contact_id}

{description}
"""
