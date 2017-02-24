# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import BasePermission, IsAuthenticated

from partnership.permissions import IsManagerReadOnly, IsSupervisorOrHigh as IsPartnerSupervisorOrHigh, IsDisciplesOf
from summit.permissions import IsConsultantReadOnly, IsSupervisorOrHigh as IsSummitSupervisorOrHigh


class PaymentPermission(BasePermission):
    def has_object_permission(self, request, view, purpose):
        purpose_model = view.get_queryset().model
        content_type = ContentType.objects.get_for_model(purpose_model)
        if content_type.app_label == 'summit' and content_type.model == 'summitanket':
            return (
                IsConsultantReadOnly().has_object_permission(request, view, purpose) or
                IsSummitSupervisorOrHigh().has_object_permission(request, view, purpose))
        if content_type.app_label == 'partnership' and content_type.model == 'partnership':
            return (
                (IsManagerReadOnly().has_permission(request, view) and
                 IsDisciplesOf().has_object_permission(request, view, purpose.user)) or
                IsPartnerSupervisorOrHigh().has_permission(request, view))
        if content_type.app_label == 'partnership' and content_type.model == 'deal':
            return (
                (IsManagerReadOnly().has_permission(request, view) and
                 IsDisciplesOf().has_object_permission(request, view, purpose.partnership.user)) or
                IsPartnerSupervisorOrHigh().has_permission(request, view))
        return False


class PaymentManager(IsAuthenticated):
    def has_object_permission(self, request, view, payment):
        return (super(PaymentManager, self).has_permission(request, view) and
                payment.manager == request.user)


class PaymentManagerOrSupervisor(BasePermission):
    def has_object_permission(self, request, view, payment):
        content_type = payment.content_type
        if PaymentManager().has_object_permission(request, view, payment):
            return True
        if content_type.app_label == 'summit' and content_type.model == 'summitanket':
            return IsSummitSupervisorOrHigh().has_object_permission(request, view, payment.purpose.summit)
        if content_type.app_label == 'partnership' and content_type.model in ('partnership', 'deal'):
            return IsPartnerSupervisorOrHigh().has_permission(request, view)
        return False
