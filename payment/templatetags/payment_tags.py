from django import template

from partnership.models import Deal, Partnership
from payment.models import Currency

register = template.Library()


@register.inclusion_tag('payment/partials/create_payment.html')
def create_payment_form(purpose=None):
    currencies = Currency.objects.all()

    ctx = {
        'currencies': currencies,
        'purpose': purpose,
    }
    return ctx


@register.inclusion_tag('payment/partials/update_payment.html', takes_context=True)
def update_payment_form(context, purpose=None):
    currencies = Currency.objects.all()
    request = context.get('request', None)

    ctx = {
        'currencies': currencies,
        'purpose': purpose,
        'user': request.user
    }
    return ctx


@register.inclusion_tag('payment/partials/payment_table.html')
def payment_table(payments, can_edit=False):

    ctx = {
        'can_edit': can_edit,
        'payments': payments,
    }
    return ctx


@register.simple_tag(takes_context=True)
def can_i_edit_payment(context, purpose):
    request = context.get('request', None)
    if request is None:
        return False
    user = request.user
    if not user.is_authenticated:
        return False
    if isinstance(purpose, Deal):
        deal = purpose
        return deal.can_user_edit_payment(user)
    if isinstance(purpose, Partnership):
        partner = purpose
        return partner.can_user_edit_payment(user)
    return False
