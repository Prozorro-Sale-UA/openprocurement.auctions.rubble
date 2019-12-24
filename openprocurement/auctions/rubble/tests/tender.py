# -*- coding: utf-8 -*-
import unittest
# from calendar import monthrange
# from copy import deepcopy
# from datetime import datetime, timedelta, time, date
# from uuid import uuid4
# from iso8601 import parse_date
# import pytz

from openprocurement.auctions.rubble.models import (
    RubbleOther,
    RubbleFinancial,
)
from openprocurement.auctions.rubble.tests.base import (
    test_auction_maximum_data,
    test_auction_data,
    test_financial_auction_data,
    test_organization,
    test_financial_organization,
    BaseWebTest,
    BaseAuctionWebTest,
    test_bids,
    test_financial_bids
)

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.tender import (
    ExtractCredentialsMixin
)
from openprocurement.auctions.core.tests.blanks.tender_blanks import (
    simple_add_auction
)
from openprocurement.auctions.core.tests.blanks.tender_blanks import (
    # AuctionResourceTest
    auction_features_invalid,
    auction_features,
    patch_tender_jsonpatch,
    dateModified_auction,
    guarantee,
    empty_listing,
    listing,
    listing_changes,
    listing_draft,
    create_auction_draft,
    get_auction,
    auction_not_found,
    invalid_auction_conditions
)
from openprocurement.auctions.rubble.tests.blanks.tender_blanks import (
    # AuctionTest
    create_role,
    edit_role,
    # AuctionResourceTest
    create_auction_validation_accelerated,
    create_auction_invalid,
    required_dgf_id,
    required_dgf_item_address,
    create_auction_auctionPeriod,
    create_auction_rectificationPeriod_generated,
    create_auction_rectificationPeriod_set,
    create_auction_generated,
    create_auction,
    create_auction_tender_attempts,
    create_auction_with_item_with_schema_properties,
    create_auction_with_item_with_invalid_schema_properties,
    additionalClassifications,
    cavps_cpvs_classifications,
    patch_auction,
    patch_auction_rectificationPeriod_invalidationDate,
    patch_old_auction_rectificationPeriod_invalidationDate,
    delete_procurementMethodDetails,
    auction_Administrator_change,
    # AuctionFieldsEditingTest
    patch_auction_denied,
    patch_auction_during_rectification_period,
    invalidate_bids_auction_unsuccessful,
    # AuctionProcessTest
    one_valid_bid_auction,
    one_invalid_bid_auction,
    first_bid_auction,
)


class AuctionTest(BaseWebTest):
    auction = RubbleOther
    initial_data = test_auction_data
    test_simple_add_auction = snitch(simple_add_auction)
    test_create_role = snitch(create_role)
    test_edit_role = snitch(edit_role)


class AuctionResourceTest(BaseWebTest):
    initial_data = test_auction_data
    initial_organization = test_organization
    initial_status = 'active.tendering'

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_auction_draft = snitch(create_auction_draft)
    test_get_auction = snitch(get_auction)
    test_auction_not_found = snitch(auction_not_found)
    test_create_auction_validation_accelerated = snitch(create_auction_validation_accelerated)
    test_create_auction_invalid = snitch(create_auction_invalid)
    test_required_dgf_id = snitch(required_dgf_id)
    test_required_dgf_item_address = snitch(required_dgf_item_address)
    test_create_auction_auctionPeriod = snitch(create_auction_auctionPeriod)
    test_create_auction_rectificationPeriod_generated = snitch(create_auction_rectificationPeriod_generated)
    test_create_auction_rectificationPeriod_set = snitch(create_auction_rectificationPeriod_set)
    test_create_auction_generated = snitch(create_auction_generated)
    test_create_auction = snitch(create_auction)
    test_create_auction_tender_attempts = snitch(create_auction_tender_attempts)
    test_create_auction_with_item_with_schema_properties = snitch(create_auction_with_item_with_schema_properties)
    test_create_auction_with_item_with_invalid_schema_properties = snitch(create_auction_with_item_with_invalid_schema_properties)
    test_additionalClassifications = snitch(additionalClassifications)
    test_cavps_cpvs_classifications = snitch(cavps_cpvs_classifications)
    test_auction_features_invalid = snitch(unittest.skip("option not available")(auction_features_invalid))
    test_auction_features = snitch(unittest.skip("option not available")(auction_features))
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_auction = snitch(patch_auction)
    test_patch_auction_rectificationPeriod_invalidationDate = snitch(patch_auction_rectificationPeriod_invalidationDate)
    test_patch_old_auction_rectificationPeriod_invalidationDate = snitch(patch_old_auction_rectificationPeriod_invalidationDate)
    test_dateModified_auction = snitch(dateModified_auction)
    test_guarantee = snitch(guarantee)
    test_auction_Administrator_change = snitch(auction_Administrator_change)
    test_delete_procurementMethodDetails = snitch(delete_procurementMethodDetails)


class AuctionFieldsEditingTest(BaseAuctionWebTest):
    initial_data = test_auction_data
    initial_maximum_data = test_auction_maximum_data
    initial_organization = test_organization
    initial_bids = test_bids
    patch_auction_denied = snitch(patch_auction_denied)
    patch_auction_during_rectification_period = snitch(patch_auction_during_rectification_period)
    invalidate_bids_auction_unsuccessful = snitch(invalidate_bids_auction_unsuccessful)


class AuctionProcessTest(BaseAuctionWebTest):
    test_invalid_auction_conditions = snitch(unittest.skip("option not available")(invalid_auction_conditions))
    test_one_valid_bid_auction = snitch(one_valid_bid_auction)
    test_one_invalid_bid_auction = snitch(one_invalid_bid_auction)
    test_first_bid_auction = snitch(first_bid_auction)

    # setUp = BaseWebTest.setUp
    def setUp(self):
        super(AuctionProcessTest.__bases__[0], self).setUp()


class FinancialAuctionTest(AuctionTest):
    auction = RubbleFinancial


class FinancialAuctionFieldsEditingTest(AuctionFieldsEditingTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization
    initial_bids = test_financial_bids


class FinancialAuctionResourceTest(AuctionResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization

    def test_create_auction_generated(self):
        data = self.initial_data.copy()
        # del data['awardPeriod']
        data.update({'id': 'hash', 'doc_id': 'hash2', 'auctionID': 'hash3'})
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        if 'procurementMethodDetails' in auction:
            auction.pop('procurementMethodDetails')
        self.assertEqual(set(auction), set([
            u'procurementMethodType', u'id', u'date', u'dateModified', u'auctionID', u'status', u'enquiryPeriod',
            u'tenderPeriod', u'minimalStep', u'items', u'value', u'procuringEntity', u'next_check', u'dgfID',
            u'procurementMethod', u'awardCriteria', u'submissionMethod', u'title', u'owner', u'auctionPeriod',
            u'eligibilityCriteria', u'eligibilityCriteria_en', u'eligibilityCriteria_ru', u'tenderAttempts',
            u'rectificationPeriod'
        ]))
        self.assertNotEqual(data['id'], auction['id'])
        self.assertNotEqual(data['doc_id'], auction['id'])
        self.assertNotEqual(data['auctionID'], auction['auctionID'])

        self.assertEqual(auction['eligibilityCriteria'], u"До участі допускаються лише ліцензовані фінансові установи.")
        self.assertEqual(auction['eligibilityCriteria_en'], u"Only licensed financial institutions are eligible to participate.")
        self.assertEqual(auction['eligibilityCriteria_ru'], u"К участию допускаются только лицензированные финансовые учреждения.")


class FinancialAuctionProcessTest(AuctionProcessTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class AuctionExtractCredentialsTest(BaseAuctionWebTest, ExtractCredentialsMixin):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionProcessTest))
    suite.addTest(unittest.makeSuite(AuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionFieldsEditingTest))
    suite.addTest(unittest.makeSuite(AuctionTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionProcessTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionFieldsEditingTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionTest))
    suite.addTest(unittest.makeSuite(AuctionExtractCredentialsTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
