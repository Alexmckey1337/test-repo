from account.abstact_models import UserPermission
from summit.permissions import can_see_summit, can_see_summit_type, can_see_any_summit, can_see_any_summit_type


class SummitUserPermission(UserPermission):
    class Meta:
        abstract = True

    def can_see_summit(self, summit_id):
        request = self._perm_req()
        return can_see_summit(request, summit_id)

    def can_see_summit_type(self, summit_type):
        request = self._perm_req()
        return can_see_summit_type(request, summit_type)

    def can_see_any_summit(self):
        request = self._perm_req()
        return can_see_any_summit(request)

    def can_see_any_summit_type(self):
        request = self._perm_req()
        return can_see_any_summit_type(request)
