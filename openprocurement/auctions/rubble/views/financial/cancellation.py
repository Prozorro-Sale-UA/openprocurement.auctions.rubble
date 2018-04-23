# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.cancellation import (
    AuctionCancellationResource,
)


@opresource(name='rubbleFinancial:Auction Cancellations',
            collection_path='/auctions/{auction_id}/cancellations',
            path='/auctions/{auction_id}/cancellations/{cancellation_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="Financial auction cancellations")
class FinancialAuctionCancellationResource(AuctionCancellationResource):
    pass
