from django.db import models


class ConsultantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_consultant=True)
