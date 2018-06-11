from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, status, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.account.models import CustomUser
from apps.proposal.api.permissions import CanCreateProposal, CanReceiveProposal, CanReopenProposal, CanRejectProposal, \
    CanProcessProposal
from apps.proposal.api.serializers import CreateProposalSerializer, UpdateProposalSerializer, ReceiveProposalSerializer, \
    ReopenProposalSerializer
from apps.proposal.models import Proposal, History


class CreateProposalView(generics.CreateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = CreateProposalSerializer
    permission_classes = (CanCreateProposal,)


class UpdateProposalStatusMixin(generics.GenericAPIView):
    queryset = Proposal.objects.all()
    new_status = None
    serializer_class = UpdateProposalSerializer

    def post(self, request, *args, **kwargs):
        proposal = self.get_object()

        data = request.data
        data.pop('manager', None)
        data.pop('status', None)
        data.update(self.get_data())

        serializer = self.serializer_class(proposal, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.update_proposal(serializer)
        self.log_updating(proposal)

        result = serializer.data
        result['available_next_statuses'] = settings.PROPOSAL_STATUS_PIPELINE.get(self.new_status, [])
        return Response(data=result, status=status.HTTP_200_OK)

    def get_data(self, **kwargs):
        kwargs['status'] = self.new_status
        return kwargs

    def update_proposal(self, proposal):
        proposal.save()

    def log_updating(self, proposal):
        History.log_proposal(proposal, owner=self.request.user)


class ReceiveProposalView(UpdateProposalStatusMixin):
    new_status = settings.PROPOSAL_IN_PROGRESS
    permission_classes = (IsAuthenticated, CanReceiveProposal)
    serializer_class = ReceiveProposalSerializer

    def get_data(self, **kwargs):
        return super().get_data(
            manager=self.request.user,
            closed_at=None,
            user=None
        )


class ReopenProposalView(UpdateProposalStatusMixin):
    new_status = settings.PROPOSAL_REOPEN
    permission_classes = (IsAuthenticated, CanReopenProposal)
    serializer_class = ReopenProposalSerializer

    def get_data(self, **kwargs):
        return super().get_data(
            manager=None,
            closed_at=None,
            user=None
        )


class RejectProposalView(UpdateProposalStatusMixin):
    new_status = settings.PROPOSAL_REJECTED
    permission_classes = (IsAuthenticated, CanRejectProposal)

    def get_data(self, **kwargs):
        return super().get_data(closed_at=timezone.now())


class ProcessProposalView(UpdateProposalStatusMixin):
    new_status = settings.PROPOSAL_PROCESSED
    permission_classes = (IsAuthenticated, CanProcessProposal)

    def get_data(self, **kwargs):
        return super().get_data(closed_at=timezone.now())
