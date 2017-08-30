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
