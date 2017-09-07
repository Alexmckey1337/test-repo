from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_fields import payment_table


class PaymentPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    value = 0

    def get_paginated_response(self, data):
        uah = sum([int(x['sum']) for x in data if x['currency_sum']['code'] == 'uah'])
        rub = sum([int(x['sum']) for x in data if x['currency_sum']['code'] == 'rur'])
        eur = sum([int(x['sum']) for x in data if x['currency_sum']['code'] == 'eur'])
        usd = sum([int(x['sum']) for x in data if x['currency_sum']['code'] == 'usd'])

        summa = {'uah': uah,
                 'rub': rub,
                 'eur': eur,
                 'usd': usd}

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': payment_table(self.request.user),
            'results': data,
            'summa': summa,
        })
