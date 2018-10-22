from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Manager(models.Model):
	person = models.ForeignKey('account.CustomUser', null=True, blank=True, on_delete=models.SET_NULL, related_name='managed_groups', verbose_name=_('Manager'))
	group = models.ForeignKey('group.HomeGroup', on_delete=models.CASCADE, related_name='manage_person', unique=True, verbose_name=_('Group'))

	def __str__(self):
		return '%s manager' % self.group.title