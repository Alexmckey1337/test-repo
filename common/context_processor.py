import edem


def true_false_options(request):
    return {'true_false_options': [{'id': 'True', 'title': 'Да'}, {'id': 'False', 'title': 'Нет'}]}


def crm_version(request):
    return {
        'crm': {
            'version': edem.__version__,
        }
    }
