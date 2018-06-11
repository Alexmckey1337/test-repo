from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.account.models import CustomUser


class Proposal(models.Model):
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
    email = models.CharField(_('email address'), max_length=254, blank=True)
    phone_number = models.CharField(_('Phone number'), max_length=23, blank=True)

    SHORT, FULL, OTHER = 'short', 'full', 'other'
    TYPES = (
        (SHORT, _('Short')),
        (FULL, _('Full')),
        (OTHER, _('Other')),
    )
    type = models.CharField(_('Type'), default=OTHER, max_length=25)

    # Internal fields (editable)
    STATUSES = settings.PROPOSAL_STATUSES
    status = models.CharField(
        _('Status'), choices=STATUSES, default=settings.PROPOSAL_OPEN, max_length=25
    )

    created_at = models.DateTimeField(_('Created at'), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True, editable=False)
    closed_at = models.DateTimeField(_('Closed at'), null=True, blank=True)

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
    note = models.TextField(_('Note'))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return ' '.join([self.last_name, self.first_name]).strip()

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


def create_proposal(sender, instance, created, **kwargs):
    if created:
        History.objects.create(
            proposal=instance,
            status=instance.status,
            reason=History.CREATE
        )


post_save.connect(create_proposal, Proposal)