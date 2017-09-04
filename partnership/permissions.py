# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission


class CanSeePartners(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of partners
        """
        return can_see_partners(request.user)


class CanExportPartnerList(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to export list of partners
        """
        return can_export_partner_list(request.user)


class CanSeeDeals(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of deals
        """
        return can_see_deals(request.user)


class CanCreateDeals(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create new deal
        """
        return request.user.is_partner_manager_or_high


class CanUpdatePartner(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to update partners
        """
        return request.user.is_partner_manager_or_high

    def has_object_permission(self, request, view, partner):
        """
        Checking that the ``request.user`` has the right to update ``partner``
        """
        return can_update_partner(request.user, partner.user)


class CanUpdateDeals(BasePermission):
    def has_object_permission(self, request, view, deal):
        """
        Checking that the ``request.user`` has the right to update ``deal``
        """
        return can_update_deal(request.user, deal)


class CanSeeDealPayments(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of payments by deals
        """
        return can_see_deal_payments(request.user)


class CanSeePartnerStatistics(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see statistic of partners
        """
        return can_see_partner_stats(request.user)


class CanSeePartnerPayments(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see partner's payments
        """
        return can_see_partner_payments(request.user)


class CanCreatePartnerPayment(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create payment by partnership
        """
        return can_create_partner_payments(request.user)

    def has_object_permission(self, request, view, partner):
        """
        Checking that the ``request.user`` has the right to create payment for certain ``partner``
        """
        return can_create_payment_for_partner(request.user, partner)


def can_see_partners(user):
    """
    Checking that the ``user`` has the right to see list of partners
    """
    return user.is_partner_manager_or_high


def can_see_partner_summary(user):
    """
    Checking that the ``user`` has the right to see partner summary
    """
    return user.is_leader_or_high


def can_export_partner_list(user):
    """
    Checking that the ``user`` has the right to export list of partners
    """
    return user.is_partner_manager_or_high


def can_see_deals(user):
    """
    Checking that the ``user`` has the right to see list of deals
    """
    return user.is_partner_manager_or_high


def can_see_partner_stats(user):
    """
    Checking that the ``user`` has the right to see statistic of partners
    """
    return user.is_partner_manager_or_high


def can_see_deal_payments(user):
    """
    Checking that the ``user`` has the right to see list of payments by deals
    """
    return user.is_partner_manager_or_high


def can_close_partner_deals(user):
    """
    Checking that the ``request.user`` has the right to close deals of partnership
    """
    return user.is_partner_manager_or_high


def can_create_partner_payments(user):
    """
    Checking that the ``request.user`` has the right to create payments by deals
    """
    return user.is_partner_supervisor_or_high


def can_create_payment_for_partner(user, partner):
    """
    Checking that the ``request.user`` has the right to create payment for certain ``partner``
    """
    return user.is_partner_supervisor_or_high


def can_create_deal_for_partner(user, partner):
    """
    Checking that the ``user`` has the right to create deal for certain ``partner``
    """
    if user.is_partner_supervisor_or_high:
        return True
    return user.is_partner_manager and user.partnership.disciples.filter(id=partner.id).exists()


def can_update_partner_need(user, partner):
    """
    Checking that the ``user`` has the right to update need field of certain ``partner``
    """
    if user.is_partner_supervisor_or_high:
        return True
    return user.is_partner_manager and user.partnership.disciples.filter(id=partner.id).exists()


def can_update_partner(user, partner_user):
    """
    Checking that the ``user`` has the right to update partnership of ``partner_user``
    """
    if user.is_partner_supervisor_or_high:
        return True
    return user.is_partner_manager and user.partnership.disciples.filter(user=partner_user).exists()


def can_edit_partner_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

    - partnership.is_active
    - partnership.date
    - partnership.value and partnership.currency
    - partnership.responsible
    """
    return current_user.is_partner_supervisor_or_high


def can_see_partner_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see partner block
    """
    return (
        current_user.is_partner_supervisor_or_high or
        user.is_descendant_of(current_user) or
        current_user.is_partner_responlible_of(user)
    )


def can_see_deal_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see deals block
    """
    return True


def can_update_deal(user, deal):
    """
    Checking that the ``user`` has the right to update ``deal``
    """
    if user.is_partner_supervisor_or_high:
        return True
    partner = deal.partnership
    return user.is_partner_manager and user.partnership.disciples.filter(id=partner.id).exists()


def can_see_partner_payments(user):
    """
    Checking that the ``user`` has the right to see partner's payments
    """
    return user.is_partner_manager_or_high
