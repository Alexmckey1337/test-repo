from django.conf import settings


class BaseUserPermission(object):
    queryset = None

    def __init__(self, user, **kwargs):
        self.user = user
        queryset = kwargs.get('queryset', None)
        if queryset is not None:
            self.queryset = queryset

    def has_permission(self):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def get_queryset(self):
        """
        User-accessible queryset
        """
        assert self.queryset is not None, 'queryset not specified.'

        return self.queryset


def can_vo_org_ua_key(request):
    return settings.VO_ORG_UA_TOKEN == request.META.get(settings.VO_ORG_UA_TOKEN_NAME, '')