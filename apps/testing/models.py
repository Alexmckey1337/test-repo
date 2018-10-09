from django.db import models

from apps.account.models import CustomUser


class TestResult(models.Model):
    test_id = models.IntegerField()
    test_title = models.CharField(max_length=200)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_points = models.FloatField()

    class Meta:
        unique_together = ('test_id', 'user')

    def __str__(self):
        return '{}: {}'.format(self.test_id, self.user)
