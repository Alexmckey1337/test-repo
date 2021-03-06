import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

from apps.account.models import CustomUser
from apps.group.models import Direction
from apps.proposal.models import Proposal, EventProposal

logger = logging.getLogger('vo_org_ua')

BASE_PROPOSAL_FIELDS = (
    'first_name', 'last_name', 'sex', 'born_date', 'locality',
    'city', 'country',
    'email', 'phone_number', 'type',
    'leader_name', 'age_group', 'gender_group', 'geo_location', 'directions',
)


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = BASE_PROPOSAL_FIELDS + ('raw_data', 'created_at')


class CreateProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = BASE_PROPOSAL_FIELDS

    def save(self, **kwargs):
        kwargs.update({'raw_data': self.initial_data})
        return super().save(**kwargs)

    def validate_sex(self, sex):
        if sex not in [s[0] for s in CustomUser.SEX]:
            logger.warning({
                "message": _("Invalid proposal type"),
                "value": sex,
            })
            return CustomUser.UNKNOWN
        return sex

    def validate_type(self, type_):
        if type_ not in [t[0] for t in Proposal.TYPES]:
            logger.warning({
                "message": _("Invalid proposal type"),
                "value": type_,
            })
            return Proposal.OTHER
        return type_

    def validate_directions(self, codes):
        invalid_codes = (
                set(codes) - set(Direction.objects.filter(code__in=codes).values_list('code', flat=True))
        )

        if invalid_codes:
            logger.warning({
                "message": _("Invalid codes of directions"),
                "value": invalid_codes,
            })
        return codes


class BaseUpdateProposalSerializer(serializers.ModelSerializer):
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


class UpdateProposalSerializer(BaseUpdateProposalSerializer):
    class Meta:
        model = Proposal
        fields = ('status', 'user', 'manager', 'note', 'closed_at')


class ReceiveProposalSerializer(UpdateProposalSerializer):
    class Meta:
        model = Proposal
        fields = ('status', 'user', 'manager', 'note', 'closed_at')


class ReopenProposalSerializer(UpdateProposalSerializer):
    class Meta:
        model = Proposal
        fields = ('status', 'user', 'manager', 'note', 'closed_at')


class CreateEventProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventProposal
        fields = ('user', 'info')
        extra_kwargs = {
            'user': {'required': True},
        }

    def save(self, **kwargs):
        kwargs.update({'raw_data': self.initial_data})
        return super().save(**kwargs)


class EventProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventProposal
        fields = ('user', 'info', 'raw_data', 'created_at')


class UpdateEventProposalSerializer(BaseUpdateProposalSerializer):
    class Meta:
        model = EventProposal
        fields = ('status', 'profile', 'manager', 'note', 'closed_at')
