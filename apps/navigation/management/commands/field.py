import time
from decimal import Decimal
from pprint import pprint

from django.contrib.postgres.aggregates import ArrayAgg
from django.core.management.base import BaseCommand
from django.db.models import Case, IntegerField
from django.db.models import F
from django.db.models import Sum, Value
from django.db.models import When
from django.db.models.functions import Coalesce
from apps.partnership.models import Partnership
from apps.payment.models import Currency

MAX_RECURSIVE_LEVEL = 1


class Command(BaseCommand):
    def get_concrete_fields(self, opts, level=0):
        r = list()
        fields = opts._get_fields(reverse=False)
        for f in fields:
            f_dict = {
                'name': f.name,
                'field': f,
                'model': f.model
            }
            if f.is_relation and level < MAX_RECURSIVE_LEVEL and f.remote_field is not None:
                opts = f.remote_field.model._meta.concrete_model._meta
                f_dict['related_fields'] = self.get_concrete_fields(opts, level=level + 1)
            r.append(f_dict)
        return r

    def get_reverse_fields(self, opts, level=0):
        r = list()
        fields = opts._get_fields(forward=False)
        for f in fields:
            f_dict = {
                'name': f.get_accessor_name(),
                'field': f,
                'model': f.remote_model
            }
            if MAX_RECURSIVE_LEVEL > 0:
                opts = f.remote_model._meta.concrete_model._meta
                f_dict['related_fields'] = self.get_concrete_fields(opts, level=level + 1)
            r.append(f_dict)
        return r

    def print_fields(self, fields, indent=0):
        for f in fields:
            print('{}{:24}{:60}'.format('\t' * indent, f['name'], repr(f['field'])))
            if 'related_fields' in f.keys():
                self.print_fields(f['related_fields'], indent=indent + 1)

    #
    # def handle(self, *args, **options):
    #     user = CustomUser.objects.first()
    #
    #     opts = CustomUser._meta.concrete_model._meta
    #
    #     # for f in fields:
    #     #     if isinstance(f, OneToOneRel):
    #     #         print('{:30}'.format(f.name), f.related_model.objects.filter(**{f.field.name: user}).first())
    #     #     elif isinstance(f, (ManyToOneRel, ManyToManyRel)):
    #     #         print('{:30}'.format(f.name), f.related_model.objects.filter(**{f.field.name: user}))
    #     #     elif isinstance(f, (OneToOneField,)):
    #     #         print('{:30}'.format(f.name), f.value_from_object(user))
    #     #     elif isinstance(f, (ManyToManyField,)):
    #     #         print('{:30}'.format(f.name), f.value_from_object(user))
    #     #     elif isinstance(f, GenericRelation):
    #     #         print('{:30}'.format(f.name), f.value_from_object(user).get_queryset())
    #     #     elif f.is_relation:
    #     #         print('{:30}'.format(f.name), f.remote_field.model.objects.filter(
    #     #             pk=f.value_from_object(user)).first())
    #     #     else:
    #     #         value = f.value_from_object(user)
    #     #         print('{:30}'.format(f.name), value if value != '' else '----')
    #     fields = self.get_concrete_fields(opts)
    #
    #     print('{:24} {}'.format('CONCRETE:', len(fields)))
    #     print('-'*88)
    #     self.print_fields(fields)
    #     print()
    #     # ---------------------------------------------------------------------------------------
    #
    #     fields = self.get_reverse_fields(opts)
    #
    #     print('{:24} {}'.format('REVERSE:', len(fields)))
    #     print('-'*88)
    #     for f in fields:
    #         print('{:24}{:50}'.format(f['name'], repr(f['field'])), f['model'])
    #         if 'related_fields' in f.keys():
    #             self.print_fields(f['related_fields'], 1)

    def handle(self, *args, **options):
        t = time.time()
        partnership = Partnership.objects.get(pk=34)

        month = 11
        year = 2016

        deals = partnership.disciples_deals
        disciples_deals = deals.filter(
            date_created__month=month, date_created__year=year)
        deals_annotate = disciples_deals.annotate(
            total_sum=Coalesce(Sum('payments__effective_sum'), Value(0)))

        paid = deals_annotate.filter(total_sum__gte=F('value')).count()
        unpaid = deals_annotate.filter(total_sum__lt=F('value'), total_sum=Decimal(0)).count()
        partial_paid = deals_annotate.filter(total_sum__lt=F('value'), total_sum__gt=Decimal(0)).count()
        result = {
            'sum': {},
            'deals': {
                'paid_count': paid,
                'unpaid_count': unpaid,
                'partial_paid_count': partial_paid
            }
        }

        closed_count = disciples_deals.aggregate(
            closed_count=Sum(
                Case(When(done=True, then=1), default=0,
                     output_field=IntegerField())
            ),
            unclosed_count=Sum(
                Case(When(done=False, then=1), default=0,
                     output_field=IntegerField())
            ))
        result['deals'].update(closed_count)

        paid = set(deals_annotate.filter(total_sum__gte=F('value')).aggregate(p=ArrayAgg('partnership'))['p'])
        unpaid = set(deals_annotate.filter(
            total_sum__lt=F('value'),
            total_sum=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        partial_paid = set(deals_annotate.filter(
            total_sum__lt=F('value'),
            total_sum__gt=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        paid_count = len(paid - unpaid - partial_paid)
        unpaid_count = len(unpaid - partial_paid - paid)
        partial_paid_count = len(partial_paid | (paid & unpaid))

        closed = set(disciples_deals.filter(done=True).aggregate(p=ArrayAgg('partnership'))['p'])
        unclosed = set(disciples_deals.filter(done=False).aggregate(p=ArrayAgg('partnership'))['p'])
        closed_count = len(closed - unclosed)
        unclosed_count = len(unclosed)

        result['partners'] = {
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'partial_paid_count': partial_paid_count,
            'closed_count': closed_count,
            'unclosed_count': unclosed_count
        }

        currencies = set(
            disciples_deals.aggregate(currency_codes=ArrayAgg('currency__code'))['currency_codes'])

        for c in Currency.objects.filter(code__in=currencies):
            total_paid_sum = deals_annotate.filter(currency=c).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            closed_paid_sum = deals_annotate.filter(currency=c, done=True).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            result['sum'][c.code] = {
                'currency_name': c.name,
                'total_paid_sum': total_paid_sum,
                'closed_paid_sum': closed_paid_sum
            }

        pprint(result)
        print(round(time.time() - t, 4))
