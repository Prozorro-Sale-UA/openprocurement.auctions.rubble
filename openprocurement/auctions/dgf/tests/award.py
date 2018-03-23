# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy


from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_lots, test_organization,
    test_bids as base_bids,
    test_financial_auction_data,
    test_financial_organization,
)
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.plugins.awarding.v2_1.tests.blanks.award_blanks import (
    # CreateAuctionAwardTest
    create_auction_award_invalid,
    create_auction_award,
    # AuctionAwardProcessTest
    invalid_patch_auction_award,
    patch_auction_award,
    patch_auction_award_admin,
    complate_auction_with_second_award1,
    complate_auction_with_second_award2,
    complate_auction_with_second_award3,
    successful_second_auction_award,
    unsuccessful_auction1,
    unsuccessful_auction2,
    unsuccessful_auction3,
    unsuccessful_auction4,
    unsuccessful_auction5,
    get_auction_awards,
    patch_auction_award_Administrator_change,
    # AuctionLotAwardResourceTest
    create_auction_award_lot,
    patch_auction_award_lot,
    patch_auction_award_unsuccessful_lot,
    # Auction2LotAwardResourceTest
    create_auction_award_2_lots,
    patch_auction_award_2_lots,
    # AuctionAwardComplaintResourceTest
    create_auction_award_complaint_invalid,
    create_auction_award_complaint,
    patch_auction_award_complaint,
    review_auction_award_complaint,
    get_auction_award_complaint,
    get_auction_award_complaints,
    # AuctionLotAwardComplaintResourceTest
    create_auction_award_complaint_lot_complaint,
    patch_auction_award_complaint_lot_complaint,
    get_auction_award_complaint_lot_complaint,
    get_auction_award_complaints_lot_complaint,
    # Auction2LotAwardComplaintResourceTest
    create_auction_award_complaint_2_lot_complaint,
    patch_auction_award_complaint_2_lot_complaint,
    # AuctionAwardComplaintDocumentResourceTest
    not_found_award_complaint_document,
    create_auction_award_complaint_document,
    put_auction_award_complaint_document,
    patch_auction_award_complaint_document,
    # Auction2LotAwardComplaintDocumentResourceTest
    create_auction_award_complaint_document_2_lots,
    put_auction_award_complaint_document_2_lots,
    patch_auction_award_complaint_document_2_lots,
    # AuctionAwardDocumentResourceTest
    not_found_award_document,
    create_auction_award_document,
    put_auction_award_document,
    patch_auction_award_document,
    # Auction2LotAwardDocumentResourceTest
    create_auction_award_document_2_lots,
    put_auction_award_document_2_lots,
    patch_auction_award_document_2_lots,
)
bid = {
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 459,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        },
        "qualified": True
       }
test_bids = deepcopy(base_bids)
test_bids.append(bid)

test_financial_bids = []
for i in test_bids:
    bid = deepcopy(i)
    bid.update({'eligible': True})
    bid['tenderers'] = [test_financial_organization]
    test_financial_bids.append(bid)


class CreateAuctionAwardTest(BaseAuctionWebTest):
    #initial_data = auction_data
    initial_status = 'active.qualification'
    initial_bids = test_bids
    docservice = True

    test_create_auction_award_invalid = snitch(create_auction_award_invalid)
    test_create_auction_award = snitch(create_auction_award)



class AuctionAwardProcessTest(BaseAuctionWebTest):
    #initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids
    docservice = True

    test_invalid_patch_auction_award = snitch(invalid_patch_auction_award)
    test_patch_auction_award = snitch(patch_auction_award)
    test_patch_auction_award_admin = snitch(patch_auction_award_admin)
    test_complate_auction_with_second_award1 = snitch(complate_auction_with_second_award1)
    test_complate_auction_with_second_award2 = snitch(complate_auction_with_second_award2)
    test_complate_auction_with_second_award3 = snitch(complate_auction_with_second_award3)
    test_successful_second_auction_award = snitch(successful_second_auction_award)
    test_unsuccessful_auction1 = snitch(unsuccessful_auction1)
    test_unsuccessful_auction2 = snitch(unsuccessful_auction2)
    test_unsuccessful_auction3 = snitch(unsuccessful_auction3)
    test_unsuccessful_auction4 = snitch(unsuccessful_auction4)
    test_unsuccessful_auction5 = snitch(unsuccessful_auction5)
    test_get_auction_awards = snitch(get_auction_awards)
    test_patch_auction_award_Administrator_change = snitch(patch_auction_award_Administrator_change)

    def setUp(self):
        super(AuctionAwardProcessTest, self).setUp()
        self.post_auction_results()


@unittest.skip("option not available")
class AuctionLotAwardResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_auction_award_lot = snitch(create_auction_award_lot)
    test_patch_auction_award_lot = snitch(patch_auction_award_lot)
    test_patch_auction_award_unsuccessful_lot = snitch(patch_auction_award_unsuccessful_lot)


@unittest.skip("option not available")
class Auction2LotAwardResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_auction_award_2_lots = snitch(create_auction_award_2_lots)
    test_patch_auction_award_2_lots = snitch(patch_auction_award_2_lots)


@unittest.skip("option not available")
class AuctionAwardComplaintResourceTest(BaseAuctionWebTest):
    #initial_data = auction_data
    initial_status = 'active.qualification'
    initial_bids = test_bids

    test_create_auction_award_complaint_invalid = snitch(create_auction_award_complaint_invalid)
    test_create_auction_award_complaint = snitch(create_auction_award_complaint)
    test_patch_auction_award_complaint = snitch(patch_auction_award_complaint)
    test_review_auction_award_complaint = snitch(review_auction_award_complaint)
    test_get_auction_award_complaint = snitch(get_auction_award_complaint)
    test_get_auction_award_complaints = snitch(get_auction_award_complaints)

    def setUp(self):
        super(AuctionAwardComplaintResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']


@unittest.skip("option not available")
class AuctionLotAwardComplaintResourceTest(BaseAuctionWebTest):
    #initial_data = auction_data
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_auction_award_complaint_lot_complaint = snitch(create_auction_award_complaint_lot_complaint)
    test_patch_auction_award_complaint_lot_complaint = snitch(patch_auction_award_complaint_lot_complaint)
    test_get_auction_award_complaint_lot_complaint = snitch(get_auction_award_complaint_lot_complaint)
    test_get_auction_award_complaints_lot_complaint = snitch(get_auction_award_complaints_lot_complaint)

    def setUp(self):
        super(AuctionLotAwardComplaintResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


@unittest.skip("option not available")
class Auction2LotAwardComplaintResourceTest(BaseAuctionWebTest):
    initial_lots = 2 * test_lots

    test_create_auction_award_complaint_2_lot_complaint = snitch(create_auction_award_complaint_2_lot_complaint)
    test_patch_auction_award_complaint_2_lot_complaint = snitch(patch_auction_award_complaint_2_lot_complaint)
    test_get_auction_award_complaint_lot_complaint = snitch(get_auction_award_complaint_lot_complaint)
    test_get_auction_award_complaints_lot_complaint = snitch(get_auction_award_complaints_lot_complaint)



@unittest.skip("option not available")
class AuctionAwardComplaintDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    test_not_found_award_complaint_document = snitch(not_found_award_complaint_document)
    test_create_auction_award_complaint_document = snitch(create_auction_award_complaint_document)
    test_put_auction_award_complaint_document = snitch(put_auction_award_complaint_document)
    test_patch_auction_award_complaint_document = snitch(patch_auction_award_complaint_document)


    def setUp(self):
        super(AuctionAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        # Create complaint for award
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
            self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']


@unittest.skip("option not available")
class Auction2LotAwardComplaintDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    test_create_auction_award_complaint_document_2_lots = snitch(create_auction_award_complaint_document_2_lots)
    test_put_auction_award_complaint_document_2_lots = snitch(put_auction_award_complaint_document_2_lots)
    test_patch_auction_award_complaint_document_2_lots = snitch(patch_auction_award_complaint_document_2_lots)

    def setUp(self):
        super(Auction2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        # Create complaint for award
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
            self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']


class AuctionAwardDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.auction'
    initial_bids = test_bids

    test_not_found_award_document = snitch(not_found_award_document)
    test_create_auction_award_document = snitch(create_auction_award_document)
    test_put_auction_award_document = snitch(put_auction_award_document)
    test_patch_auction_award_document = snitch(patch_auction_award_document)

    def setUp(self):
        super(AuctionAwardDocumentResourceTest, self).setUp()
        self.post_auction_results()


@unittest.skip("option not available")
class Auction2LotAwardDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    test_create_auction_award_document_2_lots = snitch(create_auction_award_document_2_lots)
    test_put_auction_award_document_2_lots = snitch(put_auction_award_document_2_lots)
    test_patch_auction_award_document_2_lots = snitch(patch_auction_award_document_2_lots)

    def setUp(self):
        super(Auction2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


class CreateFinancialAuctionAwardTest(CreateAuctionAwardTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAwardProcessTest(AuctionAwardProcessTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardResourceTest(AuctionLotAwardResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardResourceTest(Auction2LotAwardResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionAwardComplaintResourceTest(AuctionAwardComplaintResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardComplaintResourceTest(AuctionLotAwardComplaintResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data


@unittest.skip("option not available")
class FinancialAuction2LotAwardComplaintResourceTest(Auction2LotAwardComplaintResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionAwardComplaintDocumentResourceTest(AuctionAwardComplaintDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardComplaintDocumentResourceTest(Auction2LotAwardComplaintDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAwardDocumentResourceTest(AuctionAwardDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardDocumentResourceTest(Auction2LotAwardDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Auction2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Auction2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(Auction2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Auction2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(AuctionAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(AuctionAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotAwardResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotAwardResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
