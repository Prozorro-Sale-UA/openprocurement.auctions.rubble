# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import AuctionConfigurator
from openprocurement.auctions.dgf.models import (
    DGFOtherAssets,
    DGFFinancialAssets
)
from openprocurement.auctions.core.plugins.awarding.v2_1.adapters import (
    AwardingV2_1ConfiguratorMixin
)


class AuctionDGFOtherAssetsConfigurator(AuctionConfigurator,
                                        AwardingV2_1ConfiguratorMixin):
    name = 'Auction Dgf Configurator'
    model = DGFOtherAssets


class AuctionDGFFinancialAssetsConfigurator(AuctionConfigurator,
                                            AwardingV2_1ConfiguratorMixin):
    name = 'Auction Dgf Configurator'
    model = DGFFinancialAssets