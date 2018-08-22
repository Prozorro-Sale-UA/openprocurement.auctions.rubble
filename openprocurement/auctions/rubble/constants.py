from datetime import datetime, timedelta

from openprocurement.auctions.core.constants import TZ, ORA_CODES, read_json

# document types
DOCUMENT_TYPE_OFFLINE = ['x_dgfAssetFamiliarization']
DOCUMENT_TYPE_URL_ONLY = ['virtualDataRoom'] # requiremnt periods
MINIMAL_EXPOSITION_PERIOD = timedelta(days=6)
MINIMAL_PERIOD_FROM_RECTIFICATION_END = timedelta(days=5)
VERIFY_AUCTION_PROTOCOL_TIME = timedelta(days=6)
AWARD_PAYMENT_TIME = timedelta(days=20)
CONTRACT_SIGNING_TIME = timedelta(days=20)

# time constants
DGF_ID_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
DGF_DECISION_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
CLASSIFICATION_PRECISELY_FROM = datetime(2017, 7, 19, tzinfo=TZ)
MINIMAL_EXPOSITION_REQUIRED_FROM = datetime(2017, 11, 17, tzinfo=TZ)
DGF_ADDRESS_REQUIRED_FROM = datetime(2018, 2, 9, tzinfo=TZ)

# codes
CAVPS_CODES = read_json('cav_ps.json')
CPVS_CODES = read_json('cpvs.json')

ORA_CODES[0:0] = ["UA-IPN", "UA-FIN"]

NUMBER_OF_BIDS_TO_BE_QUALIFIED = 2

# code units
CPV_NON_SPECIFIC_LOCATION_UNITS = ('45', '48', '50', '51', '55', '60', '63', '64',
                                   '65', '66', '71', '72', '73', '75', '76', '77',
                                   '79', '80', '85', '90', '92', '98')
CAV_NON_SPECIFIC_LOCATION_UNITS = ('07', '08')

DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER = "rubbleOther"
DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL = "rubbleFinancial"

DEFAULT_LEVEL_OF_ACCREDITATION = {'create': [1],
                                  'edit': [2]}
