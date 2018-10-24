from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.account.models import CustomUser


class GroupsManager(models.Model):
	person = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='managed_groups', verbose_name=_('Group manager'))
	group = models.OneToOneField('group.HomeGroup', blank=True, on_delete=models.CASCADE, related_name='manage_person', verbose_name=_('Group'))

	def __str__(self):
		return '%s manager' % self.group.title