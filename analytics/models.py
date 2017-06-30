from typing import Tuple

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import six
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.translation import ugettext_lazy as _, ugettext


class LogModel(models.Model):
    tracking_fields = tuple()
    tracking_reverse_fields = tuple()

    class Meta:
        abstract = True

    @classmethod
    def get_tracking_fields(cls) -> Tuple[str]:
        return cls.tracking_fields

    @classmethod
    def get_tracking_reverse_fields(cls) -> Tuple[str]:
        return cls.tracking_reverse_fields


@python_2_unicode_compatible
class LogRecord(models.Model):
    action_time = models.DateTimeField(
        _('action time'),
        default=timezone.now,
        editable=False,
    )
    user = models.ForeignKey(
        'account.CustomUser',
        models.CASCADE,
        verbose_name=_('user'),
        related_name='log_records'
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('content type'),
        blank=True, null=True,
    )
    object_id = models.TextField(_('object id'), blank=True, null=True)
    object_repr = models.CharField(_('object repr'), max_length=200)

    ADDITION, CHANGE, DELETION = 1, 2, 3
    ACTIONS = (
        (ADDITION, _('Addition')),
        (CHANGE, _('Change')),
        (DELETION, _('Deletion')),
    )
    action_flag = models.PositiveSmallIntegerField(_('action flag'), choices=ACTIONS, default=CHANGE)

    change_data = JSONField(_('change data'), blank=True)

    class Meta:
        verbose_name = _('log record')
        verbose_name_plural = _('log records')
        ordering = ('-action_time',)

    def __repr__(self):
        return smart_text(self.action_time)

    def __str__(self):
        if self.is_addition():
            return ugettext('Added "%(object)s".') % {'object': self.object_repr}
        elif self.is_change():
            return ugettext('Changed "%(object)s" - %(changes)s') % {
                'object': self.object_repr,
                'changes': self.get_change_message(),
            }
        elif self.is_deletion():
            return ugettext('Deleted "%(object)s."') % {'object': self.object_repr}

        return ugettext('LogRecord Object')

    def is_addition(self):
        return self.action_flag == self.ADDITION

    def is_change(self):
        return self.action_flag == self.CHANGE

    def is_deletion(self):
        return self.action_flag == self.DELETION

    @staticmethod
    def _get_value(value_dict, key):
        return value_dict[key].get('name', '') if isinstance(value_dict[key], dict) else value_dict[key]

    def _get_change_data(self, f, value):
        name = value.get('verbose_name', f)
        if 'value' in value.keys():
            old_value = '"{}"'.format(self._get_value(value['value'], 'old') or '')
            new_value = '"{}"'.format(self._get_value(value['value'], 'new') or '')
        else:
            return ''
        return ugettext('%s: с %s на %s' % (name, old_value, new_value))

    def get_change_message(self):
        change_data = self.change_data
        changed = change_data.get('changed', {})
        data = filter(lambda string: bool(string),
                      map(self._get_change_data, six.iterkeys(changed), six.itervalues(changed)))
        if changed == {}:
            return 'Unknown'
        if not changed:
            return ugettext('Without changes')
        return ', '.join(data)