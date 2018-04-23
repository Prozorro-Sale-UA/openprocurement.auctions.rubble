# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.cancellation_document import (
    AuctionCancellationDocumentResource,
)


@opresource(name='rubbleFinancial:Auction Cancellation Documents',
            collection_path='/auctions/{auction_id}/cancellations/{cancellation_id}/documents',
            path='/auctions/{auction_id}/cancellations/{cancellation_id}/documents/{document_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="Financial auction cancellation documents")
class FinancialAuctionCancellationDocumentResource(AuctionCancellationDocumentResource):
    pass
