import django_filters
from django.conf import settings
from django.utils import timezone
from django_filters import rest_framework
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.proposal.api.permissions import (
    CanCreateProposal, CanReceiveProposal, CanReopenProposal, CanRejectProposal, CanProcessProposal)
from apps.proposal.api.serializers import (
    CreateProposalSerializer, UpdateProposalSerializer, ReceiveProposalSerializer,
    ReopenProposalSerializer, ProposalSerializer, CreateEventProposalSerializer, EventProposalSerializer,
    UpdateEventProposalSerializer)
from apps.proposal.models import Proposal, History, EventProposal, EventHistory
from common.filters import OrderingFilterWithPk, FieldSearchFilter


class CreateProposalView(generics.CreateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = CreateProposalSerializer
    permission_classes = (CanCreateProposal,)


class ProposalFilter(django_filters.FilterSet):
    created_from = django_filters.DateTimeFilter(name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(name='created_at', lookup_expr='lte')

    class Meta:
        model = Proposal
        fields = ['created_from', 'created_to', 'sex', 'type']


class ProposalListView(generics.ListAPIView):
    queryset = Proposal.objects.order_by('-created_at')
    serializer_class = ProposalSerializer
    permission_classes = (CanCreateProposal,)
    filter_backends = (
        rest_framework.DjangoFilterBackend,
        FieldSearchFilter,
        OrderingFilterWithPk,
    )
    ordering_fields = (
        'first_name', 'last_name', 'born_date', 'country', 'city',
        'phone_number', 'email', 'sex', 'type',
    )
    field_search_fields = {
        'search_fio': ('last_name', 'first_name'),
        'search_email': ('email',),
        'search_phone_number': ('phone_number',),
        'search_city': ('city',),
        'search_country': ('country',),
        'search': ('leader_name', 'age_group', 'gender_group', 'geo_location'),
    }
    filter_class = ProposalFilter

    def post(self, request, *args, **kwargs):
        return CreateProposalView.as_view()(request._request, *args, **kwargs)


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


class CreateEventProposalView(generics.CreateAPIView):
    queryset = EventProposal.objects.all()
    serializer_class = CreateEventProposalSerializer
    permission_classes = (CanCreateProposal,)


class EventProposalListView(generics.ListAPIView):
    queryset = EventProposal.objects.order_by('-created_at')
    serializer_class = EventProposalSerializer
    permission_classes = (CanCreateProposal,)

    def post(self, request, *args, **kwargs):
        return CreateEventProposalView.as_view()(request._request, *args, **kwargs)


class UpdateEventProposalStatusMixin(generics.GenericAPIView):
    queryset = EventProposal.objects.all()
    new_status = None
    serializer_class = UpdateEventProposalSerializer

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
        EventHistory.log_proposal(proposal, owner=self.request.user)


class ReceiveEventProposalView(UpdateEventProposalStatusMixin):
    new_status = settings.PROPOSAL_IN_PROGRESS
    permission_classes = (IsAuthenticated, CanReceiveProposal)

    def get_data(self, **kwargs):
        return super().get_data(
            manager=self.request.user,
            closed_at=None,
            profile=None
        )


class ReopenEventProposalView(UpdateEventProposalStatusMixin):
    new_status = settings.PROPOSAL_REOPEN
    permission_classes = (IsAuthenticated, CanReopenProposal)

    def get_data(self, **kwargs):
        return super().get_data(
            manager=None,
            closed_at=None,
            profile=None
        )


class RejectEventProposalView(UpdateEventProposalStatusMixin):
    new_status = settings.PROPOSAL_REJECTED
    permission_classes = (IsAuthenticated, CanRejectProposal)

    def get_data(self, **kwargs):
        return super().get_data(closed_at=timezone.now())


class ProcessEventProposalView(UpdateEventProposalStatusMixin):
    new_status = settings.PROPOSAL_PROCESSED
    permission_classes = (IsAuthenticated, CanProcessProposal)

    def get_data(self, **kwargs):
        return super().get_data(closed_at=timezone.now())
