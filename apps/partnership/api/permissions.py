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


class CanExportChurchPartnerList(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to export list of church partners
        """
        return can_export_church_partner_list(request.user)


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


class CanSeeChurchPartners(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of church partners
        """
        return can_see_partners(request.user)


class CanUpdateChurchPartner(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to update church partners
        """
        return request.user.is_partner_manager_or_high

    def has_object_permission(self, request, view, church_partner):
        """
        Checking that the ``request.user`` has the right to update ``church_partner``
        """
        return can_update_church_partner(request.user, church_partner.church)


class CanSeeChurchDeals(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of church deals
        """
        return can_see_church_deals(request.user)


class CanUpdateChurchDeals(BasePermission):
    def has_object_permission(self, request, view, church_deal):
        """
        Checking that the ``request.user`` has the right to update ``church_deal``
        """
        return can_update_church_deal(request.user, church_deal)


class CanCreateChurchDeals(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create new church_deal
        """
        return request.user.is_partner_manager_or_high


class CanCreateChurchPartnerPayment(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create payment by church partnership
        """
        return can_create_church_partner_payments(request.user)

    def has_object_permission(self, request, view, church_partner):
        """
        Checking that the ``request.user`` has the right to create payment for certain ``church_partner``
        """
        return can_create_payment_for_church_partner(request.user, church_partner)


class CanSeeChurchDealPayments(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of payments by church deals
        """
        return can_see_church_deal_payments(request.user)


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


class CanUpdateManagersPlan(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to update manager's plan
        """
        return can_set_managers_plan(request.user)


class CanSeeManagerSummary(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see manager's summary
        """
        return can_see_managers_summary(request.user)


class CanCreateUpdatePartnerGroup(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create partner group
        """
        return can_create_partner_group(request.user)

    def has_object_permission(self, request, view, partner_group):
        """
        Checking that the ``request.user`` has the right to update ``partner_group``
        """
        return can_update_partner_group(request.user, partner_group)


class CanCreatePartnerRole(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create partner role
        """
        return can_create_partner_role(request.user)


class CanUpdatePartnerRole(BasePermission):
    def has_object_permission(self, request, view, partner_role):
        """
        Checking that the ``request.user`` has the right to update ``partner_role``
        """
        return can_update_partner_role(request.user, partner_role)


class CanDeletePartnerRole(BasePermission):
    def has_object_permission(self, request, view, partner_role):
        """
        Checking that the ``request.user`` has the right to delete ``partner_role``
        """
        return can_delete_partner_role(request.user, partner_role)


class CanSeePartnerGroups(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see partner groups
        """
        return can_see_partner_groups(request.user)


def can_see_partners(user):
    """
    Checking that the ``user`` has the right to see list of partners
    """
    return user.is_partner_manager_or_high


def can_see_partner_summary(user):
    """
    Checking that the ``user`` has the right to see partner summary
    """
    return user.is_partner_director or user.is_staff


def can_export_partner_list(user):
    """
    Checking that the ``user`` has the right to export list of partners
    """
    return user.is_partner_manager_or_high


def can_export_church_partner_list(user):
    """
    Checking that the ``user`` has the right to export list of church partners
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


def can_see_church_deal_payments(user):
    """
    Checking that the ``user`` has the right to see list of payments by church deals
    """
    return user.is_partner_manager_or_high


def can_close_partner_deals(user):
    """
    Checking that the ``request.user`` has the right to close deals of partnership
    """
    return user.is_partner_manager_or_high


def can_close_church_partner_deals(user):
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


def can_create_church_partner_payments(user):
    """
    Checking that the ``request.user`` has the right to create payments by church deals
    """
    return user.is_partner_supervisor_or_high


def can_create_payment_for_church_partner(user, church_partner):
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
    return user.is_partner_manager and user.partner_disciples.filter(id=partner.id).exists()


def can_update_partner_need(user, partner):
    """
    Checking that the ``user`` has the right to update need field of certain ``partner``
    """
    if user.is_partner_supervisor_or_high:
        return True
    return user.is_partner_manager and user.partner_disciples.filter(id=partner.id).exists()


def can_update_partner(user, partner_user):
    """
    Checking that the ``user`` has the right to update partnership of ``partner_user``
    """
    if user.is_partner_supervisor_or_high:
        return True
    return user.is_partner_manager and user.partner_disciples.filter(user=partner_user).exists()


def can_update_church_partner(user, church):
    """
    Checking that the ``user`` has the right to update partnership of ``church_partner``
    """
    if user.is_partner_supervisor_or_high:
        return True
    return user.is_partner_manager and user.church_partner_disciples.filter(church=church).exists()


def can_create_church_deal_for_partner(user, church_partner):
    """
    Checking that the ``user`` has the right to create deal for certain ``partner``
    """
    if user.is_partner_supervisor_or_high:
        return True
    return user.is_partner_manager and user.church_partner_disciples.filter(id=church_partner.id).exists()


def can_see_church_partners(user):
    """
    Checking that the ``user`` has the right to see list of church partners
    """
    return user.is_partner_manager_or_high


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
    return user.is_partner_manager and user.partner_disciples.filter(id=partner.id).exists()


def can_see_church_deals(user):
    """
    Checking that the ``user`` has the right to see list of church deals
    """
    return user.is_partner_manager_or_high


def can_update_church_deal(user, church_deal):
    """
    Checking that the ``user`` has the right to update ``church_deal``
    """
    if user.is_partner_supervisor_or_high:
        return True
    partner = church_deal.partnership
    return user.is_partner_manager and user.church_partner_disciples.filter(id=partner.id).exists()


def can_see_partner_payments(user):
    """
    Checking that the ``user`` has the right to see partner's payments
    """
    return user.is_partner_manager_or_high


def can_set_managers_plan(user):
    """
    Checking that the ``user`` has the right to update manager's plan
    """
    return user.is_partner_director


def can_see_managers_summary(user):
    """
    Checking that the ``user`` has the right to see manager's summary
    """
    return user.is_partner_director or user.is_staff


def can_see_partner_groups(user):
    """
    Checking that the ``user`` has the right to see partner groups
    """
    return user.is_partner_manager_or_high or user.is_staff


def can_create_partner_group(user):
    """
    Checking that the ``user`` has the right to create partner group
    """
    return user.is_partner_supervisor_or_high or user.is_staff


def can_update_partner_group(user, partner_group):
    """
    Checking that the ``user`` has the right to update ``partner_group``
    """
    return user.is_partner_supervisor_or_high or user.is_staff


def can_create_partner_role(user):
    """
    Checking that the ``user`` has the right to create partner role
    """
    return user.is_partner_supervisor_or_high


def can_update_partner_role(user, partner_role):
    """
    Checking that the ``user`` has the right to update ``partner_role``
    """
    return user.is_partner_supervisor_or_high


def can_delete_partner_role(user, partner_role):
    """
    Checking that the ``user`` has the right to delete ``partner_role``
    """
    return user.is_partner_supervisor_or_high
