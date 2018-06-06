from django.conf import settings
from rest_framework.permissions import BasePermission


class CanCreateProposal(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the user can create proposal
        """
        return can_vo_org_ua_key(request)


class CanReceiveProposal(BasePermission):
    def has_object_permission(self, request, view, proposal):
        """
        Checking that the user can receive proposal
        """
        return can_receive_proposal(request.user, proposal)


class CanReopenProposal(BasePermission):
    def has_object_permission(self, request, view, proposal):
        """
        Checking that the user can reopen proposal
        """
        return can_reopen_proposal(request.user, proposal)


class CanRejectProposal(BasePermission):
    def has_object_permission(self, request, view, proposal):
        """
        Checking that the user can reject proposal
        """
        return can_reject_proposal(request.user, proposal)


class CanProcessProposal(BasePermission):
    def has_object_permission(self, request, view, proposal):
        """
        Checking that the user can process proposal
        """
        return can_process_proposal(request.user, proposal)


def can_vo_org_ua_key(request):
    return settings.VO_ORG_UA_TOKEN == request.META.get(settings.VO_ORG_UA_TOKEN_NAME, '')


def can_see_proposal(user, proposal):
    """
    Checking that the user can see  proposal
    """
    return user.is_proposal_manager or user.is_staff


def can_see_proposal_list(user):
    """
    Checking that the user can see list of proposals
    """
    return user.is_proposal_manager or user.is_staff


def can_receive_proposal(user, proposal):
    """
    Checking that the user can receive proposal
    """
    return user.is_proposal_manager and (
        proposal.manager == user or not proposal.manager
    )


def can_reopen_proposal(user, proposal):
    """
    Checking that the user can reopen proposal
    """
    return user.is_proposal_manager and proposal.manager == user


def can_reject_proposal(user, proposal):
    """
    Checking that the user can reject proposal
    """
    return user.is_proposal_manager and proposal.manager == user


def can_process_proposal(user, proposal):
    """
    Checking that the user can process proposal
    """
    return user.is_proposal_manager and proposal.manager == user
