from datetime import datetime, timedelta

from openprocurement.auctions.core.models import ORA_CODES
from openprocurement.auctions.core.utils import TZ


#document types
DOCUMENT_TYPE_OFFLINE = ['x_dgfAssetFamiliarization']
DOCUMENT_TYPE_URL_ONLY = ['virtualDataRoom']

#requiremnt periods
MINIMAL_EXPOSITION_PERIOD = timedelta(days=6)
MINIMAL_PERIOD_FROM_RECTIFICATION_END = timedelta(days=5)
VERIFY_AUCTION_PROTOCOL_TIME = timedelta(days=6)
AWARD_PAYMENT_TIME = timedelta(days=20)
CONTRACT_SIGNING_TIME = timedelta(days=20)

#time constants
DGF_ID_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
DGF_DECISION_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
MINIMAL_EXPOSITION_REQUIRED_FROM = datetime(2017, 11, 17, tzinfo=TZ)

DGF_ADDRESS_REQUIRED_FROM = datetime(2020, 2, 8, tzinfo=TZ)

ORA_CODES[0:0] = ["UA-IPN", "UA-FIN"]

NUMBER_OF_BIDS_TO_BE_QUALIFIED = 2

#Views location

FINANCIAL_VIEW_LOCATIONS = [
    "openprocurement.auctions.rubble.views.financial",
    "openprocurement.auctions.core.plugins",
]

OTHER_VIEW_LOCATIONS = [
    "openprocurement.auctions.rubble.views.other",
    "openprocurement.auctions.core.plugins",
]

DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER = "exampleRubbleOther"
DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL = "exampleRubbleFinancial"
