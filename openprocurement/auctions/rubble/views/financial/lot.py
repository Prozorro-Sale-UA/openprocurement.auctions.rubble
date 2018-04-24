# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.lot import (
    AuctionLotResource,
)


@opresource(name='rubbleFinancial:Auction Lots',
            collection_path='/auctions/{auction_id}/lots',
            path='/auctions/{auction_id}/lots/{lot_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="Financial auction lots")
class FinancialAuctionLotResource(AuctionLotResource):
    pass
