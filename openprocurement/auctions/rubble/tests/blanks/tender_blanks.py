# -*- coding: utf-8 -*-
import unittest

from copy import deepcopy
from datetime import timedelta, time
from iso8601 import parse_date

from openprocurement.auctions.core.constants import (
    DGF_CDB2_CLASSIFICATION_PRECISELY_FROM as CLASSIFICATION_PRECISELY_FROM,
    DGF_CDB2_ADDRESS_REQUIRED_FROM as DGF_ADDRESS_REQUIRED_FROM
)
from openprocurement.auctions.core.tests.base import JSON_RENDERER_ERROR
from openprocurement.auctions.core.utils import get_now, SANDBOX_MODE, TZ

from openprocurement.auctions.rubble.constants import (
  MINIMAL_PERIOD_FROM_RECTIFICATION_END
)
from openprocurement.auctions.rubble.models import (
    LOTIDENTIFIER_ID_REQUIRED_FROM
)
from openprocurement.auctions.rubble.tests.base import (
    test_financial_organization,
    test_item,
    DEFAULT_ACCELERATION,
)

# AuctionTest


def create_role(self):
    fields = set([
        'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru',
        'description', 'description_en', 'description_ru', 'lotIdentifier', 'tenderAttempts',
        'features', 'guarantee', 'hasEnquiries', 'items', 'lots', 'minimalStep', 'mode',
        'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru',
        'procurementMethodType', 'procuringEntity', 'minNumberOfQualifiedBids',
        'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru',
        'title', 'title_en', 'title_ru', 'value', 'auctionPeriod', 'rectificationPeriod'
    ])
    if SANDBOX_MODE:
        fields.add('procurementMethodDetails')
    self.assertEqual(set(self.auction._fields) - self.auction._options.roles['create'].fields, fields)


def edit_role(self):
    fields = set([
        'description', 'description_en', 'description_ru',
        'features', 'hasEnquiries', 'items', 'procuringEntity',
        'value', 'minimalStep', 'guarantee', 'tenderAttempts', 'title_en', 'lotIdentifier', 'title_ru',
        'title'
    ])
    if SANDBOX_MODE:
        fields.add('procurementMethodDetails')
    self.assertEqual(set(self.auction._fields) - self.auction._options.roles['edit_active.tendering'].fields, fields)


# AuctionResourceTest


def create_auction_validation_accelerated(self):
    request_path = '/auctions'
    now = get_now()
    auction_data = deepcopy(self.initial_data)
    if SANDBOX_MODE:
        startDate = (now + timedelta(days=8, hours=4) / DEFAULT_ACCELERATION).isoformat()
    else:
        startDate = (now + timedelta(days=8, hours=4)).isoformat()
    auction_data['auctionPeriod'] = {'startDate': startDate}
    response = self.app.post_json(request_path, {'data': auction_data}, status=201)
    auction = response.json['data']
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender_period_startDate = parse_date(auction['tenderPeriod']['startDate'], None)
    if not tender_period_startDate.tzinfo:
        tender_period_startDate = TZ.localize(tender_period_startDate)
    tender_period_endDate = parse_date(auction['tenderPeriod']['endDate'], None)
    if not tender_period_endDate.tzinfo:
        tender_period_endDate = TZ.localize(tender_period_endDate)
    if SANDBOX_MODE:
        self.assertLess((tender_period_endDate - tender_period_startDate), timedelta(days=8, hours=4) / DEFAULT_ACCELERATION)
    else:
        self.assertLess((tender_period_endDate - tender_period_startDate), timedelta(days=8, hours=4))


def create_auction_invalid(self):
    request_path = '/auctions'
    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
            u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
    ])

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        JSON_RENDERER_ERROR
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
            u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
            u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': []}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
            u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'invalid_value'}}, status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'procurementMethodType is not implemented', u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value', 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {'value': 'invalid_value', 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethod': 'invalid_value', 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn({u'description': [u"Value must be one of ['open', 'selective', 'limited']."], u'location': u'body', u'name': u'procurementMethod'}, response.json['errors'])
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'tenderPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'enquiryPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])

    response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': 'invalid_value'}, 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u"Could not parse invalid_value. Should be ISO8601."]}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': '9999-12-31T23:59:59.999999'}, 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u'date value out of range']}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    self.initial_data['tenderPeriod'] = self.initial_data.pop('auctionPeriod')
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['auctionPeriod'] = self.initial_data.pop('tenderPeriod')
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'startDate': [u'This field is required.']}, u'location': u'body', u'name': u'auctionPeriod'}
    ])

    self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2014-10-01T00:00:00'}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data.pop('tenderPeriod')
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'startDate': [u'period should begin before its end']}, u'location': u'body', u'name': u'tenderPeriod'}
    ])

    now = get_now()

    data = self.initial_data['auctionPeriod']
    self.initial_data['auctionPeriod'] = {'startDate': (now + timedelta(days=15)).isoformat(), 'endDate': (now + timedelta(days=15)).isoformat()}
    self.initial_data['awardPeriod'] = {'startDate': (now + timedelta(days=14)).isoformat(), 'endDate': (now + timedelta(days=14)).isoformat()}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['auctionPeriod'] = data
    del self.initial_data['awardPeriod']
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'period should begin after auctionPeriod'], u'location': u'body', u'name': u'awardPeriod'}
    ])

    auction_data = deepcopy(self.initial_data)
    if SANDBOX_MODE:
        auction_data['auctionPeriod'] = {'startDate': (now + timedelta(days=5) / DEFAULT_ACCELERATION).isoformat()}
    else:
        auction_data['auctionPeriod'] = {'startDate': (now + timedelta(days=5)).isoformat()}
    response = self.app.post_json(request_path, {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'rectificationPeriod.endDate should come at least 5 working days earlier than tenderPeriod.endDate'], u'location': u'body', u'name': u'rectificationPeriod'},
        {u'description': [u'tenderPeriod should be greater than 6 days'], u'location': u'body', u'name': u'tenderPeriod'}
    ])

    if SANDBOX_MODE:
        auction_data['auctionPeriod'] = {'startDate': (now + timedelta(days=10) / DEFAULT_ACCELERATION).isoformat()}
        auction_data['rectificationPeriod'] = {'endDate': (now + timedelta(days=9) / DEFAULT_ACCELERATION).isoformat()}
    else:
        auction_data['auctionPeriod'] = {'startDate': (now + timedelta(days=10)).isoformat()}
        auction_data['rectificationPeriod'] = {'endDate': (now + timedelta(days=9)).isoformat()}
    response = self.app.post_json(request_path, {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '1000.0'}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value should be less than value of auction'], u'location': u'body', u'name': u'minimalStep'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '100.0', 'valueAddedTaxIncluded': False}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of auction'], u'location': u'body', u'name': u'minimalStep'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '100.0', 'currency': "USD"}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be identical to currency of value of auction'], u'location': u'body', u'name': u'minimalStep'}
    ])

    auction_data = deepcopy(self.initial_data)
    auction_data['value'] = {'amount': '100.0', 'currency': "USD"}
    auction_data['minimalStep'] = {'amount': '5.0', 'currency': "USD"}
    response = self.app.post_json(request_path, {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be only UAH'], u'location': u'body', u'name': u'value'}
    ])

    data = self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    del self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'contactPoint': {u'email': [u'telephone or email should be present']}}, u'location': u'body', u'name': u'procuringEntity'}
    ])


@unittest.skipIf(get_now() < LOTIDENTIFIER_ID_REQUIRED_FROM, "Can`t create auction without lotIdentifier only from {}".format(LOTIDENTIFIER_ID_REQUIRED_FROM))
def required_dgf_id(self):
    data = self.initial_data.copy()
    del data['lotIdentifier']
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{"location": "body", "name": "lotIdentifier", "description": ["This field is required."]}])

    data['lotIdentifier'] = self.initial_data['lotIdentifier']
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertIn('lotIdentifier', auction)
    self.assertEqual(data['lotIdentifier'], auction['lotIdentifier'])


@unittest.skipIf(get_now() < DGF_ADDRESS_REQUIRED_FROM, "Can`t create auction without item.address only from {}".format(DGF_ADDRESS_REQUIRED_FROM))
def required_dgf_item_address(self):
    auction_data = deepcopy(self.initial_data)
    del auction_data['items'][0]['address']

    address = {
        "countryName": u"Україна",
        "postalCode": "79000",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова 1"
    }

    # CAV-PS specific location code test (address is required)
    auction_data['items'][0]['classification'] = {
        "scheme": u"CAV-PS",
        "id": u"04210000-3",
        "description": u"Промислова нерухомість"
    }
    response = self.app.post_json('/auctions', {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{"location": "body", "name": "items", "description": [{"address": ["This field is required."]}]}])

    auction_data['items'][0]["address"] = address

    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    del auction_data['items'][0]['address']

    # CPV specific location code test (address is required)
    auction_data['items'][0]['classification'] = {
        "scheme": u"CPV",
        "id": u"34965000-9",
        "description": u"Всебічно направлений далекомірний радіомаяк"
    }
    response = self.app.post_json('/auctions', {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{"location": "body", "name": "items", "description": [{"address": ["This field is required."]}]}])

    auction_data['items'][0]["address"] = address

    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    del auction_data['items'][0]["address"]

    # CAV-PS/CPV non specific location code test (address is not required)
    auction_data['items'][0]['classification'] = {
        "scheme": u"CPV",
        "id": u"90470000-2",
        "description": u"Послуги з чищення каналізаційних колекторів"
    }
    item = deepcopy(auction_data['items'][0])
    item['classification'] = {
        "scheme": u"CAV-PS",
        "id": u"07227000-6",
        "description": u"Застава - Інше"
    }
    auction_data['items'].append(item)

    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    auction_data['items'][0]["address"] = address

    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')


def create_auction_auctionPeriod(self):
    data = self.initial_data.copy()
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertIn('tenderPeriod', auction)
    self.assertIn('auctionPeriod', auction)
    self.assertNotIn('startDate', auction['auctionPeriod'])
    self.assertEqual(parse_date(data['auctionPeriod']['startDate']).date(), parse_date(auction['auctionPeriod']['shouldStartAfter'], TZ).date())
    if SANDBOX_MODE:
        auction_startDate = parse_date(data['auctionPeriod']['startDate'], None)
        if not auction_startDate.tzinfo:
            auction_startDate = TZ.localize(auction_startDate)
        tender_endDate = parse_date(auction['tenderPeriod']['endDate'], None)
        if not tender_endDate.tzinfo:
            tender_endDate = TZ.localize(tender_endDate)
        self.assertLessEqual((auction_startDate - tender_endDate).total_seconds(), 70)
    else:
        self.assertEqual(parse_date(auction['tenderPeriod']['endDate']).date(), parse_date(data['auctionPeriod']['startDate'], TZ).date() - timedelta(days=1))
        self.assertEqual(parse_date(auction['tenderPeriod']['endDate']).time(), time(20, 0))


def create_auction_rectificationPeriod_generated(self):
    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertIn('tenderPeriod', auction)
    self.assertIn('enquiryPeriod', auction)
    self.assertIn('rectificationPeriod', auction)
    self.assertIn('auctionPeriod', auction)
    self.assertNotIn('startDate', auction['auctionPeriod'])
    self.assertEqual(parse_date(self.initial_data['auctionPeriod']['startDate']).date(), parse_date(auction['auctionPeriod']['shouldStartAfter'], TZ).date())
    tender_period_end_date = parse_date(auction['tenderPeriod']['endDate']).replace(tzinfo=None)
    rectification_period_end_date = parse_date(auction['rectificationPeriod']['endDate']).replace(tzinfo=None)

    timedelta_during_periods_ends = tender_period_end_date - rectification_period_end_date
    if not SANDBOX_MODE:
        self.assertEqual(timedelta_during_periods_ends, MINIMAL_PERIOD_FROM_RECTIFICATION_END)
    else:
        self.assertEqual(timedelta_during_periods_ends, (MINIMAL_PERIOD_FROM_RECTIFICATION_END / DEFAULT_ACCELERATION))


def create_auction_rectificationPeriod_set(self):
    auction_data = deepcopy(self.initial_data)
    auction_data['rectificationPeriod'] = {'endDate': (get_now() + timedelta(days=2)).isoformat()}
    auction_data['auctionPeriod'] = {'startDate': (get_now() + timedelta(days=10)).isoformat()}
    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    self.assertIn('rectificationPeriod', auction)
    timedelta_during_set_periods_ends = parse_date(auction['tenderPeriod']['endDate']) - parse_date(auction_data['rectificationPeriod']['endDate'])
    self.assertGreaterEqual(timedelta_during_set_periods_ends, MINIMAL_PERIOD_FROM_RECTIFICATION_END)
    self.assertEqual(timedelta_during_set_periods_ends, parse_date(auction['tenderPeriod']['endDate']) - parse_date(auction['rectificationPeriod']['endDate']))


def create_auction_generated(self):
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
        u'tenderPeriod', u'minimalStep', u'items', u'value', u'procuringEntity', u'next_check', u'lotIdentifier',
        u'procurementMethod', u'awardCriteria', u'submissionMethod', u'title', u'owner', u'auctionPeriod',
        u'tenderAttempts', u'rectificationPeriod'
    ]))
    self.assertNotEqual(data['id'], auction['id'])
    self.assertNotEqual(data['doc_id'], auction['id'])
    self.assertNotEqual(data['auctionID'], auction['auctionID'])


def create_auction(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/auctions', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    if self.initial_organization == test_financial_organization:
        self.assertEqual(set(auction) - set(self.initial_data), set([
            u'id', u'dateModified', u'auctionID', u'date', u'status', u'procurementMethod', u'rectificationPeriod',
            u'awardCriteria', u'submissionMethod', u'next_check', u'owner', u'enquiryPeriod', u'tenderPeriod',
            u'eligibilityCriteria_en', u'eligibilityCriteria', u'eligibilityCriteria_ru'
        ]))
    else:
        self.assertEqual(set(auction) - set(self.initial_data), set([
            u'id', u'dateModified', u'auctionID', u'date', u'status', u'procurementMethod', u'rectificationPeriod',
            u'awardCriteria', u'submissionMethod', u'next_check', u'owner', u'enquiryPeriod', u'tenderPeriod',
        ]))
    self.assertIn(auction['id'], response.headers['Location'])

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(auction))
    self.assertEqual(response.json['data'], auction)

    response = self.app.post_json('/auctions?opt_jsonp=callback', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"', response.body)

    response = self.app.post_json('/auctions?opt_pretty=1', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json('/auctions', {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    auction_data = deepcopy(self.initial_data)
    auction_data['guarantee'] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    data = response.json['data']
    self.assertIn('guarantee', data)
    self.assertEqual(data['guarantee']['amount'], 100500)
    self.assertEqual(data['guarantee']['currency'], "USD")


def create_auction_with_item_with_schema_properties(self):
    """
        Test flexible fields
        if item has defined 'schema_properties', then created  auction
        will contain appropriate schema
    """

    # prepare request data

    # build classification
    classification = {
        "scheme": u"CPV",
        "id": u"34621100-7",
        "description": u"Вантажні залізничні вагони"
    }

    # build schema_properties
    schema_properties_code = '346211'
    schema_properties_version = '001'
    rolling_stock = 'test rolling stock'
    loading_restriction = 'test loading restriction'
    schema_properties = {
        'code': schema_properties_code,
        'version': schema_properties_version,
        'properties': {
            'rollingStock': rolling_stock,
            'loadingRestriction': loading_restriction
        }
    }
    # build item
    item = deepcopy(test_item)
    item['classification'] = classification
    item['schema_properties'] = schema_properties

    # build auction
    auction_data = deepcopy(self.initial_data)
    auction_data['items'] = [item]

    entrypoint = '/auctions'
    request_data = {"data": auction_data}
    response = self.app.post_json(entrypoint, request_data)

    auction = response.json['data']

    # get created auction
    entrypoint = '/auctions/{}'.format(auction['id'])
    response = self.app.get(entrypoint)

    # check schema_properties
    auction = response.json['data']
    schema_properties = auction['items'][0]['schema_properties']

    self.assertIsNotNone(schema_properties)
    self.assertEqual(schema_properties['code'], schema_properties_code)
    self.assertEqual(schema_properties['version'], schema_properties_version)
    self.assertEqual(schema_properties['properties']['rollingStock'], rolling_stock)
    self.assertEqual(schema_properties['properties']['loadingRestriction'], loading_restriction)


def create_auction_with_item_with_invalid_schema_properties(self):
    """
        Test create auction with item with invalida schema_properties
        'shcema_properties' is invalid then 'classification' id
        don`t start with 'shcema_properties' id
    """

    # prepare request data

    # build classification with invalid id
    classification = {
        "scheme": u"CPV",
        "id": u"34621200-8",
        "description": u"Вантажні залізничні вагони"
    }

    # build schema_properties
    schema_properties_code = '346211'
    schema_properties_version = '001'
    rolling_stock = 'test rolling stock'
    loading_restriction = 'test loading restriction'
    schema_properties = {
        'code': schema_properties_code,
        'version': schema_properties_version,
        'properties': {
            'rollingStock': rolling_stock,
            'loadingRestriction': loading_restriction
        }
    }
    # build item
    item = deepcopy(test_item)
    item['classification'] = classification
    item['schema_properties'] = schema_properties

    # build auction
    auction_data = deepcopy(self.initial_data)
    auction_data['items'] = [item]

    entrypoint = '/auctions'
    request_data = {"data": auction_data}
    response = self.app.post_json(entrypoint, request_data, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')


def additionalClassifications(self):
    auction_data = deepcopy(self.initial_data)
    # CAV-PS classification test
    auction_data['items'][0]['classification'] = {
        "scheme": u"CAV-PS",
        "id": u"04210000-3",
        "description": u"Промислова нерухомість"
    }
    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    data = response.json['data']
    self.assertEqual(data['items'][0]['classification']['scheme'], 'CAV-PS')
    self.assertEqual(data['items'][0]['classification']['id'], '04210000-3')

    # CAV-PS and CPV classification in different items
    auction_data = deepcopy(self.initial_data)
    item = deepcopy(auction_data['items'][0])
    item['classification'] = {
        "scheme": u"CAV-PS",
        "id": u"04210000-3",
        "description": u"Промислова нерухомість"
    }
    auction_data['items'].append(item)
    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    data = response.json['data']
    self.assertEqual(data['items'][1]['classification']['scheme'], 'CAV-PS')
    self.assertEqual(data['items'][1]['classification']['id'], '04210000-3')
    self.assertEqual(data['items'][0]['classification']['scheme'], 'CPV')
    self.assertEqual(data['items'][0]['classification']['id'], '66113000-5')

    # Additional Classification

    auction_data['items'][0]['additionalClassifications'] = [{
        "scheme": u"CPVS",
        "id": u"PA01-7",
        "description": u"Найм"
    }]
    response = self.app.post_json('/auctions', {'data': auction_data}, status=201)
    data = response.json['data']
    self.assertEqual(data['items'][0]['additionalClassifications'][0]['scheme'], 'CPVS')
    self.assertEqual(data['items'][0]['additionalClassifications'][0]['id'], 'PA01-7')

    # CAV-PS classification fail test
    auction_data['items'][0]['classification'] = {
        "scheme": u"CAV-PS",
        "id": u"07227000-3",    # last number is wrong
        "description": u"Застава - Інше"
    }
    response = self.app.post_json('/auctions', {'data': auction_data}, status=422)
    self.assertTrue(response.json['errors'][0]['description'][0]['classification'])

    # Bad classification
    auction_data['items'][0]['classification'] = {
        "scheme": u"CAE",   # wrong scheme
        "id": u"07227000-6",
        "description": u"Застава - Інше"
    }
    response = self.app.post_json('/auctions', {'data': auction_data}, status=422)
    self.assertEqual(response.json['errors'], [{u'description': [{u'classification': {u'scheme': [u"Value must be one of [u'CPV', u'CAV-PS']."]}}], u'location': u'body', u'name': u'items'}])

    # Additional Classification wrong id
    auction_data['items'][0]['additionalClassifications'] = [{
        "scheme": u"CPVS",
        "id": u"PA01-2",    # Wrong ID
        "description": u"Найм"
    }]
    response = self.app.post_json('/auctions', {'data': auction_data}, status=422)
    self.assertRegexpMatches(response.json['errors'][0]['description'][0]['additionalClassifications'][0]['id'][0], "Value must be one of*")


@unittest.skipIf(get_now() < CLASSIFICATION_PRECISELY_FROM, "Can`t setup precisely classification from {}".format(CLASSIFICATION_PRECISELY_FROM))
def cavps_cpvs_classifications(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    data = deepcopy(self.initial_data)
    data['guarantee'] = {"amount": 100, "currency": "UAH"}

    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    auction_token = response.json['access']['token']

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], auction_token
    ), {'data': {'items': [{"classification": {
        "scheme": u"CPV",
        "id": u"19212310-1",
        "description": u"Нерухоме майно"
    }}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], auction_token
    ), {'data': {'items': [{"classification": {
        "scheme": u"CPV",
        "id": u"03100000-2",
        "description": u"Нерухоме майно"
    }}]}}, status=422)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], auction_token
    ), {'data': {'items': [{"additionalClassifications": [auction['items'][0]["classification"]]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')


def patch_auction(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    data = deepcopy(self.initial_data)
    data['guarantee'] = {"amount": 100, "currency": "UAH"}

    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']
    dateModified = auction.pop('dateModified')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'cancelled'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['status'], 'cancelled')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], owner_token
    ), {'data': {'status': 'cancelled'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['status'], 'cancelled')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'procuringEntity': {'kind': 'defense'}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('kind', response.json['data']['procuringEntity'])

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], owner_token
    ), {'data': {'procurementMethodRationale': 'Open'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_auction = response.json['data']
    new_dateModified = new_auction.pop('dateModified')
    new_auction['rectificationPeriod'].pop('invalidationDate')
    self.assertEqual(auction, new_auction)
    self.assertNotEqual(dateModified, new_dateModified)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], owner_token
    ), {'data': {'dateModified': new_dateModified}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_auction2 = response.json['data']
    new_dateModified2 = new_auction2.pop('dateModified')
    new_auction2['rectificationPeriod'].pop('invalidationDate')
    self.assertEqual(new_auction, new_auction2)
    self.assertNotEqual(new_dateModified, new_dateModified2)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], owner_token
    ), {'data': {'items': [self.initial_data['items'][0]]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], owner_token
    ), {'data': {'enquiryPeriod': {'endDate': new_dateModified2}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_auction = response.json['data']
    self.assertIn('startDate', new_auction['enquiryPeriod'])

    # Check availability of value, minimalStep, guarantee
    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertIn('value', response.json['data'])
    self.assertIn('guarantee', response.json['data'])
    self.assertIn('minimalStep', response.json['data'])

    # 422 very low amount
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token),
                                   {'data': {'value': {'amount': auction['value']['amount'] - 80}}}, status=422)
    self.assertEqual(response.json['errors'], [{'location': 'body', 'name': 'minimalStep', 'description': [u'value should be less than value of auction']}])

    auction_data = self.db.get(auction['id'])
    auction_data['status'] = 'complete'
    self.db.save(auction_data)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        auction['id'], owner_token
    ), {'data': {'status': 'active.auction'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update auction in current (complete) status")


def patch_auction_rectificationPeriod_invalidationDate(self):

    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    data = deepcopy(self.initial_data)
    data['guarantee'] = {"amount": 100, "currency": "UAH"}

    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertNotIn('invalidationDate', response.json['data']['rectificationPeriod'])
    auction = response.json['data']
    owner_token = response.json['access']['token']

    # patch one of main auction field by auction owner

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"value": {"amount": 120}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('invalidationDate', response.json['data']['rectificationPeriod'])


def patch_old_auction_rectificationPeriod_invalidationDate(self):

    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    data = deepcopy(self.initial_data)
    data['auctionPeriod']['startDate'] = (get_now().date() + timedelta(days=8)).isoformat()
    data['guarantee'] = {"amount": 100, "currency": "UAH"}

    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertNotIn('invalidationDate', response.json['data']['rectificationPeriod'])
    auction = response.json['data']
    owner_token = response.json['access']['token']

    db_auction = self.db.get(auction['id'])
    del db_auction['rectificationPeriod']
    self.db.save(db_auction)

    # patch one of main auction field by auction owner

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"value": {"amount": 120}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('invalidationDate', response.json['data']['rectificationPeriod'])


def auction_Administrator_change(self):
    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']

    response = self.app.post_json('/auctions/{}/questions'.format(auction['id']), {'data': {'title': 'question title', 'description': 'question description', 'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'mode': u'test', 'procuringEntity': {"identifier": {"id": "00000000"}}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['mode'], u'test')
    self.assertEqual(response.json['data']["procuringEntity"]["identifier"]["id"], "00000000")

    response = self.app.patch_json('/auctions/{}/questions/{}'.format(auction['id'], question['id']), {"data": {"answer": "answer"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {"location": "url", "name": "role", "description": "Forbidden"}
    ])
    self.app.authorization = authorization

    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    auction_token = response.json['access']['token']

    response = self.app.post_json('/auctions/{}/cancellations?acc_token={}'.format(
        auction['id'], auction_token
    ), {'data': {'reason': 'cancellation reason', 'status': 'active'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'mode': u'test'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['mode'], u'test')

    self.app.authorization = authorization
    auction_data = deepcopy(self.initial_data)
    auction_data['guarantee'] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']

    self.app.authorization = ('Basic', ('administrator', ''))

    # Check availability of value, minimalStep, guarantee

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertIn('value', response.json['data'])
    self.assertIn('guarantee', response.json['data'])
    self.assertIn('minimalStep', response.json['data'])

    # 422 very low amount
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'value': {'amount': auction['value']['amount'] - 80}}}, status=422)
    self.assertEqual(response.json['errors'], [{'location': 'body', 'name': 'minimalStep', 'description': [u'value should be less than value of auction']}])


# AuctionFieldsEditingTest


def patch_auction_denied(self):

    # patch auction during rectificationPeriod

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'value': {'amount': 80}}}, status=200)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['value']['amount'], 80)
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'minimalStep': {'amount': 20}}}, status=200)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['minimalStep']['amount'], 20)

    self.go_to_rectificationPeriod_end()

    # patch auction after the rectificationPeriod.endDate

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'value': {'amount': 80}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn(u'Auction can be edited only during the rectification period',
                  response.json['errors'][0][u'description'])
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'minimalStep': {'amount': 20}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn(u'Auction can be edited only during the rectification period',
                  response.json['errors'][0][u'description'])


def patch_auction_during_rectification_period(self):
    auction_data = deepcopy(self.initial_maximum_data)
    classification_data_edited = {
        "scheme": "CAV-PS",
        "description": "Edited field",
        "id": "06125000-4"
    }
    unit_data_edited = {
        "code": "44617100-0",
        "name": "edited item"
    }
    address_data_edited = auction_data["procuringEntity"]["address"]
    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']

    for param in ['title', 'title_en', 'title_ru']:
        response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
            self.auction_id, self.auction_token
        ), {'data': {param: auction[param] + u' EDITED'}}, status=200)
        self.assertNotEqual(response.json['data'][param], auction[param])
        self.assertEqual(response.json['data'][param], auction[param] + u' EDITED')

    for param in ['description', 'description_en', 'description_ru']:
        response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
            self.auction_id, self.auction_token
        ), {'data': {'items': [{param: auction[param] + u' EDITED'}]}}, status=200)
        self.assertNotEqual(response.json['data']['items'][0][param], auction['items'][0][param])
        self.assertEqual(response.json['data']['items'][0][param], auction[param] + u' EDITED')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'items': [{"address": address_data_edited}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['items'][0]['address'], auction['items'][0]['address'])
    self.assertEqual(response.json['data']['items'][0]['address'], address_data_edited)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'items': [{"classification": classification_data_edited}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['items'][0]['classification'], auction['items'][0]['classification'])
    self.assertEqual(response.json['data']['items'][0]['classification'], classification_data_edited)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'items': [{"unit": unit_data_edited}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['items'][0]['unit'], auction['items'][0]['unit'])
    self.assertEqual(response.json['data']['items'][0]['unit'], unit_data_edited)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'items': [{"quantity": auction['items'][0]['quantity'] + 1}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['items'][0]['quantity'], auction['items'][0]['quantity'])
    self.assertEqual(response.json['data']['items'][0]['quantity'], auction['items'][0]['quantity'] + 1)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'tenderAttempts': auction['tenderAttempts'] + 1}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['tenderAttempts'], auction['tenderAttempts'])
    self.assertEqual(response.json['data']['tenderAttempts'], auction['tenderAttempts'] + 1)

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), {'data': {'lotIdentifier': auction['lotIdentifier'] + u'EDITED'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['lotIdentifier'], auction['lotIdentifier'])
    self.assertEqual(response.json['data']['lotIdentifier'], auction['lotIdentifier'] + u'EDITED')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(self.auction_id, self.auction_token), {
        'data': {'value': {'valueAddedTaxIncluded': False, 'amount': auction['value']['amount']},
                 'minimalStep': {'valueAddedTaxIncluded': False}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['value']['valueAddedTaxIncluded'], False)
    self.assertEqual(response.json['data']['minimalStep']['valueAddedTaxIncluded'], False)


def invalidate_bids_auction_unsuccessful(self):

    # patch auction already created

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(self.auction_id, self.auction_token),
                                   {'data': {'value': {'amount': 80}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    # switch to active.auction

    response = self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")
    self.assertNotIn("awards", response.json['data'])
    self.assertNotIn("bids", response.json['data'])


# AuctionProcessTest


def one_valid_bid_auction(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction

    data = deepcopy(self.initial_data)
    data['minNumberOfQualifiedBids'] = 1

    response = self.app.post_json('/auctions',
                                  {"data": data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    response = self.set_status('active.tendering', {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}})
    self.assertIn("auctionPeriod", response.json['data'])
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
    # switch to active.qualification
    self.set_status('active.auction', {'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
    self.assertNotIn('auctionPeriod', response.json['data'])
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending.verification award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending.verification'][0]
    award_date = [i['date'] for i in response.json['data'] if i['status'] == 'pending.verification'][0]
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award_id, owner_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
    response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, owner_token), {"data": {
        "description": "auction protocol",
        "documentType": 'auctionProtocol'
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
    self.assertEqual(response.json["data"]["author"], 'auction_owner')

    # set award as pending.payment
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "pending.payment"}})
    self.assertNotEqual(response.json['data']['date'], award_date)
    # set award as active
    self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "active"}})
    # get contract id
    response = self.app.get('/auctions/{}'.format(auction_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    auction = self.db.get(auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(auction_id, contract_id, owner_token), {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'complete')


def one_invalid_bid_auction(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction
    data = deepcopy(self.initial_data)
    data['minNumberOfQualifiedBids'] = 1

    response = self.app.post_json('/auctions',
                                  {"data": data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True}})
    # switch to active.qualification
    self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending.verification'][0]
    # set award as unsuccessful
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                                   {"data": {"status": "unsuccessful"}})

    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def first_bid_auction(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction
    response = self.app.post_json('/auctions',
                                  {"data": self.initial_data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True}})
    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']
    bids_tokens = {bid_id: bid_token}
    # create second bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True}})
    bids_tokens[response.json['data']['id']] = response.json['access']['token']
    # switch to active.auction
    self.set_status('active.auction')

    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/auctions/{}/auction'.format(auction_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    response = self.app.patch_json('/auctions/{}/auction'.format(auction_id),
                                   {
                                       'data': {
                                           'auctionUrl': 'https://auction.auction.url',
                                           'bids': [
                                               {
                                                   'id': i['id'],
                                                   'participationUrl': 'https://auction.auction.url/for_bid/{}'.format(i['id'])
                                               }
                                               for i in auction_bids_data
                                           ]
                                       }
    })
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/bids/{}?acc_token={}'.format(auction_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['participationUrl'], 'https://auction.auction.url/for_bid/{}'.format(bid_id))

    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/auctions/{}/auction'.format(auction_id),
                                  {'data': {'bids': auction_bids_data}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending.verification award
    award = [i for i in response.json['data'] if i['status'] == 'pending.verification'][0]
    award_id = award['id']
    # Upload auction protocol
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award_id, owner_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']

    response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, owner_token), {"data": {
        "description": "auction protocol",
        "documentType": 'auctionProtocol'
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
    self.assertEqual(response.json["data"]["author"], 'auction_owner')
    # set award as unsuccessful
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                                   {"data": {"status": "unsuccessful"}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award2 = [i for i in response.json['data'] if i['status'] == 'pending.verification'][0]
    award2_id = award2['id']
    self.assertNotEqual(award_id, award2_id)
    # create first award complaint
    # self.app.authorization = ('Basic', ('broker', ''))
    # response = self.app.post_json('/auctions/{}/awards/{}/complaints?acc_token={}'.format(auction_id, award_id, bid_token),
    #                               {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization, 'status': 'claim'}})
    # complaint_id = response.json['data']['id']
    # complaint_owner_token = response.json['access']['token']
    # # create first award complaint #2
    # response = self.app.post_json('/auctions/{}/awards/{}/complaints?acc_token={}'.format(auction_id, award_id, bid_token),
    #                               {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
    # # answering claim
    # self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(auction_id, award_id, complaint_id, owner_token), {"data": {
    #     "status": "answered",
    #     "resolutionType": "resolved",
    #     "resolution": "resolution text " * 2
    # }})
    # # satisfying resolution
    # self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(auction_id, award_id, complaint_id, complaint_owner_token), {"data": {
    #     "satisfied": True,
    #     "status": "resolved"
    # }})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award = [i for i in response.json['data'] if i['status'] == 'pending.verification'][0]
    award_id = award['id']
    # Upload auction protocol
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award_id, owner_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']

    response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, owner_token), {"data": {
        "description": "auction protocol",
        "documentType": 'auctionProtocol'
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
    self.assertEqual(response.json["data"]["author"], 'auction_owner')
    # set award as "pending.payment
    self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "pending.payment"}})
    # set award as active
    self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "active"}})
    # get contract id
    response = self.app.get('/auctions/{}'.format(auction_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # create auction contract document for test
    response = self.app.post('/auctions/{}/contracts/{}/documents?acc_token={}'.format(auction_id, contract_id, owner_token), upload_files=[('file', 'name.doc', 'content')], status=201)
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    auction = self.db.get(auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(auction_id, contract_id, owner_token), {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    response = self.app.post('/auctions/{}/contracts/{}/documents?acc_token={}'.format(auction_id, contract_id, owner_token), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(auction_id, contract_id, doc_id, owner_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(auction_id, contract_id, doc_id, owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")


@unittest.skipIf(not SANDBOX_MODE, 'procurementMethodDetails is absent while SANDBOX_MODE is False')
def delete_procurementMethodDetails(self):
    data = deepcopy(self.initial_data)
    data['procurementMethodDetails'] = 'some procurementMethodDetails'

    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['procurementMethodDetails'], data['procurementMethodDetails'])
    auction = response.json['data']

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json(
        '/auctions/{}'.format(auction['id']),
        {'data': {'procurementMethodDetails': None}}
    )
    self.assertNotIn('procurementMethodDetails', response.json['data'])

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertNotIn('procurementMethodDetails', response.json['data'])
