from rest_framework.generics import get_object_or_404
from account.models import CustomUser


class EventUserTreeSummaryMixin(object):
    def user_for_tree(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            user = get_object_or_404(CustomUser, pk=user_id)
        else:
            user = self.request.user

        return user
