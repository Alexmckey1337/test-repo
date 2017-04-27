from django.db import models


class UserPermission(models.Model):
    class Meta:
        abstract = True

    def _perm_req(self):
        return type('Request', (), {'user': self})
