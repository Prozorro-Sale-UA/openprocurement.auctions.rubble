# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time

from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import StringType, IntType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from pyramid.security import Allow
from zope.interface import implementer

from openprocurement.auctions.core.includeme import IAwardingNextCheck
from openprocurement.auctions.core.models import (
    Administrator_role,
    Auction as BaseAuction,
    Bid as BaseBid,
    FinancialOrganization,
    IAuction,
    IsoDateTimeType,
    ListType,
    Lot,
    Period,
    auction_embedded_role,
    calc_auction_end_time,
    dgfCDB2Complaint,
    dgfCDB2Document,
    dgfCDB2Item,
    dgfCancellation,
    edit_role,
    get_auction,
    validate_items_uniq,
    validate_lots_uniq,
    validate_not_available,
)
from openprocurement.auctions.core.plugins.awarding.v2_1.models import Award
from openprocurement.auctions.core.plugins.contracting.v2_1.models import Contract
from openprocurement.auctions.core.utils import (
    AUCTIONS_COMPLAINT_STAND_STILL_TIME as COMPLAINT_STAND_STILL_TIME,
    SANDBOX_MODE,
    TZ,
    calculate_business_date,
    get_auction_creation_date,
    get_now,
    get_request_from_root,
    generate_rectificationPeriod_tender_period_margin,
)

from .constants import (
    DGF_ID_REQUIRED_FROM,
    MINIMAL_EXPOSITION_PERIOD,
    MINIMAL_EXPOSITION_REQUIRED_FROM,
    MINIMAL_PERIOD_FROM_RECTIFICATION_END
)


def bids_validation_wrapper(validation_func):
    def validator(klass, data, value):
        orig_data = data
        while not isinstance(data['__parent__'], BaseAuction):
            # in case this validation wrapper is used for subelement of bid (such as parameters)
            # traverse back to the bid to get possibility to check status  # troo-to-to =)
            data = data['__parent__']
        if data['status'] in ('invalid', 'draft'):
            # skip not valid bids
            return
        tender = data['__parent__']
        request = tender.__parent__.request
        if request.method == "PATCH" and isinstance(tender, BaseAuction) and request.authenticated_role == "auction_owner":
            # disable bids validation on tender PATCH requests as tender bids will be invalidated
            return
        return validation_func(klass, orig_data, value)
    return validator


class Bid(BaseBid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified'),
        }

    status = StringType(choices=['active', 'draft', 'invalid'], default='active')
    documents = ListType(ModelType(dgfCDB2Document), default=list())
    qualified = BooleanType(required=True, choices=[True])

    @bids_validation_wrapper
    def validate_value(self, data, value):
        BaseBid._validator_functions['value'](self, data, value)


class Cancellation(dgfCancellation):
    documents = ListType(ModelType(dgfCDB2Document), default=list())


def rounding_shouldStartAfter(start_after, auction, use_from=datetime(2016, 6, 1, tzinfo=TZ)):
    if (auction.enquiryPeriod and auction.enquiryPeriod.startDate or get_now()) > use_from and not (SANDBOX_MODE and auction.submissionMethodDetails and u'quick' in auction.submissionMethodDetails):
        midnigth = datetime.combine(start_after.date(), time(0, tzinfo=start_after.tzinfo))
        if start_after >= midnigth:
            start_after = midnigth + timedelta(1)
    return start_after


class AuctionAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        auction = self.__parent__
        if auction.lots or auction.status not in ['active.tendering', 'active.auction']:
            return
        if self.startDate and get_now() > calc_auction_end_time(auction.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(auction.numberOfBids, self.startDate)
        elif auction.tenderPeriod and auction.tenderPeriod.endDate:
            start_after = auction.tenderPeriod.endDate
        else:
            return
        return rounding_shouldStartAfter(start_after, auction).isoformat()

    def validate_startDate(self, data, startDate):
        auction = get_auction(data['__parent__'])
        if not auction.revisions and not startDate:
            raise ValidationError(u'This field is required.')


class RectificationPeriod(Period):
    invalidationDate = IsoDateTimeType()


create_role = (blacklist(
    '_attachments',
    'auctionID',
    'auctionUrl',
    'awardCriteria',
    'awardPeriod',
    'awards',
    'bids',
    'cancellations',
    'complaints',
    'contracts',
    'date',
    'dateModified',
    'doc_id',
    'documents',
    'eligibilityCriteria',
    'eligibilityCriteria_en',
    'eligibilityCriteria_ru',
    'enquiryPeriod',
    'numberOfBidders',
    'owner',
    'procurementMethod',
    'questions',
    'revisions',
    'status',
    'submissionMethod',
    'tenderPeriod'
) + auction_embedded_role)

edit_role = (edit_role + blacklist('enquiryPeriod', 'tenderPeriod', 'auction_value', 'auction_minimalStep', 'auction_guarantee', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru', 'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru', 'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru', 'minNumberOfQualifiedBids'))
Administrator_role = (Administrator_role + whitelist('awards'))


class IRubbleOtherAuction(IAuction):
    """Marker interface for RubbleOther auctions"""


class IRubbleFinancialAuction(IAuction):
    """Marker interface for RubbleFinancial auctions"""


@implementer(IRubbleOtherAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = {
            'create': create_role,
            'edit_active.tendering': (blacklist('enquiryPeriod', 'tenderPeriod', 'rectificationPeriod', 'auction_value', 'auction_minimalStep', 'auction_guarantee', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'minNumberOfQualifiedBids') + edit_role),
            'Administrator': (whitelist('rectificationPeriod') + Administrator_role),
        }

    def __local_roles__(self):
        roles = dict([('{}_{}'.format(self.owner, self.owner_token), 'auction_owner')])
        for i in self.bids:
            roles['{}_{}'.format(i.owner, i.owner_token)] = 'bid_owner'
        return roles

    _internal_type = "rubbleOther"
    awards = ListType(ModelType(Award), default=list())
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ModelType(dgfCDB2Complaint), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    dgfID = StringType()
    documents = ListType(ModelType(dgfCDB2Document), default=list())  # All documents and attachments related to the auction.
    enquiryPeriod = ModelType(Period)  # The period during which enquiries may be made and will be answered.
    rectificationPeriod = ModelType(RectificationPeriod)  # The period during which editing of main procedure fields are allowed
    tenderPeriod = ModelType(Period)  # The period when the auction is open for submissions. The end date is the closing date for auction submissions.
    tenderAttempts = IntType(choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    auctionPeriod = ModelType(AuctionAuctionPeriod, required=True, default={})
    procurementMethodType = StringType()
    status = StringType(choices=['draft', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq, validate_not_available])
    items = ListType(ModelType(dgfCDB2Item), required=True, min_size=1, validators=[validate_items_uniq])
    minNumberOfQualifiedBids = IntType(choices=[1, 2])

    def __acl__(self):
        return [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction_award'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_auction_documents'),
        ]

    def initialize(self):
        if not self.enquiryPeriod:
            self.enquiryPeriod = type(self).enquiryPeriod.model_class()
        if not self.tenderPeriod:
            self.tenderPeriod = type(self).tenderPeriod.model_class()
        now = get_now()
        start_date = TZ.localize(self.auctionPeriod.startDate.replace(tzinfo=None))
        self.tenderPeriod.startDate = self.enquiryPeriod.startDate = now
        pause_between_periods = start_date - (start_date.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(days=1))
        end_date = calculate_business_date(start_date, -pause_between_periods, self)
        self.enquiryPeriod.endDate = end_date
        self.tenderPeriod.endDate = self.enquiryPeriod.endDate
        if not self.rectificationPeriod:
            self.rectificationPeriod = generate_rectificationPeriod_tender_period_margin(self)
        self.rectificationPeriod.startDate = now
        self.auctionPeriod.startDate = None
        self.auctionPeriod.endDate = None
        self.date = now
        if self.lots:
            for lot in self.lots:
                lot.date = now

    def validate_tenderPeriod(self, data, period):
        """Auction start date must be not closer than MINIMAL_EXPOSITION_PERIOD days and not a holiday"""
        if not (period and period.startDate and period.endDate):
            return
        if get_auction_creation_date(data) < MINIMAL_EXPOSITION_REQUIRED_FROM:
            return
        if calculate_business_date(period.startDate, MINIMAL_EXPOSITION_PERIOD, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than 6 days")

    def validate_rectificationPeriod(self, data, period):
        if not (period and period.startDate) or not period.endDate:
            return
        if period.endDate > calculate_business_date(data['tenderPeriod']['endDate'], -MINIMAL_PERIOD_FROM_RECTIFICATION_END, data).astimezone(getattr(period.endDate, 'tzinfo', TZ)):
            raise ValidationError(u"rectificationPeriod.endDate should come at least 5 working days earlier than tenderPeriod.endDate")

    def validate_value(self, data, value):
        if value.currency != u'UAH':
            raise ValidationError(u"currency should be only UAH")

    def validate_dgfID(self, data, dgfID):
        if not dgfID:
            if get_auction_creation_date(data) > DGF_ID_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod and self.tenderPeriod.endDate:
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.auction' and self.auctionPeriod and self.auctionPeriod.startDate and not self.auctionPeriod.endDate:
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            elif now < calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ))
        elif self.lots and self.status == 'active.auction':
            for lot in self.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ))
        # Use next_check part from awarding
        request = get_request_from_root(self)
        if request is not None:
            awarding_check = request.registry.getAdapter(self, IAwardingNextCheck).add_awarding_checks(self)
            if awarding_check is not None:
                checks.append(awarding_check)
        if self.status.startswith('active'):
            from openprocurement.auctions.core.utils import calculate_business_date
            for complaint in self.complaints:
                if complaint.status == 'claim' and complaint.dateSubmitted:
                    checks.append(calculate_business_date(complaint.dateSubmitted, COMPLAINT_STAND_STILL_TIME, self))
                elif complaint.status == 'answered' and complaint.dateAnswered:
                    checks.append(calculate_business_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self))
            for award in self.awards:
                for complaint in award.complaints:
                    if complaint.status == 'claim' and complaint.dateSubmitted:
                        checks.append(calculate_business_date(complaint.dateSubmitted, COMPLAINT_STAND_STILL_TIME, self))
                    elif complaint.status == 'answered' and complaint.dateAnswered:
                        checks.append(calculate_business_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self))
        return min(checks).isoformat() if checks else None


RubbleOther = Auction

# Rubble Financial models


class dgfFinCDB2Document(dgfCDB2Document):
    documentType = StringType(choices=[
        'auctionNotice', 'awardNotice', 'contractNotice',
        'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms',
        'riskProvisions', 'billOfQuantity', 'bidders', 'conflictOfInterest',
        'debarments', 'evaluationReports', 'winningBid', 'complaints',
        'contractSigned', 'contractArrangements', 'contractSchedule',
        'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal',
        'qualificationDocuments', 'eligibilityDocuments', 'tenderNotice',
        'illustration', 'financialLicense', 'virtualDataRoom',
        'auctionProtocol', 'x_dgfAssetFamiliarization',
        'x_presentation', 'x_nda',
    ])

dgfFinCDB2Document.__name__ = 'Document'


class Bid(Bid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified', 'eligible'),
        }
    documents = ListType(ModelType(dgfFinCDB2Document), default=list())
    tenderers = ListType(ModelType(FinancialOrganization), required=True, min_size=1, max_size=1)
    eligible = BooleanType(required=True, choices=[True])


@implementer(IRubbleFinancialAuction)
class Auction(RubbleOther):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    _internal_type = "rubbleFinancial"
    documents = ListType(ModelType(dgfFinCDB2Document), default=list())  # All documents and attachments related to the auction.
    bids = ListType(ModelType(Bid), default=list())
    procurementMethodType = StringType()
    eligibilityCriteria = StringType(default=u"До участі допускаються лише ліцензовані фінансові установи.")
    eligibilityCriteria_en = StringType(default=u"Only licensed financial institutions are eligible to participate.")
    eligibilityCriteria_ru = StringType(default=u"К участию допускаются только лицензированные финансовые учреждения.")


RubbleFinancial = Auction
