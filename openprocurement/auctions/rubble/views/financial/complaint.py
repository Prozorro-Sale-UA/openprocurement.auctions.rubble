# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.complaint import (
    AuctionComplaintResource,
)


@opresource(name='rubbleFinancial:Auction Complaints',
            collection_path='/auctions/{auction_id}/complaints',
            path='/auctions/{auction_id}/complaints/{complaint_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="Financial auction complaints")
class FinancialAuctionComplaintResource(AuctionComplaintResource):
    pass
