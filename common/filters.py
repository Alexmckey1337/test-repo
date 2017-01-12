import operator

from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.template import loader
from django.utils import six
from rest_framework.compat import template_render
from rest_framework.filters import BaseFilterBackend

if six.PY3:
    from functools import reduce


class FieldSearchFilter(BaseFilterBackend):
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
                for search_field in search_fields[key]
                ]

        # base = queryset
        for term_key in search_terms.keys():
            for search_term in search_terms[term_key]:
                queries = [
                    models.Q(**{orm_lookup: search_term})
                    for orm_lookup in orm_lookups[term_key]
                    ]
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
        return template_render(template, context)

    def get_fields(self, view):
        return [view.field_search_fields.keys()] if hasattr(view, 'field_search_fields') else []
