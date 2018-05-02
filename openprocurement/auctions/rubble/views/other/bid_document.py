# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import get_now, opresource
from openprocurement.auctions.core.views.mixins import AuctionBidDocumentResource


@opresource(name='rubbleOther:Auction Bid Documents',
            collection_path='/auctions/{auction_id}/bids/{bid_id}/documents',
            path='/auctions/{auction_id}/bids/{bid_id}/documents/{document_id}',
            auctionsprocurementMethodType="rubbleOther",
            description="Auction bidder documents")
class AuctionBidDocumentResource(AuctionBidDocumentResource):

    def validate_bid_document(self, operation):
        auction = self.request.validated['auction']
        if auction.status not in ['active.tendering', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) auction status'.format(operation, auction.status))
            self.request.errors.status = 403
            return
        if auction.status == 'active.tendering' and not (auction.tenderPeriod.startDate < get_now() < auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be {} only during the tendering period: from ({}) to ({}).'.format('added' if operation == 'add' else 'updated', auction.tenderPeriod.startDate.isoformat(), auction.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if auction.status == 'active.qualification' and not [i for i in auction.awards if 'pending' in i.status and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t {} document because award of bid is not in pending state'.format(operation))
            self.request.errors.status = 403
            return
        return True
