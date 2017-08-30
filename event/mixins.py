from rest_framework.generics import get_object_or_404
from account.models import CustomUser


class EventUserTreeSummaryMixin(object):
    @staticmethod
    def user_for_tree(request):
        master_id = request.query_params.get('master_id')
        if master_id:
            user = get_object_or_404(CustomUser, pk=master_id)
        else:
            user = request.user
        return user
