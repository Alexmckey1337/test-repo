from rest_framework.generics import get_object_or_404
from apps.account.models import CustomUser


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
