# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler

def validate_change_price_criteria_reduction_by_administrator(request):
    """
        Validate value, minimalStep, guarantee change
        Value only decrease for not more that 50%
        minimalStep, guarantee only decrease
    """
    if request.authenticated_role == 'Administrator' and request.context.status == 'active.tendering':
        new_value = request.validated['data'].get('value').get('amount')
        new_minimalStep = request.validated['data'].get('minimalStep').get('amount')
        if not request.context.value.amount * 0.5 <= new_value <= request.context.value.amount:
            request.errors.add('body', 'data', 'Only value reduction for not more than 50% is allowed')
        if request.context.minimalStep.amount < new_minimalStep:
            request.errors.add('body', 'data', 'Only reducing minimalStep is allowed')
        if request.context.guarantee and request.context.guarantee.amount < request.validated['data'].get('guarantee').get('amount'):
            request.errors.add('body', 'data', 'Only reducing guarantee is allowed')
        if request.errors:
            request.errors.status = 403
            raise error_handler(request.errors)