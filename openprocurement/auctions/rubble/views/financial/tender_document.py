# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.tender_document import (
    AuctionDocumentResource,
)


@opresource(name='rubbleFinancial:Auction Documents',
            collection_path='/auctions/{auction_id}/documents',
            path='/auctions/{auction_id}/documents/{document_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="Financial auction related binary files (PDFs, etc.)")
class FinancialAuctionDocumentResource(AuctionDocumentResource):
    pass
