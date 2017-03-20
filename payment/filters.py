from rest_framework.filters import BaseFilterBackend


class PaymentFilterByPurpose(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        purpose = request.query_params.getlist('purpose', None)
        if not purpose:
            return queryset
        return queryset.filter(content_type__model__in=purpose)
