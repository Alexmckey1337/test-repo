# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import BasePermission, SAFE_METHODS


class PaymentPermission(BasePermission):
    def has_object_permission(self, request, view, purpose):
        purpose_model = view.get_queryset().model
        content_type = ContentType.objects.get_for_model(purpose_model)
        if content_type.app_label == 'summit' and content_type.model == 'summitanket':
            return (
                (request.user.is_summit_consultant_or_high(purpose) and request.method in SAFE_METHODS) or
                request.user.is_summit_supervisor_or_high(purpose))
        if content_type.app_label == 'partnership' and content_type.model == 'partnership':
            return (
                (request.user.is_partner_manager_or_high and request.method in SAFE_METHODS and
                 request.user.is_partner_responsible_of(purpose.user)) or
                request.user.is_partner_supervisor_or_high)
        if content_type.app_label == 'partnership' and content_type.model == 'deal':
            return (
                (request.user.is_partner_manager_or_high and request.method in SAFE_METHODS and
                 request.user.is_partner_responsible_of(purpose.partnership.user)) or
                request.user.is_partner_supervisor_or_high)

        if content_type.model in ('churchreport', 'churchreportpastor'):
            # Temporary solution. Permissions like a partnerships.
            return (
                (request.user.is_partner_manager_or_high and request.method in SAFE_METHODS and
                 request.user.is_partner_responsible_of(purpose.partnership.user)) or
                request.user.is_partner_supervisor_or_high)
        return False


class PaymentManager(BasePermission):
    def has_object_permission(self, request, view, payment):
        return payment.manager == request.user


class PaymentManagerOrSupervisor(BasePermission):
    def has_object_permission(self, request, view, payment):
        if PaymentManager().has_object_permission(request, view, payment):
            return True

        content_type = payment.content_type
        if content_type and content_type.app_label == 'summit' and content_type.model == 'summitanket':
            return request.user.is_summit_supervisor_or_high(payment.purpose.summit)
        if content_type and content_type.app_label == 'partnership' and content_type.model in ('partnership', 'deal'):
            return request.user.is_partner_supervisor_or_high
        if content_type and content_type.model in ('churchreport', 'churchreportpastor'):
            return request.user.is_partner_supervisor_or_high
        return False
