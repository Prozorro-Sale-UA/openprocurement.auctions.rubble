from pyramid.interfaces import IRequest
from openprocurement.auctions.dgf.models import (
    IDgfAuction,
    DGFOtherAssets,
    DGFFinancialAssets
)
from openprocurement.auctions.dgf.adapters import (
    AuctionDGFOtherAssetsConfigurator,
    AuctionDGFFinancialAssetsConfigurator
)
from openprocurement.auctions.core.plugins.awarding.v2_1.adapters import (
    AwardingNextCheckV2_1
)
from openprocurement.api.interfaces import (
    IContentConfigurator,
    IAwardingNextCheck
)


def includeme_other(config):
    config.add_auction_procurementMethodType(DGFOtherAssets)

    config.scan("openprocurement.auctions.dgf.views.other")

    # Register adapters
    config.registry.registerAdapter(
        AuctionDGFOtherAssetsConfigurator,
        (IDgfAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV2_1,
        (IDgfAuction, ),
        IAwardingNextCheck
    )


def includeme_financial(config):
    config.add_auction_procurementMethodType(DGFFinancialAssets)

    config.scan("openprocurement.auctions.dgf.views.financial")

    # Register Adapters
    config.registry.registerAdapter(
        AuctionDGFFinancialAssetsConfigurator,
        (IDgfAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV2_1,
        (IDgfAuction, ),
        IAwardingNextCheck
)