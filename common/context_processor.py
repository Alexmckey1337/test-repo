import edem
from apps.payment.models import Currency


def true_false_options(request):
    return {'true_false_options': [{'id': 'True', 'title': 'Да'}, {'id': 'False', 'title': 'Нет'}]}


def crm_version(request):
    return {
        'crm': {
            'version': edem.__version__,
        }
    }


def currency(request):
    currencies = Currency.objects.all()
    return {
        'currencies': currencies,
        'currency_options': [{'id': c.pk, 'title': c.name} for c in currencies]
    }