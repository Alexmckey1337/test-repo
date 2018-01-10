from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView

from apps.account.models import CustomUser, UserMarker
from apps.analytics.models import LogRecord
from apps.group.models import Church
from apps.hierarchy.models import Department, Hierarchy
from apps.partnership.models import Partnership, PartnerGroup
from apps.payment.models import Currency
from apps.status.models import Division


@login_required(login_url='entry')
def account(request, user_id=None):
    user = get_object_or_404(CustomUser, pk=user_id)
    currencies = Currency.objects.all()
    if not request.user.can_see_account_page(user):
        raise PermissionDenied
    ctx = {
        'account': user,
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'divisions': Division.objects.all(),
        'currencies': currencies,
        'churches': Church.objects.all(),
        'log_messages': LogRecord.objects.filter(
            object_id=user_id,
            content_type=ContentType.objects.get_for_model(user)
        ),
        'log_messages_iam': LogRecord.objects.filter(
            user_id=user_id,
            content_type=ContentType.objects.get_for_model(user)
        ),
        'partner_log_messages': LogRecord.objects.filter(
            object_id__in=list(user.partners.values_list('id', flat=True)),
            content_type=ContentType.objects.get_for_model(Partnership)
        ),
        'partner_log_messages_iam': LogRecord.objects.filter(
            user_id=user_id,
            content_type=ContentType.objects.get_for_model(Partnership)
        ),
        'markers': UserMarker.objects.all(),
        'partner_groups': PartnerGroup.objects.all()
    }
    return render(request, 'account/anketa.html', context=ctx)


class UserLogsListView(LoginRequiredMixin, ListView):
    model = LogRecord
    context_object_name = 'log_messages'
    template_name = 'account/logs/user.html'
    login_url = 'entry'

    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(CustomUser, pk=kwargs.get('user_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return LogRecord.objects.filter(
            object_id=self.user.id,
            content_type=ContentType.objects.get_for_model(self.user)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user'] = self.user
        return ctx


class OwnerLogsListView(UserLogsListView):
    template_name = 'account/logs/owner.html'

    def get_queryset(self):
        return LogRecord.objects.filter(
            user_id=self.user.id,
            content_type=ContentType.objects.get_for_model(self.user)
        )


class UserLogDetailView(LoginRequiredMixin, DetailView):
    model = LogRecord
    context_object_name = 'log_message'
    template_name = 'account/logs/detail.html'
    login_url = 'entry'
    pk_url_kwarg = 'log_id'
