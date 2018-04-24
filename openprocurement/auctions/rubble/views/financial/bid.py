# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.bid import (
    AuctionBidResource,
)


@opresource(name='rubbleFinancial:Auction Bids',
            collection_path='/auctions/{auction_id}/bids',
            path='/auctions/{auction_id}/bids/{bid_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="Financial auction bids")
class FinancialAuctionBidResource(AuctionBidResource):
    pass
