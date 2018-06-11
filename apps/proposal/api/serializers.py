from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

from apps.account.models import CustomUser
from apps.proposal.models import Proposal


class CreateProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ('first_name', 'last_name', 'sex', 'born_date', 'locality', 'email', 'phone_number', 'type')

    def validate_sex(self, sex):
        if sex not in [s[0] for s in CustomUser.SEX]:
            return CustomUser.UNKNOWN
        return sex

    def validate_type(self, type_):
        if type_ not in [t[0] for t in Proposal.TYPES]:
            return Proposal.OTHER
        return type_


class UpdateProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ('status', 'user', 'manager', 'note', 'closed_at')

    def validate_status(self, new_status):
        current_status = self.instance.status

        if new_status not in settings.PROPOSAL_STATUS_PIPELINE.get(current_status, []):
            raise exceptions.ValidationError(
                {
                    'detail': _("You cannot change status from %s to %s") % (current_status, new_status),
                    'available_statuses': settings.PROPOSAL_STATUS_PIPELINE.get(current_status, [])
                 })

        proposal_is_reject = current_status in (settings.PROPOSAL_REJECTED, settings.PROPOSAL_PROCESSED)
        cancel_time_is_over = self.instance.cancel_time_is_over()

        if proposal_is_reject and cancel_time_is_over:
            raise exceptions.ValidationError(_("Время на возобновление отклоненной заявки прошло."))
        return new_status


class ReceiveProposalSerializer(UpdateProposalSerializer):
    class Meta:
        model = Proposal
        fields = ('status', 'manager', 'note')


class ReopenProposalSerializer(UpdateProposalSerializer):
    class Meta:
        model = Proposal
        fields = ('status', 'manager', 'note')