# -*- coding: utf-8 -*-
from logging import getLogger

from pkg_resources import get_distribution

from openprocurement.auctions.core.utils import (
    check_complaint_status, check_auction_status, remove_draft_bids,
    upload_file as base_upload_file, get_file as base_get_file,
    API_DOCUMENT_BLACKLISTED_FIELDS as DOCUMENT_BLACKLISTED_FIELDS,
    context_unpack, calculate_business_date, get_now, TZ
)

from .constants import (
    DOCUMENT_TYPE_URL_ONLY,
    DOCUMENT_TYPE_OFFLINE,
    MINIMAL_PERIOD_FROM_RECTIFICATION_END
)


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def upload_file(request, blacklisted_fields=DOCUMENT_BLACKLISTED_FIELDS):
    first_document = request.validated['documents'][0] if 'documents' in request.validated and request.validated['documents'] else None
    if 'data' in request.validated and request.validated['data']:
        document = request.validated['document']
        if document.documentType in (DOCUMENT_TYPE_URL_ONLY + DOCUMENT_TYPE_OFFLINE):
            if first_document:
                for attr_name in type(first_document)._fields:
                    if attr_name not in blacklisted_fields:
                        setattr(document, attr_name, getattr(first_document, attr_name))
            if document.documentType in DOCUMENT_TYPE_OFFLINE:
                document.format = 'offline/on-site-examination'
            return document
    return base_upload_file(request, blacklisted_fields)


def get_file(request):
    document = request.validated['document']
    if document.documentType == 'virtualDataRoom':
        request.response.status = '302 Moved Temporarily'
        request.response.location = document.url
        return document.url
    return base_get_file(request)


def check_bids(request):
    auction = request.validated['auction']
    if auction.auctionPeriod:
        if auction.numberOfBids < (auction.minNumberOfQualifiedBids or 2):
            auction.auctionPeriod.startDate = None
            auction.status = 'unsuccessful'
        elif auction.numberOfBids == 1:
            auction.auctionPeriod.startDate = None
            request.content_configurator.start_awarding()


def check_auction_protocol(award):
    if award.documents:
        for document in award.documents:
            if document['documentType'] == 'auctionProtocol' and document['author'] == 'auction_owner':
                return True
    return False


def check_status(request):
    auction = request.validated['auction']
    now = get_now()
    for complaint in auction.complaints:
        check_complaint_status(request, complaint, now)
    for award in auction.awards:
        for complaint in award.complaints:
            check_complaint_status(request, complaint, now)
    if not auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        remove_invalid_bids(request)
        check_bids(request)
        return
    elif auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        remove_invalid_bids(request)
        check_bids(request)
        [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return
    elif not auction.lots and auction.status == 'active.awarded':
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        if not standStillEnds:
            return
        standStillEnd = max(standStillEnds)
        if standStillEnd <= now:
            check_auction_status(request)
    elif auction.lots and auction.status in ['active.qualification', 'active.awarded']:
        if any([i['status'] in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints]):
            return
        for lot in auction.lots:
            if lot['status'] != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod.endDate
            ]
            if not standStillEnds:
                continue
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                check_auction_status(request)
                return


def calculate_enddate(auction, period, duration):
    period.endDate = calculate_business_date(period.startDate, duration, auction, True)
    round_to_18_hour_delta = period.endDate.replace(hour=18, minute=0, second=0) - period.endDate
    period.endDate = calculate_business_date(period.endDate, round_to_18_hour_delta, auction, False)


def invalidate_bids_under_threshold(auction):
    """Invalidate bids that lower value.amount + minimalStep.amount"""
    value_threshold = round(auction['value']['amount'] +
                            auction['minimalStep']['amount'], 2)
    for bid in auction['bids']:
        if bid['value']['amount'] < value_threshold:
            bid['status'] = 'invalid'


def get_auction_creation_date(data):
    auction_creation_date = (data.get('revisions')[0].date if data.get('revisions') else get_now())
    return auction_creation_date


def remove_invalid_bids(request):
    auction = request.validated['auction']
    if [bid for bid in auction.bids if getattr(bid, "status", "active") == "invalid"]:
        LOGGER.info('Remove invalid bids',
                    extra=context_unpack(request, {'MESSAGE_ID': 'remove_invalid_bids'}))
        auction.bids = [bid for bid in auction.bids if getattr(bid, "status", "active") != "invalid"]


def invalidate_bids_data(auction):
    for bid in auction.bids:
        setattr(bid, "status", "invalid")
    auction.rectificationPeriod.invalidationDate = get_now()


def generate_rectificationPeriod(auction):
    now = get_now()
    if not auction.rectificationPeriod:
        period = type(auction).rectificationPeriod.model_class()
    period.startDate = period.startDate or now
    if not period.endDate:
        calculated_endDate = calculate_business_date(auction.tenderPeriod.endDate, -MINIMAL_PERIOD_FROM_RECTIFICATION_END, auction)
        period.endDate = calculated_endDate if calculated_endDate > now else now
    period.invalidationDate = None
    return period
