# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import AuctionConfigurator
from openprocurement.auctions.rubble.models import (
    RubbleOther,
    RubbleFinancial
)
from openprocurement.auctions.core.plugins.awarding.v2_1.adapters import (
    AwardingV2_1ConfiguratorMixin
)


class AuctionRubbleOtherConfigurator(AuctionConfigurator,
                                     AwardingV2_1ConfiguratorMixin):
    name = 'Auction Rubble Configurator'
    model = RubbleOther


class AuctionRubbleFinancialConfigurator(AuctionConfigurator,
                                         AwardingV2_1ConfiguratorMixin):
    name = 'Auction Rubble Configurator'
    model = RubbleFinancial
