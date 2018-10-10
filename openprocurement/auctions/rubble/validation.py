# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    TZ,
    error_handler,
    generate_rectificationPeriod_tender_period_margin,
    get_now,
)


def validate_rectification_period_editing(request, **kwargs):
    if (
        request.context.status == 'active.tendering'
        and request.authenticated_role
        not in ['chronograph', 'Administrator']
    ):
        auction = request.validated['auction']
        rectificationPeriod = auction.rectificationPeriod or generate_rectificationPeriod_tender_period_margin(auction)
        if rectificationPeriod.endDate.astimezone(TZ) < get_now():
            request.errors.add(
                'body',
                'data',
                'Auction can be edited only during the rectification period: from ({}) to ({}).'.format(
                    rectificationPeriod.startDate.isoformat(),
                    rectificationPeriod.endDate.isoformat()
                )
            )
            request.errors.status = 403
            raise error_handler(request)
