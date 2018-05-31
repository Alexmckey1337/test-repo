import operator
from datetime import datetime, timedelta

import coreapi
import coreschema
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP
from django.template import loader
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework import filters

from apps.account.models import CustomUser

if six.PY3:
    from functools import reduce


class FieldSearchFilter(filters.BaseFilterBackend):
    # The URL query parameter used for the search.
    # search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    lookup_prefixes = {
        '^': 'istartswith',
        '=': 'iexact',
        '@': 'search',
        '$': 'iregex',
    }

    def get_search_terms(self, request, search_params):
        """
        :param request:
        :param search_params: list of parameters, for example: ('search_title', 'search_text')
        :return: dict, for example: {'search_title': 'test', 'search_text': 'very long text'}
        """
        search_terms = dict()
        for search_param in search_params:
            params = request.query_params.get(search_param, '')
            if params:
                search_terms[search_param] = params.replace(',', ' ').split()
        return search_terms

    def construct_search(self, field_name):
        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = 'icontains'
        return LOOKUP_SEP.join([field_name, lookup])

    def must_call_distinct(self, queryset, search_fields):
        """
        Return True if 'distinct()' should be used to query the given lookups.
        """
        for search_field in search_fields:
            opts = queryset.model._meta
            if search_field[0] in self.lookup_prefixes:
                search_field = search_field[1:]
            parts = search_field.split(LOOKUP_SEP)
            for part in parts:
                field = opts.get_field(part)
                if hasattr(field, 'get_path_info'):
                    # This field is a relation, update opts to follow the relation
                    path_info = field.get_path_info()
                    opts = path_info[-1].to_opts
                    if any(path.m2m for path in path_info):
                        # This field is a m2m relation so we know we need to call distinct
                        return True
        return False

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'field_search_fields', {})
        search_terms = self.get_search_terms(request, search_fields.keys())

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = dict()

        for key in search_fields.keys():
            orm_lookups[key] = [
                self.construct_search(six.text_type(search_field))
                for search_field in search_fields[key]]

        # base = queryset
        for term_key in search_terms.keys():
            for search_term in search_terms[term_key]:
                queries = [
                    models.Q(**{orm_lookup: search_term})
                    for orm_lookup in orm_lookups[term_key]]
                queryset = queryset.filter(reduce(operator.or_, queries))

        # if self.must_call_distinct(queryset, search_fields):
        #     # Filtering against a many-to-many field requires us to
        #     # call queryset.distinct() in order to avoid duplicate items
        #     # in the resulting queryset.
        #     # We try to avoid this is possible, for performance reasons.
        #     queryset = distinct(queryset, base)
        return queryset

    def to_html(self, request, queryset, view):
        if not getattr(view, 'field_search_fields', None):
            return ''

        terms = self.get_search_terms(request, view.field_search_fields.keys())
        context = dict()
        for k, term in terms.items():
            term = term[0] if term else ''
            context[k] = {
                'param': k,
                'term': term
            }
        template = loader.get_template(self.template)
        return template.render(context)

    def get_fields(self, view):
        return [view.field_search_fields.keys()] if hasattr(view, 'field_search_fields') else []

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=field_name,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=field_name.replace('search_', '').capitalize(),
                    description="Search by fields: [``{}``]".format("``, ``".join(fields))
                )
            ) for field_name, fields in view.field_search_fields.items()
        ]


class BaseFilterByBirthday(filters.BaseFilterBackend):
    born_date_field = ''

    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        from_date = params.get('from_date', None)
        to_date = params.get('to_date', None)

        if not (from_date and to_date):
            return queryset
        from_date = pytz.utc.localize(datetime.strptime(from_date, '%Y-%m-%d'))
        to_date = pytz.utc.localize(datetime.strptime(to_date, '%Y-%m-%d'))
        if from_date > to_date:
            raise exceptions.ValidationError(detail=_('Некоректный временной интервал.'))

        monthdays = [(from_date.month, from_date.day)]
        while from_date <= to_date:
            monthdays.append((from_date.month, from_date.day))
            from_date += timedelta(days=1)

        monthdays = (dict(zip((
            "%s__month" % self.born_date_field,
            "%s__day" % self.born_date_field), t)) for t in monthdays)
        query = reduce(operator.or_, (Q(**d) for d in monthdays))

        return queryset.filter(query)

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=self.born_date_field,
                required=False,
                location='query',
                schema=coreschema.String(
                    title="Birthday",
                    description="Day of birth, format: ``%Y-%m-%d``"
                )
            )
        ]


class BaseFilterMasterTree(filters.BaseFilterBackend):
    include_self_master = False
    user_field_prefix = ''

    def filter_queryset(self, request, queryset, view):
        master_id = request.query_params.get('master_tree', None)

        try:
            master = CustomUser.objects.get(pk=master_id)
        except (ObjectDoesNotExist, ValueError):
            return queryset

        if master.is_leaf():
            if self.include_self_master:
                return queryset.filter(**{'%sid' % self.user_field_prefix: master.id})
            return queryset.none()

        # return cls.objects.filter(path__startswith=parent.path,
        #                           depth__gte=parent.depth)
        filter_by_master_tree = {
            '%spath__startswith' % self.user_field_prefix: master.path,
            '%sdepth__gte' % self.user_field_prefix: master.depth,
        }

        qs = queryset.filter(**filter_by_master_tree)
        if self.include_self_master:
            return qs
        return qs.exclude(**{'%sid' % self.user_field_prefix: master.id})

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name="master_tree",
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Master tree',
                    description="Id of user (master) for filter by master tree"
                )
            )
        ]


class OrderingFilter(filters.OrderingFilter):
    def get_schema_fields(self, view):
        ordering_fields = getattr(view, "ordering_fields", self.ordering_fields)
        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.ordering_title),
                    description=("Ordering by one of (``{}``)".format("``, ``".join(ordering_fields))
                                 if ordering_fields else force_text(self.ordering_description))
                )
            )
        ]


class OrderingFilterWithPk(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)

        if ordering and isinstance(ordering, (list, tuple)):
            return ordering + {tuple: ('pk',), list: ['pk']}[type(ordering)]
        return ordering
