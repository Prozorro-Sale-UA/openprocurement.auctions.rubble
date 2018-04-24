# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.rubble.views.other.question import (
    AuctionQuestionResource,
)


@opresource(name='rubbleFinancial:Auction Questions',
            collection_path='/auctions/{auction_id}/questions',
            path='/auctions/{auction_id}/questions/{question_id}',
            auctionsprocurementMethodType="rubbleFinancial",
            description="rubbleFinancial:Auction questions")
class FinancialAuctionQuestionResource(AuctionQuestionResource):
    pass
