# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler
from openprocurement.api.models import get_now, TZ


def validate_change_price_criteria_reduction(request):
    """
        Validate value, minimalStep, guarantee change
        Value only decrease for not more that 50%
        minimalStep, guarantee only decrease
    """
    if request.context.status == 'active.tendering':
        for key in request.json['data']:
            if key in ['value', 'minimalStep', 'guarantee']:
                new_amount = request.json['data'][key].get('amount')

                if any([request.validated['data'][key][i] != request.context[key][i] for i in request.validated['data'][key] if i != 'amount']):
                    request.errors.add('body', 'data', 'Only amount change is allowed')

                elif key == 'value' and not request.context.value.amount * 0.5 <= new_amount <= request.context.value.amount:
                    request.errors.add('body', 'data', 'Only value reduction for not more than 50% is allowed')

                elif request.context[key].amount < new_amount:
                    request.errors.add('body', 'data', 'Only reducing {} is allowed'.format(key))

        if request.errors:
            request.errors.status = 403
            raise error_handler(request.errors)

def validate_enquiry_period_editing(request):
    if request.context.status == 'active.tendering' and request.authenticated_role not in ['chronograph', 'Administrator']:
        auction = request.validated['auction']
        if auction.enquiryPeriod.endDate.astimezone(TZ) < get_now():
            request.errors.add('body', 'data', 'Auction can be edited only during the enquiry period: from ({}) to ({}).'.format(auction.enquiryPeriod.startDate and auction.enquiryPeriod.startDate.isoformat(), auction.enquiryPeriod.endDate.isoformat()))
            request.errors.status = 403
            raise error_handler(request.errors)
