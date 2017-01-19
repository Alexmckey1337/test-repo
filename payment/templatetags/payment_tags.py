from django import template

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
