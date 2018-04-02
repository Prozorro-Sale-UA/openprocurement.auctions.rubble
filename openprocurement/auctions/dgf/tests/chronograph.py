# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.chronograph_blanks import (
    # AuctionSwitchAuctionResourceTest
    switch_to_auction,
    # AuctionSwitchUnsuccessfulResourceTest
    switch_to_unsuccessful,
    # AuctionComplaintSwitchResourceTest
    switch_to_pending,
    switch_to_complaint,
    # AuctionAwardComplaintSwitchResourceTest
    switch_to_pending_award,
    switch_to_complaint_award,
)
from openprocurement.api.utils import get_now
from openprocurement.auctions.dgf.tests.base import BaseAuctionWebTest, test_lots, test_bids, test_financial_auction_data, test_financial_organization, test_financial_bids, test_organization
from openprocurement.auctions.dgf.tests.blanks.chronograph_blanks import (
    # AuctionSwitchQualificationResourceTest
    switch_to_qualification,
    switch_to_qualification1,
    # AuctionAuctionPeriodResourceTest
    set_auction_period,
    reset_auction_period
)


class AuctionSwitchQualificationResourceTest(BaseAuctionWebTest):
    initial_bids = test_bids[:1]
    test_switch_to_qualification1 = snitch(switch_to_qualification1)
    test_switch_to_qualification = snitch(switch_to_qualification)


class AuctionSwitchAuctionResourceTest(BaseAuctionWebTest):
    initial_bids = test_bids

    test_switch_to_auction = snitch(switch_to_auction)


class AuctionSwitchUnsuccessfulResourceTest(BaseAuctionWebTest):

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


@unittest.skip("option not available")
class AuctionLotSwitchQualificationResourceTest(AuctionSwitchQualificationResourceTest):
    initial_lots = test_lots


@unittest.skip("option not available")
class AuctionLotSwitchAuctionResourceTest(AuctionSwitchAuctionResourceTest):
    initial_lots = test_lots


@unittest.skip("option not available")
class AuctionLotSwitchUnsuccessfulResourceTest(AuctionSwitchUnsuccessfulResourceTest):
    initial_lots = test_lots


class AuctionAuctionPeriodResourceTest(BaseAuctionWebTest):
    initial_bids = test_bids

    test_set_auction_period = snitch(set_auction_period)
    test_reset_auction_period = snitch(reset_auction_period)


class AuctionComplaintSwitchResourceTest(BaseAuctionWebTest):

    test_switch_to_pending = snitch(switch_to_pending)
    test_switch_to_complaint = snitch(switch_to_complaint)


@unittest.skip("option not available")
class AuctionLotComplaintSwitchResourceTest(AuctionComplaintSwitchResourceTest):
    initial_lots = test_lots


@unittest.skip("option not available")
class AuctionAwardComplaintSwitchResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    test_switch_to_pending_award = snitch(switch_to_pending_award)
    test_switch_to_complaint_award = snitch(switch_to_complaint_award)

    def setUp(self):
        super(AuctionAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']


@unittest.skip("option not available")
class AuctionLotAwardComplaintSwitchResourceTest(AuctionAwardComplaintSwitchResourceTest):
    initial_lots = test_lots

    def setUp(self):
        super(AuctionAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(self.auction_id), {'data': {
            'suppliers': [self.initial_organization],
            'status': 'pending',
            'bid_id': self.initial_bids[0]['id'],
            'lotID': self.initial_bids[0]['lotValues'][0]['relatedLot']
        }})
        award = response.json['data']
        self.award_id = award['id']


class FinancialAuctionSwitchQualificationResourceTest(AuctionSwitchQualificationResourceTest):
    initial_bids = test_financial_bids[:1]
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionSwitchAuctionResourceTest(AuctionSwitchAuctionResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionSwitchUnsuccessfulResourceTest(AuctionSwitchUnsuccessfulResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotSwitchQualificationResourceTest(AuctionLotSwitchQualificationResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotSwitchAuctionResourceTest(AuctionLotSwitchAuctionResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotSwitchUnsuccessfulResourceTest(AuctionLotSwitchUnsuccessfulResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAuctionPeriodResourceTest(AuctionAuctionPeriodResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionComplaintSwitchResourceTest(AuctionComplaintSwitchResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotComplaintSwitchResourceTest(AuctionLotComplaintSwitchResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionAwardComplaintSwitchResourceTest(AuctionAwardComplaintSwitchResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardComplaintSwitchResourceTest(AuctionLotAwardComplaintSwitchResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
