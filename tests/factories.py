# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from datetime import datetime

import factory

from dbaas.constants import DBStatus, DBWorkload


class RegionFactory(factory.DictFactory):
    id = factory.Iterator(['eu-west', 'us-central'])
    name = factory.Iterator(['Hell', 'Heaven'])


class CaseFactory(factory.DictFactory):
    id = factory.Sequence(lambda n: f'CS-{n:05}')


class UserFactory(factory.DictFactory):
    id = factory.Sequence(lambda n: f'UR-{n:05}')
    name = factory.Faker('name')
    email = factory.Faker('email')
    active = True


class DBFactory(factory.DictFactory):
    id = factory.Sequence(lambda n: f'DB-{n:05}')
    name = factory.Faker('name')
    description = factory.Faker('text', max_nb_chars=200)
    workload = factory.Iterator(DBWorkload.all())
    status = DBStatus.RECONFIGURING

    region = factory.SubFactory(RegionFactory)
    tech_contact = factory.SubFactory(UserFactory)
    cases = factory.List([])

    credentials = factory.Dict({
        'host': factory.Faker('hostname'),
        'username': factory.Faker('user_name'),
        'password': factory.Faker('password'),
    })

    events = factory.Dict({
        'created': factory.Dict({
            'at': factory.LazyFunction(datetime.now),
            'by': factory.SubFactory(UserFactory),
        }),
    })

    account_id = factory.Sequence(lambda n: f'VA-{n:05}')

    @factory.post_generation
    def owner(obj, *a, **kw):
        obj['owner'] = {'id': obj['account_id']}


class InstallationFactory(factory.DictFactory):
    id = factory.Sequence(lambda n: f'EIN-{n:05}')

    environment = factory.Dict({
        'extension': factory.Dict({
            'owner': factory.Dict({
                'id': factory.Sequence(lambda n: f'PA-{n:05}'),
            }),
        }),
    })
