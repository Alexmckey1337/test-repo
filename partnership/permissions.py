from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsManagerReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and
            request.user.is_partner_manager_or_high and request.method in SAFE_METHODS
        )


class IsSupervisorOrManagerReadOnly(IsManagerReadOnly):
    def has_permission(self, request, view):
        return (
            super(IsSupervisorOrManagerReadOnly, self).has_permission(request, view) or
            request.user and request.user.is_authenticated and request.user.is_partner_supervisor_or_high
        )


class IsDisciplesOf(BasePermission):
    def has_object_permission(self, request, view, account):
        return (
            request.user and request.user.is_authenticated and request.user.is_partner and
            request.user.partnership.disciples.filter(user=account).exists()
        )


class CanSeePartners(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to see list of partners
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high


class CanExportPartnerList(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to export list of partners
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high


class CanSeeDeals(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to see list of deals
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high


class CanCreateDeals(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to create new deal
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high

    def can_create_for_partner(self, user, partner):
        """
        Checking that the ``user`` is partner and he has the right to create deal for certain ``partner``
        """
        user_is_supervisor_or_high = (
            user and user.is_authenticated and user.is_partner_supervisor_or_high)
        if user_is_supervisor_or_high:
            return True
        user_is_manager = user and user.is_authenticated and user.is_partner_manager
        return user_is_manager and user.partnership.disciples.filter(id=partner.id).exists()


class CanUpdatePartner(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to update partners
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high

    def can_update_partner_need(self, user, partner):
        """
        Checking that the ``user`` is partner and he has the right to update need field of certain ``partner``
        """
        user_is_supervisor_or_high = (
            user and user.is_authenticated and user.is_partner_supervisor_or_high)
        if user_is_supervisor_or_high:
            return True
        user_is_manager = user and user.is_authenticated and user.is_partner_manager
        return user_is_manager and user.partnership.disciples.filter(id=partner.id).exists()


class CanUpdateDeals(BasePermission):
    def has_object_permission(self, request, view, deal):
        """
        Checking that the ``request.user`` is partner and he has the right to update ``deal``
        """
        partner = deal.partnership
        user_is_supervisor_or_high = (
            request.user and request.user.is_authenticated and request.user.is_partner_supervisor_or_high)
        if user_is_supervisor_or_high:
            return True
        user_is_manager = request.user and request.user.is_authenticated and request.user.is_partner_manager
        return user_is_manager and request.user.partnership.disciples.filter(id=partner.id).exists()


class CanSeeDealPayments(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to see list of payments by deals
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high


class CanSeePartnerStatistics(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to see statistic of partners
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high


class CanClosePartnerDeal(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to close a deals
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high


class CanReadPartnerPayment(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to read payments by partner
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_manager_or_high


class CanCreatePartnerPayment(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` is partner and he has the right to create a payment by partnership
        """
        return request.user and request.user.is_authenticated and request.user.is_partner_supervisor_or_high


class AccountCanEditPartnerBlock(BasePermission):
    def can_edit(self, current_user, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

        - partnership.is_active
        - partnership.date
        - partnership.value and partnership.currency
        - partnership.responsible
        """
        return current_user.is_partner_supervisor_or_high


class AccountCanSeePartnerBlock(BasePermission):
    def can_see(self, current_user, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see partner block
        """
        return (
            current_user.is_partner_supervisor_or_high or
            current_user.is_ancestor_of(user) or
            current_user.is_partner_responlible_of(user)
        )


class AccountCanSeeDealBlock(BasePermission):
    def can_see(self, current_user, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see deals block
        """
        return True


def can_see_partners(request, view=None):
    """
    Checking that the ``request.user`` is partner and he has the right to see list of partners
    """
    return CanSeePartners().has_permission(request, view)


def can_export_partner_list(request, view=None):
    """
    Checking that the ``request.user`` is partner and he has the right to export list of partners
    """
    return CanExportPartnerList().has_permission(request, view)


def can_see_deals(request, view=None):
    """
    Checking that the ``request.user`` is partner and he has the right to see list of deals
    """
    return CanSeeDeals().has_permission(request, view)


def can_see_partner_stats(request, view=None):
    """
    Checking that the ``request.user`` is partner and he has the right to see statistic of partners
    """
    return CanSeePartnerStatistics().has_permission(request, view)


def can_see_deal_payments(request, view=None):
    """
    Checking that the ``request.user`` is partner and he has the right to see list of payments by deals
    """
    return CanSeeDealPayments().has_permission(request, view)


def can_close_partner_deals(request, view=None):
    """
    Checking that the ``request.user`` is partner and he has the right to close deals of partnership
    """
    return CanClosePartnerDeal().has_permission(request, view)


def can_create_partner_payments(request, view=None):
    """
    Checking that the ``request.user`` is partner and he has the right to create payments by deals
    """
    return CanCreatePartnerPayment().has_permission(request, view)


def can_create_deal_for_partner(user, partner):
    """
    Checking that the ``user`` is partner and he has the right to create deal for certain ``partner``
    """
    return CanCreateDeals().can_create_for_partner(user, partner)


def can_update_partner_need(user, partner):
    """
    Checking that the ``user`` is partner and he has the right to update need field of certain ``partner``
    """
    return CanUpdatePartner().can_update_partner_need(user, partner)


def can_edit_partner_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

    - partnership.is_active
    - partnership.date
    - partnership.value and partnership.currency
    - partnership.responsible
    """
    return AccountCanEditPartnerBlock().can_edit(current_user, user)


def can_see_partner_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see partner block
    """
    return AccountCanSeePartnerBlock().can_see(current_user, user)


def can_see_deal_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see deals block
    """
    return AccountCanSeeDealBlock().can_see(current_user, user)
