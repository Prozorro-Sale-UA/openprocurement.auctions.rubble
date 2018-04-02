from datetime import datetime, timedelta
from openprocurement.api.constants import TZ
from openprocurement.api.models.auction_models.models import ORA_CODES


def read_json(name):
    import os.path
    from json import loads
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, name)
    with open(file_path) as lang_file:
        data = lang_file.read()
    return loads(data)

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
    "openprocurement.auctions.dgf.views.financial",
    "openprocurement.auctions.core.plugins",
]

OTHER_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.other",
    "openprocurement.auctions.core.plugins",
]
