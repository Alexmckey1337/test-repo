from datetime import timedelta
from itertools import chain

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView

from apps.account.models import CustomUser
from apps.proposal.api.permissions import can_see_proposal_list, can_see_proposal
from apps.proposal.models import Proposal


class CanSeeProposalListMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not can_see_proposal_list(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CanSeeProposalDetailMixin(View):
    def dispatch(self, request, *args, **kwargs):
        proposal = kwargs.get('pk')
        if not (proposal and can_see_proposal(request.user, proposal)):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ProposalListView(LoginRequiredMixin, CanSeeProposalListMixin, ListView):
    model = Proposal
    context_object_name = 'proposals'
    login_url = 'entry'
    template_name = 'proposal/list.html'

    def get_queryset(self):
        proposal_is_open = Q(status__in=(settings.PROPOSAL_OPEN, settings.PROPOSAL_REOPEN))
        proposal_in_progress = (
                Q(status=settings.PROPOSAL_IN_PROGRESS) &
                Q(manager=self.request.user)
        )
        proposal_is_complete = (
                Q(status__in=(settings.PROPOSAL_REJECTED, settings.PROPOSAL_PROCESSED)) &
                Q(manager=self.request.user)
        )
        qs = super().get_queryset().filter(
            proposal_is_open | proposal_in_progress | proposal_is_complete
        )
        statuses = self.request.GET.getlist('status')
        statuses = list(chain(*[s.split(',') for s in statuses]))
        if all([status in dict(settings.PROPOSAL_STATUSES) for status in statuses]):
            qs = qs.filter(status__in=statuses)
        return qs


class ProposalDetailView(LoginRequiredMixin, CanSeeProposalDetailMixin, DetailView):
    model = Proposal
    context_object_name = 'proposal'
    login_url = 'entry'
    template_name = 'proposal/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['sex_options'] = CustomUser.SEX
        ctx['people_lang_options'] = [{'id': l[0], 'title': l[1]} for l in CustomUser.LANGUAGES]

        similar_users = CustomUser.objects.filter(is_active=True)
        similar_users = similar_users.filter(
            (~Q(phone_number='') & Q(phone_number=self.object.phone_number)) |
            (~Q(email='') & Q(email__iexact=self.object.email))
        )
        ctx['similar_users'] = similar_users

        return ctx
