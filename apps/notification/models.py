from django.db import models


class NotificationTheme(models.Model):
    title = models.CharField(max_length=100)
    birth_day = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    theme = models.ForeignKey(NotificationTheme, on_delete=models.CASCADE, related_name='notifications')
    description = models.TextField()
    date = models.DateField(null=True, blank=True)
    common = models.BooleanField(default=True)
    system = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return '{} {}'.format(self.fullname, self.theme)

    @property
    def fullname(self):
        return self.user.get_full_name()

    @property
    def uid(self):
        return str(self.user.id)
