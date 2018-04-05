from django.db import models
from django.utils.translation import ugettext as _


class TaskType(models.Model):
    title = models.CharField(_('Title'), unique=True, max_length=255)

    def __str__(self):
        return self.title


class Task(models.Model):
    IN_WORK, DONE = 'in_work', 'done'
    STATUSES = (
        (IN_WORK, _('in_work')),
        (DONE, _('done')),
    )

    type = models.ForeignKey('TaskType', on_delete=models.PROTECT,
                             related_name='tasks', verbose_name=_('TaskType'))
    division = models.ForeignKey('status.Division', on_delete=models.PROTECT,
                                 related_name='tasks', verbose_name=_('Division'),
                                 blank=True, null=True)
    executor = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT,
                                 related_name='task_executor', blank=True, null=True,
                                 verbose_name=_('Task Executor'))
    creator = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT,
                                related_name='task_creator', verbose_name=_('Task Creator'))
    target = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT,
                               related_name='task_target', blank=True, null=True,
                               verbose_name=_('Task Target'))
    status = models.CharField(_('Status'), default=IN_WORK, choices=STATUSES, max_length=255)
    date_published = models.DateField(_('Date Published'))
    description = models.TextField(_('Description'))
    date_finish = models.DateField(_('Date Finish'), blank=True, null=True)
    finish_report = models.TextField(_('Finish Report'), blank=True, null=True)

    class Meta:
        verbose_name = _('User Task')
        verbose_name_plural = _('User Tasks')
        ordering = ['status', '-date_published']

    def __str__(self):
        return 'Задача: тип - %s, статус - [%s]. Исполнитель: %s. Автор: %s' % (
            self.type, 'Выполнено' if self.status else 'В работе', self.executor, self.creator)
