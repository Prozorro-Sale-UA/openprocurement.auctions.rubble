# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.document_blanks import (
    # AuctionDocumentResourceTest
    not_found,
    put_auction_document,
    patch_auction_document,
    # AuctionDocumentWithDSResourceTest
    create_auction_document_json_invalid,
    create_auction_document_json,
    put_auction_document_json,
    create_auction_offline_document,
    # FinancialAuctionDocumentWithDSResourceTest
    create_auction_document_vdr,
    put_auction_document_vdr
)

from openprocurement.auctions.rubble.tests.base import BaseAuctionWebTest,  test_financial_auction_data, test_bids, test_financial_bids
from openprocurement.auctions.rubble.tests.blanks.document_blanks import (
    create_auction_document,
    put_auction_offline_document
)

class AuctionDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_auction_document = snitch(create_auction_document)
    test_put_auction_document = snitch(put_auction_document)
    test_patch_auction_document = snitch(patch_auction_document)


class AuctionDocumentResourceTest(BaseAuctionWebTest, AuctionDocumentResourceTestMixin):
    docservice = False


class AuctionDocumentWithDSResourceTest(BaseAuctionWebTest, AuctionDocumentResourceTestMixin):
    docservice = True
    initial_bids = test_bids
    test_create_auction_document_json_invalid = snitch(create_auction_document_json_invalid)
    test_create_auction_document_json = snitch(create_auction_document_json)
    test_put_auction_document_json = snitch(put_auction_document_json)
    test_create_auction_offline_document = snitch(create_auction_offline_document)
    test_put_auction_offline_document = snitch(put_auction_offline_document)

    def check_bids_invalidated_and_activate(self):
        for bid in self.initial_bids:
            response = self.app.get('/auctions/{}/bids/{}?acc_token={}'.format(self.auction_id, bid['id'], self.initial_bids_tokens[bid['id']]))
            self.assertEqual(response.json['data']["status"], "invalid")
            response = self.app.patch_json(
                '/auctions/{}/bids/{}?acc_token={}'.format(self.auction_id, bid['id'], self.initial_bids_tokens[bid['id']]),
                {'data': {"status": "active"}})
            self.assertEqual(response.json['data']["status"], "active")

    def check_bids_are_active(self):
        for bid in self.initial_bids:
            response = self.app.get('/auctions/{}/bids/{}?acc_token={}'.format(self.auction_id, bid['id'], self.initial_bids_tokens[bid['id']]))
            self.assertEqual(response.json['data']["status"], "active")

    def test_create_document_during_and_after_rectificationPeriod(self):

        response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json, {"data": []})

        # test document POST

        response = self.app.post_json('/auctions/{}/documents?acc_token={}'.format(
            self.auction_id, self.auction_token
        ),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

        self.check_bids_invalidated_and_activate()

        # test document PATCH

        response = self.app.patch_json('/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {
            "description": "document description",
            "documentType": 'auctionNotice'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(response.json["data"]["documentType"], 'auctionNotice')

        self.check_bids_invalidated_and_activate()

        # test document PUT

        response = self.app.put_json('/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ),
            {'data': {
                'title': u'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'name.doc', response.json["data"]["title"])

        self.check_bids_invalidated_and_activate()

        self.go_to_rectificationPeriod_end()

        response = self.app.post_json('/auctions/{}/documents?acc_token={}'.format(
            self.auction_id, self.auction_token
        ),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Document can be added only during the rectificationPeriod period.', u'location':
                u'body', u'name': u'data'}
        ])

        self.check_bids_are_active()

        response = self.app.patch_json('/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {
            "description": "document description",
            "documentType": 'auctionNotice'
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Document can be updated only during the rectificationPeriod period.', u'location':
                u'body', u'name': u'data'}
        ])

        self.check_bids_are_active()

        response = self.app.post_json('/auctions/{}/documents?acc_token={}'.format(
            self.auction_id, self.auction_token
        ),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Document can be added only during the rectificationPeriod period.', u'location':
                u'body', u'name': u'data'}
        ])

        self.check_bids_are_active()



class FinancialAuctionDocumentResourceTest(AuctionDocumentResourceTest):
    initial_data = test_financial_auction_data
    initial_bids = test_financial_bids


class FinancialAuctionDocumentWithDSResourceTest(AuctionDocumentWithDSResourceTest):
    initial_data = test_financial_auction_data
    initial_bids = test_financial_bids

    test_create_auction_document_vdr = snitch(create_auction_document_vdr)
    test_put_auction_document_vdr = snitch(put_auction_document_vdr)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
