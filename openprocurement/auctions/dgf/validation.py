# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler
from openprocurement.api.models import get_now, TZ


def validate_rectification_period_editing(request):
    if request.context.status == 'active.tendering' and request.authenticated_role not in ['chronograph', 'Administrator']:
        auction = request.validated['auction']
        if auction.rectificationPeriod.endDate.astimezone(TZ) < get_now():
            request.errors.add('body', 'data', 'Auction can be edited only during the rectification period: from ({}) to ({}).'.format(auction.rectificationPeriod.startDate.isoformat(), auction.rectificationPeriod.endDate.isoformat()))
            request.errors.status = 403
            raise error_handler(request.errors)
