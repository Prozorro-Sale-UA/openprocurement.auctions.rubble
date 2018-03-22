# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest,
    test_auction_data,
    test_features_auction_data,
    test_financial_organization,
    test_financial_auction_data,
    test_bids,
    test_financial_bids,
    test_organization
)

from openprocurement.auctions.dgf.tests.blanks.bidder_blanks import (
    # AuctionBidderResourceTest
    create_auction_bidder_invalid,
    patch_auction_bidder,
    get_auction_bidder,
    delete_auction_bidder,
    get_auction_auctioners,
    bid_Administrator_change,
    # AuctionBidInvalidationAuctionResourceTest
    post_auction_all_invalid_bids,
    post_auction_one_invalid_bid,
    post_auction_one_valid_bid,
    # AuctionBidderProcessTest
    reactivate_invalidated_bids,
    # AuctionBidderFeaturesResourceTest
    features_bidder,
    # AuctionBidderDocumentResourceTest
    create_auction_bidder_document_nopending
)
from openprocurement.auctions.core.tests.blanks.bidder_blanks import (
    # AuctionBidderResourceTest
    create_auction_bidder,
    # AuctionBidderFeaturesResourceTest
    features_bidder_invalid
)
from openprocurement.auctions.core.tests.bidder import (
    AuctionBidderDocumentResourceTestMixin,
    AuctionBidderDocumentWithDSResourceTestMixin
)
from openprocurement.auctions.core.tests.base import snitch


class AuctionBidderResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'
    test_financial_organization = test_financial_organization

    test_create_auction_bidded = snitch(create_auction_bidder)
    test_create_auction_bidder_invalid = snitch(create_auction_bidder_invalid)
    test_patch_auction_bidder = snitch(patch_auction_bidder)
    test_get_auction_bidder = snitch(get_auction_bidder)
    test_delete_auction_bidder = snitch(delete_auction_bidder)
    test_get_auction_auctioners = snitch(get_auction_auctioners)
    test_bid_Administrator_change = snitch(bid_Administrator_change)


class AuctionBidInvalidationAuctionResourceTest(BaseAuctionWebTest):
    initial_data = test_auction_data
    initial_status = 'active.auction'
    initial_bids = [
        {
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": (initial_data['value']['amount'] + initial_data['minimalStep']['amount']/2),
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'qualified': True
        }
        for i in range(3)
    ]
    test_post_auction_all_invalid_bids = snitch(post_auction_all_invalid_bids)
    test_post_auction_one_invalid_bid = snitch(post_auction_one_invalid_bid)
    test_post_auction_one_valid_bid = snitch(post_auction_one_valid_bid)

               
class AuctionBidderProcessTest(BaseAuctionWebTest):
    initial_data = test_auction_data
    initial_bids = test_bids

    test_reactivate_invalidated_bids = snitch(reactivate_invalidated_bids)


@unittest.skip("option not available")
class AuctionBidderFeaturesResourceTest(BaseAuctionWebTest):
    initial_data = test_features_auction_data
    initial_status = 'active.tendering'

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class AuctionBidderDocumentResourceTest(BaseAuctionWebTest, AuctionBidderDocumentResourceTestMixin):
    initial_status = 'active.tendering'
    test_create_auction_bidder_document_nopending = snitch(create_auction_bidder_document_nopending)

    def setUp(self):
        super(AuctionBidderDocumentResourceTest, self).setUp()
        # Create bid
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']


class AuctionBidderDocumentWithDSResourceTest(BaseAuctionWebTest,
                                              AuctionBidderDocumentResourceTestMixin,
                                              AuctionBidderDocumentWithDSResourceTestMixin):
    initial_status = 'active.tendering'
    docservice = True
    test_create_auction_bidder_document_nopending = snitch(create_auction_bidder_document_nopending)

    def setUp(self):
        super(AuctionBidderDocumentWithDSResourceTest, self).setUp()
        # Create bid
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']


class FinancialAuctionBidderResourceTest(AuctionBidderResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization

    def test_create_auction_bidder_invalid(self):
        super(FinancialAuctionBidderResourceTest, self).test_create_auction_bidder_invalid()

        organization = deepcopy(self.initial_organization)
        organization['additionalIdentifiers'][0]['scheme'] = u'UA-EDR'
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {'data': {'tenderers': [organization], 'qualified': True, 'eligible': True, "value": {"amount": 500}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertIn({u'description': [{u'additionalIdentifiers': [u'One of additional classifications should be UA-FIN.']}], u'location': u'body', u'name': u'tenderers'}, response.json['errors'])


class FinancialAuctionBidderProcessTest(AuctionBidderProcessTest):
    initial_data = test_financial_auction_data
    initial_bids = test_financial_bids


@unittest.skip("option not available")
class FinancialAuctionBidderFeaturesResourceTest(AuctionBidderFeaturesResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionBidderDocumentWithDSResourceTest(AuctionBidderDocumentWithDSResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionDocumentBidderResourceTest(AuctionBidderDocumentResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionBidderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionBidderDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(AuctionBidderFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(AuctionBidderProcessTest))
    suite.addTest(unittest.makeSuite(AuctionBidderResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionDocumentBidderResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionBidderDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionBidderFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionBidderProcessTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionBidderResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
