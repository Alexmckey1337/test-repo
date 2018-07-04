import edem
from apps.account.models import CustomUser
from apps.payment.models import Currency


def select_options(request):
    return {
        'true_false_options': [{'id': 'True', 'title': 'Да'}, {'id': 'False', 'title': 'Нет'}],
        'people_lang_options': [{'id': l[0], 'title': l[1]} for l in CustomUser.LANGUAGES],
    }


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
