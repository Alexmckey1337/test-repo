from rest_framework import throttling


class ScopedRateByUrlPkThrottle(throttling.ScopedRateThrottle):
    scope_attr = 'throttle_scope'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        uid = view.kwargs.get('pk', '0')
        ident = f'{ident}_{uid}'

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
