# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time
from schematics.types import StringType, URLType, IntType, BaseType, BooleanType
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types.serializable import serializable
from urlparse import urlparse, parse_qs
from string import hexdigits
from zope.interface import implementer
from pyramid.security import Allow

from openprocurement.api.models.auction_models.models import (
    Feature, get_now,
    validate_features_uniq, validate_lots_uniq, Identifier as BaseIdentifier,
    Classification, validate_items_uniq, Address, Location,
    schematics_embedded_role, IsoDateTimeType
)
from openprocurement.api.models.schematics_extender import ListType
from openprocurement.api.models.models import Period
from openprocurement.api.utils import calculate_business_date, get_request_from_root
from openprocurement.api.interfaces import IAwardingNextCheck
from openprocurement.api.constants import SANDBOX_MODE, CPV_CODES, ORA_CODES, TZ, AUCTIONS_COMPLAINT_STAND_STILL_TIME as COMPLAINT_STAND_STILL_TIME

from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.flash.models import (
    Auction as BaseAuction, Bid as BaseBid,
    Cancellation as BaseCancellation,
    Lot,
    ProcuringEntity as BaseProcuringEntity, Question as BaseQuestion,
    get_auction
)


from openprocurement.auctions.core.models import (
    IAuction,
    calc_auction_end_time,
    edit_role,
    Administrator_role,
    dgfCDB2Document as Document,
    dgfCDB2Item as Item,
    dgfOrganization as Organization,
    dgfCDB2Complaint as Complaint,
    Identifier
)

from openprocurement.auctions.core.plugins.awarding.v2_1.models import Award
from openprocurement.auctions.core.plugins.contracting.v2_1.models import Contract

from .utils import calculate_enddate, get_auction_creation_date, generate_rectificationPeriod

from .constants import (
    DOCUMENT_TYPE_OFFLINE,
    DOCUMENT_TYPE_URL_ONLY,
    DGF_ID_REQUIRED_FROM,
    ORA_CODES, MINIMAL_EXPOSITION_PERIOD,
    MINIMAL_EXPOSITION_REQUIRED_FROM,
    MINIMAL_PERIOD_FROM_RECTIFICATION_END
)


def read_json(name):
    import os.path
    from json import loads
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, name)
    with open(file_path) as lang_file:
        data = lang_file.read()
    return loads(data)

  
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


class ProcuringEntity(BaseProcuringEntity):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))


class Bid(BaseBid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified'),
        }

    status = StringType(choices=['active', 'draft', 'invalid'], default='active')
    tenderers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)
    documents = ListType(ModelType(Document), default=list())
    qualified = BooleanType(required=True, choices=[True])

    @bids_validation_wrapper
    def validate_value(self, data, value):
        BaseBid._validator_functions['value'](self, data, value)

class Question(BaseQuestion):
    author = ModelType(Organization, required=True)


class Cancellation(BaseCancellation):
    documents = ListType(ModelType(Document), default=list())


def validate_not_available(items, *args):
    if items:
        raise ValidationError(u"Option not available in this procurementMethodType")


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


create_role = (blacklist('owner_token', 'owner', '_attachments', 'revisions', 'date', 'dateModified', 'doc_id', 'auctionID', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'status', 'enquiryPeriod', 'tenderPeriod', 'awardPeriod', 'procurementMethod', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteria', 'submissionMethod', 'cancellations', 'numberOfBidders', 'contracts') + schematics_embedded_role)
edit_role = (edit_role + blacklist('enquiryPeriod', 'tenderPeriod', 'auction_value', 'auction_minimalStep', 'auction_guarantee', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru', 'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru', 'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru', 'minNumberOfQualifiedBids'))
Administrator_role = (Administrator_role + whitelist('awards'))



class IDgfAuction(IAuction):
    """Marker interface for Dgf auctions"""


@implementer(IDgfAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = {
            'create': create_role,
            'edit_active.tendering': (blacklist('enquiryPeriod', 'tenderPeriod', 'rectificationPeriod', 'auction_value', 'auction_minimalStep', 'auction_guarantee', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'minNumberOfQualifiedBids') + edit_role),
            'Administrator': (whitelist('rectificationPeriod') + Administrator_role),
        }

    awards = ListType(ModelType(Award), default=list())
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    dgfID = StringType()
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    enquiryPeriod = ModelType(Period)  # The period during which enquiries may be made and will be answered.
    rectificationPeriod = ModelType(RectificationPeriod)  # The period during which editing of main procedure fields are allowed
    tenderPeriod = ModelType(Period)  # The period when the auction is open for submissions. The end date is the closing date for auction submissions.
    tenderAttempts = IntType(choices=[1, 2, 3, 4])
    auctionPeriod = ModelType(AuctionAuctionPeriod, required=True, default={})
    procurementMethodType = StringType(default="dgfOtherAssets")
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=['draft', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    questions = ListType(ModelType(Question), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq, validate_not_available])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq, validate_not_available])
    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_items_uniq])
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
        self.tenderPeriod.startDate = self.enquiryPeriod.startDate = now
        pause_between_periods = self.auctionPeriod.startDate - (self.auctionPeriod.startDate.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(days=1))
        self.tenderPeriod.endDate = self.enquiryPeriod.endDate = calculate_business_date(self.auctionPeriod.startDate, -pause_between_periods, self)
        if not self.rectificationPeriod:
            self.rectificationPeriod = generate_rectificationPeriod(self)
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
        if period.endDate > TZ.localize(calculate_business_date(data['tenderPeriod']['endDate'], -MINIMAL_PERIOD_FROM_RECTIFICATION_END, data).replace(tzinfo=None)):
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
            from openprocurement.api.utils import calculate_business_date
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


DGFOtherAssets = Auction

# DGF Financial Assets models


def validate_ua_fin(items, *args):
    if items and not any([i.scheme == u"UA-FIN" for i in items]):
        raise ValidationError(u"One of additional classifications should be UA-FIN.")


class FinantialOrganization(Organization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier), required=True, validators=[validate_ua_fin])


class Document(Document):
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


class Bid(Bid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified', 'eligible'),
        }
    documents = ListType(ModelType(Document), default=list())
    tenderers = ListType(ModelType(FinantialOrganization), required=True, min_size=1, max_size=1)
    eligible = BooleanType(required=True, choices=[True])


@implementer(IAuction)
class Auction(DGFOtherAssets):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    bids = ListType(ModelType(Bid), default=list())
    procurementMethodType = StringType(default="dgfFinancialAssets")
    eligibilityCriteria = StringType(default=u"До участі допускаються лише ліцензовані фінансові установи.")
    eligibilityCriteria_en = StringType(default=u"Only licensed financial institutions are eligible to participate.")
    eligibilityCriteria_ru = StringType(default=u"К участию допускаются только лицензированные финансовые учреждения.")


DGFFinancialAssets = Auction
