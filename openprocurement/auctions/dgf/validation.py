# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler
from openprocurement.api.utils import get_now
from openprocurement.auctions.dgf.utils import generate_rectificationPeriod
from openprocurement.api.constants import TZ


def validate_rectification_period_editing(request, **kwargs):
    if request.context.status == 'active.tendering' and request.authenticated_role not in ['chronograph', 'Administrator']:
        auction = request.validated['auction']
        rectificationPeriod = auction.rectificationPeriod or generate_rectificationPeriod(auction)
        if rectificationPeriod.endDate.astimezone(TZ) < get_now():
            request.errors.add('body', 'data', 'Auction can be edited only during the rectification period: from ({}) to ({}).'.format(rectificationPeriod.startDate.isoformat(), rectificationPeriod.endDate.isoformat()))
            request.errors.status = 403
            raise error_handler(request)
