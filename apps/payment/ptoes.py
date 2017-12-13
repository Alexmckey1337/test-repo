import os
import sys

import django

print('Python %s on %s' % (sys.version, sys.platform))
print('Django %s' % django.get_version())
sys.path.extend(['/app/'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edem.settings.dev")
if 'setup' in dir(django):
    django.setup()
# import django_manage_shell; django_manage_shell.run(PROJECT_ROOT)

from apps.payment.models import Payment
from elasticsearch import Elasticsearch

es = Elasticsearch(['es'])

payments = Payment.objects.filter(content_type_id=40).select_related('currency_sum', 'currency_rate', 'manager')

for i, p in enumerate(payments):
    try:
        body = {
            'id': p.id,
            'sum': p.sum,
            'sum_str': p.sum_str,
            'effective_sum': p.effective_sum,
            'effective_sum_str': p.effective_sum_str,
            'operation': p.operation,
            'currency_sum': {
                'id': p.currency_sum.id,
                'name': p.currency_sum.name,
                'code': p.currency_sum.code,
                'symbol': p.currency_sum.symbol,
            } if p.currency_sum else {
                'id': 0,
                'name': 'Unknown',
                'code': 'unknown',
                'symbol': '-',
            },
            'currency_rate': {
                'id': p.currency_sum.id,
                'name': p.currency_sum.name,
                'code': p.currency_sum.code,
                'symbol': p.currency_sum.symbol,
            } if p.currency_rate else {
                'id': 0,
                'name': 'Unknown',
                'code': 'unknown',
                'symbol': '-',
            },
            'rate': p.rate,
            'description': p.description,
            'created_at': p.created_at,
            'sent_date': p.sent_date,
            'manager': {
                'id': p.manager.id,
                'name': ' '.join([p.manager.last_name, p.manager.first_name, p.manager.middle_name]).strip()
            } if p.manager else {
                'id': 0,
                'name': ''
            },
            'deal': {
                'id': p.purpose.id,
                'name': str(p.purpose.partnership.user),
                'type_id': p.purpose.type,
                'type': p.purpose.get_type_display(),
                'currency': {
                    'id': p.purpose.currency.id,
                    'name': p.purpose.currency.name,
                    'code': p.purpose.currency.code,
                    'symbol': p.purpose.currency.symbol,
                } if p.purpose.currency else {
                    'id': 0,
                    'name': 'Unknown',
                    'code': 'unknown',
                    'symbol': '-',
                },
                'date': p.purpose.date,
                'date_created': p.purpose.date_created,
                'responsible': {
                    'name': str(p.purpose.responsible) if p.purpose.responsible else '',
                    'id': p.purpose.responsible.id if p.purpose.responsible else 0,
                },
                'partner': {
                    'name': str(p.purpose.partnership) if p.purpose.partnership else '',
                    'id': p.purpose.partnership.id if p.purpose.partnership else 0,
                },
                'user': {
                    'name': str(p.purpose.partnership.user) if p.purpose.partnership else '',
                    'id': p.purpose.partnership.user_id if p.purpose.partnership else 0,
                },
            },
            'content_type': 'user_deal',
            'object_id': p.object_id,
        }
        es.index(index='vocrm', doc_type='payment', body=body)
    except Exception as err:
        print(p.id, err)
    if i % 1000 == 0:
        print(i)
