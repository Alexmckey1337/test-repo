from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.account.models import CustomUser
from apps.group.models import Direction


class AbstractProposal(models.Model):
    # request.data
    raw_data = JSONField(_('raw data'), blank=True, default={})

    # Internal fields (editable)
    STATUSES = settings.PROPOSAL_STATUSES
    status = models.CharField(
        _('Status'), choices=STATUSES, default=settings.PROPOSAL_OPEN, max_length=25
    )

    created_at = models.DateTimeField(_('Created at'), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True, editable=False)
    closed_at = models.DateTimeField(_('Closed at'), null=True, blank=True)

    note = models.TextField(_('Note'))

    class Meta:
        abstract = True
        ordering = ['-created_at']

    @property
    def is_open(self):
        return self.status in (settings.PROPOSAL_OPEN, settings.PROPOSAL_REOPEN)

    @property
    def in_progress(self):
        return self.status == settings.PROPOSAL_IN_PROGRESS

    @property
    def is_complete(self):
        return self.status in (settings.PROPOSAL_PROCESSED, settings.PROPOSAL_REJECTED)

    def cancel_time_is_over(self):
        return (
                self.closed_at and
                self.closed_at + timedelta(seconds=settings.CANCEL_CLOSE_TIME) < timezone.now()
        )


class Proposal(AbstractProposal):
    # Taken fields (only created, but not editable)
    first_name = models.CharField(_('First name'), blank=True, max_length=30)
    last_name = models.CharField(_('Last name'), blank=True, max_length=150)

    sex = models.CharField(_('Sex'), max_length=7, default=CustomUser.UNKNOWN)
    born_date = models.DateField(_('Born date'), blank=True, null=True)
    locality = models.ForeignKey(
        'location.City', on_delete=models.SET_NULL, related_name='proposals',
        null=True, blank=True, verbose_name=_('Locality'),
        help_text=_('City/village/etc')
    )
    city = models.CharField(_('City'), max_length=120, blank=True)
    country = models.CharField(_('Country'), max_length=120, blank=True)

    email = models.CharField(_('email address'), max_length=254, blank=True)
    phone_number = models.CharField(_('Phone number'), max_length=23, blank=True)

    SHORT, FULL, OTHER = 'short', 'full', 'other'
    TYPES = (
        (SHORT, _('Short')),
        (FULL, _('Full')),
        (OTHER, _('Other')),
    )
    type = models.CharField(_('Type'), default=OTHER, max_length=25)

    # second step
    leader_name = models.CharField(_('Leader fio'), max_length=255, blank=True)
    age_group = models.CharField(_('Age group'), max_length=255, blank=True)
    gender_group = models.CharField(_('Gender group'), max_length=255, blank=True)
    geo_location = models.CharField(_('GEO location'), max_length=255, blank=True)

    directions = ArrayField(models.CharField(max_length=60), blank=True, null=True)

    user = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='proposals', verbose_name=_('User')
    )
    manager = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='manager_proposals', verbose_name=_('Manager')
    )

    def __str__(self):
        return ' '.join([self.last_name, self.first_name]).strip() or 'No Name'

    def get_sex_display(self):
        for k, v in CustomUser.SEX:
            if k == self.sex:
                return v
        return ''

    def get_type_display(self):
        for k, v in self.TYPES:
            if k == self.type:
                return v
        return ''

    def directions_titles(self, lang='ru'):
        proposal_direction_codes = self.directions or []
        directions = Direction.in_bulk_by_codes(proposal_direction_codes)
        titles = dict()
        for code in proposal_direction_codes:
            direction = directions.get(code)
            if direction is not None:
                titles[code] = getattr(direction, f'title_{lang}', direction.title_ru)
            else:
                titles[code] = code
        return titles


class History(models.Model):
    proposal = models.ForeignKey(
        'proposal.Proposal', on_delete=models.CASCADE, related_name='histories',
        verbose_name=_('Proposal'), editable=False
    )
    owner = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True, editable=False,
        related_name='owner_histories', verbose_name=_('Owner')
    )
    manager = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True, editable=False,
        related_name='proposal_histories', verbose_name=_('Manager')
    )  # related to Proposal.manager field
    user = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True, editable=False,
        related_name='+', verbose_name=_('User')
    )  # related to Proposal.user field

    status = models.CharField(_('Status'), max_length=25, editable=False)
    note = models.TextField(_('Note'))
    closed_at = models.DateTimeField(_('Closed at'), null=True, blank=True, editable=False)

    CREATE, UPDATE = 'create', 'update'
    REASONS = (
        (CREATE, _('Create')),
        (UPDATE, _('Update')),
    )
    reason = models.CharField(_('Reason'), choices=REASONS, max_length=25, editable=False)

    created_at = models.DateTimeField(_('Created at'), default=timezone.now, editable=False)

    @classmethod
    def log_proposal(cls, proposal, owner, reason=None):
        if reason is None:
            reason = cls.UPDATE
        cls.objects.create(
            proposal=proposal,
            owner=owner,
            manager=proposal.manager,
            user=proposal.user,
            status=proposal.status,
            note=proposal.note,
            closed_at=proposal.closed_at,
            reason=reason
        )


class EventProposal(AbstractProposal):
    # Taken fields (only created, but not editable)
    user = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, null=True)
    info = JSONField(_('Additional information'), blank=True, default={})

    profile = models.ForeignKey(
        'summit.SummitAnket', on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='proposals', verbose_name=_('Event profile')
    )
    manager = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='manager_event_proposals', verbose_name=_('Manager')
    )

    def __str__(self):
        return self.user or 'Unknown user'


class EventHistory(models.Model):
    proposal = models.ForeignKey(
        'proposal.EventProposal', on_delete=models.CASCADE, related_name='histories',
        verbose_name=_('Event Proposal'), editable=False
    )
    owner = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True, editable=False,
        related_name='owner_event_histories', verbose_name=_('Owner')
    )
    manager = models.ForeignKey(
        'account.CustomUser', on_delete=models.PROTECT,
        null=True, blank=True, editable=False,
        related_name='proposal_event_histories', verbose_name=_('Manager')
    )  # related to EventProposal.manager field
    profile = models.ForeignKey(
        'summit.SummitAnket', on_delete=models.PROTECT,
        null=True, blank=True, editable=False,
        related_name='+', verbose_name=_('Event profile')
    )  # related to EventProposal.profile field

    status = models.CharField(_('Status'), max_length=25, editable=False)
    note = models.TextField(_('Note'))
    closed_at = models.DateTimeField(_('Closed at'), null=True, blank=True, editable=False)

    CREATE, UPDATE = 'create', 'update'
    REASONS = (
        (CREATE, _('Create')),
        (UPDATE, _('Update')),
    )
    reason = models.CharField(_('Reason'), choices=REASONS, max_length=25, editable=False)

    created_at = models.DateTimeField(_('Created at'), default=timezone.now, editable=False)

    @classmethod
    def log_proposal(cls, proposal, owner, reason=None):
        if reason is None:
            reason = cls.UPDATE
        cls.objects.create(
            proposal=proposal,
            owner=owner,
            manager=proposal.manager,
            profile=proposal.profile,
            status=proposal.status,
            note=proposal.note,
            closed_at=proposal.closed_at,
            reason=reason
        )


def create_proposal(sender, instance, created, **kwargs):
    if created:
        History.objects.create(
            proposal=instance,
            status=instance.status,
            reason=History.CREATE
        )


def create_event_proposal(sender, instance, created, **kwargs):
    if created:
        EventHistory.objects.create(
            proposal=instance,
            status=instance.status,
            reason=History.CREATE
        )


post_save.connect(create_proposal, Proposal)
post_save.connect(create_event_proposal, EventProposal)
