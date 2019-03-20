# -*- coding: utf-8 -*-
import logging

from openprocurement.auctions.core.plugins.awarding.v2_1.migration import (
    migrate_awarding_1_0_to_awarding_2_1
)

from openprocurement.api.migration import (
    BaseMigrationsRunner,
    BaseMigrationStep,
)

from openprocurement.auctions.rubble.models import Auction


LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = 1
SCHEMA_DOC = 'openprocurement_auctions_dgf_schema'


class RubbleMigrationsRunner(BaseMigrationsRunner):

    SCHEMA_VERSION = SCHEMA_VERSION
    SCHEMA_DOC = SCHEMA_DOC


class RenameDgfIdToLotIdentifierStep(BaseMigrationStep):

    def setUp(self):
        self.view = 'auctions/all'
        self.procurement_method_types = ['rubbleOther', 'rubbleFinancial']

    def migrate_document(self, auction):
        """
        Rename dgfID field to lotIdentifier in rubbleOther and rubbleFinancial models
        :param auction:
        :return: auction if updated else None
        """
        if auction['procurementMethodType'] in self.procurement_method_types:
            if auction.get('dgfID'):
                auction['lotIdentifier'] = auction.pop('dgfID')
                return auction
        return None


class MigrateAwardingStep(BaseMigrationStep):

    def setUp(self):
        self.view = 'auctions/all'
        self.procurement_method_types = ['rubbleOther', 'rubbleFinancial']

    def migrate_document(self, auction):
        if auction['procurementMethodType'] in self.procurement_method_types:
            migrate_awarding_1_0_to_awarding_2_1(auction, self.procurement_method_types)
            auction = Auction(auction)
            auction = auction.to_primitive()
            return auction
        return None


MIGRATION_STEPS = (MigrateAwardingStep, RenameDgfIdToLotIdentifierStep)


def migrate(db):
    runner = RubbleMigrationsRunner(db)
    runner.migrate(MIGRATION_STEPS)
