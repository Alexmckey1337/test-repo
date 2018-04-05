from django.db import models


class Department(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Hierarchy(models.Model):
    title = models.CharField(max_length=50, unique=True)
    level = models.IntegerField()

    class Meta:
        ordering = ['level']

    def __str__(self):
        return self.title
