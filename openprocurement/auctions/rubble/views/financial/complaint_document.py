# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.complaint_document import (
    AuctionComplaintDocumentResource,
)


@opresource(name='rubbleFinancial:Auction Complaint Documents',
            collection_path='/auctions/{auction_id}/complaints/{complaint_id}/documents',
            path='/auctions/{auction_id}/complaints/{complaint_id}/documents/{document_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="Financial auction complaint documents")
class FinancialComplaintDocumentResource(AuctionComplaintDocumentResource):
    pass
