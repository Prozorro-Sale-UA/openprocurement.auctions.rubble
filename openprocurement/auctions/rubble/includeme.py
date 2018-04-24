import logging

from pyramid.interfaces import IRequest

from openprocurement.auctions.core.includeme import (
    IContentConfigurator,
    IAwardingNextCheck
)
from openprocurement.auctions.core.plugins.awarding.v2_1.adapters import (
    AwardingNextCheckV2_1
)

from openprocurement.auctions.rubble.adapters import (
    AuctionRubbleOtherConfigurator,
    AuctionRubbleFinancialConfigurator
)
from openprocurement.auctions.rubble.constants import (
    DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER,
    DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL
)
from openprocurement.auctions.rubble.models import (
    IRubbleAuction,
    RubbleOther,
    RubbleFinancial
)

LOGGER = logging.getLogger(__name__)


def includeme_other(config, plugin_config=None):
    procurement_method_types = plugin_config.get('aliases', [])
    if plugin_config.get('use_default', False):
        procurement_method_types.append(
            DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER
        )
    for procurementMethodType in procurement_method_types:
        config.add_auction_procurementMethodType(RubbleOther,
                                                 procurementMethodType)

    config.scan("openprocurement.auctions.rubble.views.other")

    # Register adapters
    config.registry.registerAdapter(
        AuctionRubbleOtherConfigurator,
        (IRubbleAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV2_1,
        (IRubbleAuction,),
        IAwardingNextCheck
    )

    LOGGER.info("Included openprocurement.auctions.rubble.other plugin",
                extra={'MESSAGE_ID': 'included_plugin'})


def includeme_financial(config, plugin_config=None):
    procurement_method_types = plugin_config.get('aliases', [])
    if plugin_config.get('use_default', False):
        procurement_method_types.append(
            DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL
        )
    for procurementMethodType in procurement_method_types:
        config.add_auction_procurementMethodType(RubbleFinancial,
                                                 procurementMethodType)

    config.scan("openprocurement.auctions.rubble.views.financial")

    # Register Adapters
    config.registry.registerAdapter(
        AuctionRubbleFinancialConfigurator,
        (IRubbleAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV2_1,
        (IRubbleAuction,),
        IAwardingNextCheck
    )

    LOGGER.info("Included openprocurement.auctions.rubble.other plugin",
                extra={'MESSAGE_ID': 'included_plugin'})
