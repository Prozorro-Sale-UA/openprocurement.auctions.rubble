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
SCHEMA_VERSION = 2
SCHEMA_DOC = 'openprocurement_auctions_dgf_schema'


class RubbleMigrationsRunner(BaseMigrationsRunner):

    SCHEMA_VERSION = SCHEMA_VERSION
    SCHEMA_DOC = SCHEMA_DOC


class RenameDgfIdToLotIdentifierStep(BaseMigrationStep):

    def setUp(self):
        self.view = 'auctions/all'

    def _skip_predicate(self, auction):
        """
        If return True than migration for such auction should be skipped, otherwise migrate it
        :param auction:
        :return: True or False
        """
        is_dgf_id_is_absent = bool('dgfID' not in auction)
        target_pmts = self.resources.aliases_info.get_package_aliases('openprocurement.auctions.rubble')
        pmt_is_suitable = auction['procurementMethodType'] in target_pmts

        if is_dgf_id_is_absent or not pmt_is_suitable:
            return True

        return False

    def migrate_document(self, auction):
        """
        Rename dgfID field to lotIdentifier in rubbleOther and rubbleFinancial models
        :param auction:
        :return: auction if updated else None
        """
        if self._skip_predicate(auction):
            return None

        auction['lotIdentifier'] = auction.pop('dgfID')
        return auction


class MigrateAwardingStep(BaseMigrationStep):

    def setUp(self):
        self.view = 'auctions/all'
        self.procurement_method_types = ['rubbleOther', 'rubbleFinancial']

    def _skip_predicate(self, auction):
        """
        If return True than migration for such auction should be skipped, otherwise migrate it
        :param auction:
        :return: True or False
        """
        target_pmts = self.resources.aliases_info.get_package_aliases('openprocurement.auctions.rubble')
        pmt_is_suitable = auction['procurementMethodType'] in target_pmts

        if not pmt_is_suitable:
            return True

        return False

    def migrate_document(self, auction):
        if self._skip_predicate(auction):
            return None

        migrate_awarding_1_0_to_awarding_2_1(auction, self.procurement_method_types)
        auction = Auction(auction)
        auction = auction.to_primitive()
        return auction


MIGRATION_STEPS = (MigrateAwardingStep, RenameDgfIdToLotIdentifierStep)


def migrate(db):
    runner = RubbleMigrationsRunner(db)
    runner.migrate(MIGRATION_STEPS)
