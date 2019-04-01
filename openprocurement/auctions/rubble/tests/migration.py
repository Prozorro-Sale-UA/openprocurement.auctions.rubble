# -*- coding: utf-8 -*-
import unittest

from uuid import uuid4
from copy import deepcopy

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.rubble.migration import (
    RubbleMigrationsRunner,
    RenameDgfIdToLotIdentifierStep,
    MigrateAwardingStep
)
from openprocurement.auctions.core.tests.base import MigrationResourcesDTO_mock
from openprocurement.auctions.rubble.tests.base import BaseWebTest, BaseAuctionWebTest, test_bids, test_auction_data
from openprocurement.auctions.rubble.tests.blanks.migration_blanks import (
    # MigrateTestFrom1To2Bids
    migrate_one_pending,
    migrate_one_active,
    migrate_unsuccessful_active,
    migrate_unsuccessful_pending,
    # MigrateTestFrom1To2WithTwoBids
    migrate_pending_to_unsuccesful,
    migrate_pending_to_complete,
    migrate_active_to_unsuccessful,
    migrate_active_to_complete,
    migrate_cancelled_pending_to_complete,
    migrate_unsuccessful_pending_to_complete,
    migrate_unsuccessful_active_to_complete,
    migrate_cancelled_unsuccessful_pending,
    migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful,
    migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful,
    migrate_awards_number,
    # MigrateTestFrom1To2WithThreeBids
    migrate_unsuccessful_unsuccessful_pending,
    migrate_unsuccessful_unsuccessful_active,
    migrate_dgfId_to_lotIdentefier
)


class MigrateTest(BaseWebTest):

    def setUp(self):
        super(MigrateTest, self).setUp()
        aliases_info_dict = {'openprocurement.auctions.rubble': ('rubbleOther', 'rubbleFinancial')}
        migration_resources = MigrationResourcesDTO_mock(self.db, aliases_info_dict)

        self.runner = RubbleMigrationsRunner(migration_resources)
        self.runner.SCHEMA_VERSION = 1
        self.steps = (MigrateAwardingStep,)
        self.runner.migrate(self.steps)

    def test_migrate(self):
        self.assertEqual(self.runner._get_db_schema_version(), self.runner.SCHEMA_VERSION)
        self.runner.migrate(self.steps)
        self.assertEqual(self.runner._get_db_schema_version(), self.runner.SCHEMA_VERSION)


class MigrateTestFrom1To2Bids(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    test_migrate_one_pending = snitch(migrate_one_pending)
    test_migrate_one_active = snitch(migrate_one_active)
    test_migrate_unsuccessful_active = snitch(migrate_unsuccessful_active)
    test_migrate_unsuccessful_pending = snitch(migrate_unsuccessful_pending)

    def setUp(self):
        super(MigrateTestFrom1To2Bids, self).setUp()
        aliases_info_dict = {'openprocurement.auctions.rubble': ('rubbleOther', 'rubbleFinancial')}
        migration_resources = MigrationResourcesDTO_mock(self.db, aliases_info_dict)

        self.runner = RubbleMigrationsRunner(migration_resources)
        self.runner.SCHEMA_VERSION = 1
        self.steps = (MigrateAwardingStep, )
        self.runner.migrate(self.steps)
        self.runner._set_db_schema_version(0)
        auction = self.db.get(self.auction_id)
        auction['bids'][0]['value']['amount'] = auction['value']['amount']
        self.db.save(auction)


class MigrateTestFrom1To2WithTwoBids(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    test_migrate_pending_to_unsuccesful = snitch(migrate_pending_to_unsuccesful)
    test_migrate_pending_to_complete = snitch(migrate_pending_to_complete)
    test_migrate_active_to_unsuccessful = snitch(migrate_active_to_unsuccessful)
    test_migrate_active_to_complete = snitch(migrate_active_to_complete)
    test_migrate_cancelled_pending_to_complete = snitch(migrate_cancelled_pending_to_complete)
    test_migrate_unsuccessful_pending_to_complete = snitch(migrate_unsuccessful_pending_to_complete)
    test_migrate_unsuccessful_active_to_complete = snitch(migrate_unsuccessful_active_to_complete)
    test_migrate_cancelled_unsuccessful_pending = snitch(migrate_cancelled_unsuccessful_pending)
    test_migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful = snitch(migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful)
    test_migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful = snitch(migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful)
    test_migrate_awards_number = snitch(migrate_awards_number)

    def setUp(self):
        super(MigrateTestFrom1To2WithTwoBids, self).setUp()
        aliases_info_dict = {'openprocurement.auctions.rubble': ('rubbleOther', 'rubbleFinancial')}
        migration_resources = MigrationResourcesDTO_mock(self.db, aliases_info_dict)

        self.runner = RubbleMigrationsRunner(migration_resources)
        self.runner.SCHEMA_VERSION = 1
        self.steps = (MigrateAwardingStep, )
        self.runner.migrate(self.steps)
        self.runner._set_db_schema_version(0)


class MigrateTestFrom1To2WithThreeBids(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    test_migrate_unsuccessful_unsuccessful_pending = snitch(migrate_unsuccessful_unsuccessful_pending)
    test_migrate_unsuccessful_unsuccessful_active = snitch(migrate_unsuccessful_unsuccessful_active)

    def setUp(self):
        super(MigrateTestFrom1To2WithThreeBids, self).setUp()
        aliases_info_dict = {'openprocurement.auctions.rubble': ('rubbleOther', 'rubbleFinancial')}
        migration_resources = MigrationResourcesDTO_mock(self.db, aliases_info_dict)

        self.runner = RubbleMigrationsRunner(migration_resources)
        self.runner.SCHEMA_VERSION = 1
        self.steps = (MigrateAwardingStep,)
        self.runner.migrate(self.steps)
        self.runner._set_db_schema_version(0)
        auction = self.db.get(self.auction_id)
        auction['bids'].append(deepcopy(auction['bids'][0]))
        auction['bids'][-1]['id'] = uuid4().hex
        self.db.save(auction)


class MigrateTestDgfIdToLotIdentifier(BaseAuctionWebTest):
    initial_data = test_auction_data
    test_migrate_dgfId_to_lotIdentefier = snitch(migrate_dgfId_to_lotIdentefier)


    def setUp(self):
        super(MigrateTestDgfIdToLotIdentifier, self).setUp()
        aliases_info_dict = {'openprocurement.auctions.rubble': ('rubbleOther', 'rubbleFinancial')}
        migration_resources = MigrationResourcesDTO_mock(self.db, aliases_info_dict)

        self.runner = RubbleMigrationsRunner(migration_resources)
        self.runner.SCHEMA_VERSION = 1
        self.steps = (RenameDgfIdToLotIdentifierStep, )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTest))
    suite.addTest(unittest.makeSuite(MigrateTestFrom1To2Bids))
    suite.addTest(unittest.makeSuite(MigrateTestFrom1To2WithTwoBids))
    suite.addTest(unittest.makeSuite(MigrateTestFrom1To2WithThreeBids))
    suite.addTest(unittest.makeSuite(MigrateTestDgfIdToLotIdentifier))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')