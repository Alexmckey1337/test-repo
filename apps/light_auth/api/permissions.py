from rest_framework.permissions import BasePermission

from common.permissions import can_vo_org_ua_key


class CanCreateLightAuth(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the user can create light_auth_user
        """
        return has_light_auth_perm(request.user)

    def has_object_permission(self, request, view, user):
        """
        Checking that the user can create light_auth_user for user
        """
        return has_light_auth_perm(request.user, user)


class CanConfirmPhoneNumberLightAuth(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the user can confirm phone number
        """
        return has_light_auth_perm(request.user)

    def has_object_permission(self, request, view, user):
        """
        Checking that the user can confirm phone number for user
        """
        return has_light_auth_perm(request.user, user)


class CanChangeLightAuthPassword(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the user can change light_auth password
        """
        return can_vo_org_ua_key(request)

    def has_object_permission(self, request, view, obj):
        """
        Checking that the user can change light_auth password
        """
        return can_vo_org_ua_key(request)


class CanVerifyPhoneLightAuth(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the user can verify light_auth phone
        """
        return can_vo_org_ua_key(request)

    def has_object_permission(self, request, view, obj):
        """
        Checking that the user can verify light_auth phone
        """
        return can_vo_org_ua_key(request)


class CanResetPasswordLightAuth(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the user can reset light_auth password
        """
        return can_vo_org_ua_key(request)

    def has_object_permission(self, request, view, obj):
        """
        Checking that the user can reset light_auth password
        """
        return can_vo_org_ua_key(request)


class CanLightLogin(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the user can light_auth login
        """
        return can_vo_org_ua_key(request)

    def has_object_permission(self, request, view, obj):
        """
        Checking that the user can light_auth login
        """
        return can_vo_org_ua_key(request)


def has_light_auth_perm(user, to_user=None):
    if to_user is None:
        return user.is_staff
    return user.is_staff