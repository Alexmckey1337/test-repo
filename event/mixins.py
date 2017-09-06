from rest_framework.generics import get_object_or_404
from account.models import CustomUser
from payment.views_mixins import ListPaymentMixin
from rest_framework.response import Response


class EventUserTreeMixin(object):
    @staticmethod
    def master_for_summary(request):
        master_id = request.query_params.get('master_id')
        if master_id:
            user = get_object_or_404(CustomUser, pk=master_id)
        else:
            user = request.user
        return user

    @staticmethod
    def user_for_dashboard(request):
        user_id = request.query_params.get('user_id')
        if user_id:
            user = get_object_or_404(CustomUser, pk=user_id)
        else:
            user = request.user
        return user


class ChurchReportListPaymentMixin(ListPaymentMixin):
    def _payments(self, request, pk=None):
        purpose_model = self.get_queryset().model
        purpose = get_object_or_404(purpose_model, pk=pk)

        queryset = getattr(purpose, self.payment_list_field).select_related(
            'currency_sum', 'currency_rate', 'manager')

        serializer = self.list_payment_serializer(queryset, many=True)

        return Response(serializer.data)
