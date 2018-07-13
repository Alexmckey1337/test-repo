from rest_framework.permissions import BasePermission


class CanSeeLessonMonths(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see lesson months
        """
        return can_see_lesson_months(request.user)


class CanSeeLessons(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see lessons
        """
        return can_see_lessons(request.user)

    def has_object_permission(self, request, view, lesson):
        """
        Checking that the ``request.user`` has the right to see ``lesson``
        """
        return can_see_lesson(request.user, lesson)


class CanLikeLessons(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to like lessons
        """
        return can_like_lessons(request.user)

    def has_object_permission(self, request, view, lesson):
        """
        Checking that the ``request.user`` has the right to like ``lesson``
        """
        return can_like_lesson(request.user, lesson)


def can_see_lesson_months(user):
    """
    Checking that the ``user`` has the right to see lesson months
    """
    return user.is_leader_or_high or user.is_staff or user.has_operator_perm


def can_see_lessons(user):
    """
    Checking that the ``user`` has the right to see lessons
    """
    return user.is_leader_or_high or user.is_staff or user.has_operator_perm


def can_see_lesson(user, lesson):
    """
    Checking that the ``user`` has the right to see ``lesson``
    """
    return (user.is_leader_or_high and user.hierarchy.level >= lesson.access_level) or user.is_staff or user.has_operator_perm


def can_like_lessons(user):
    """
    Checking that the ``user`` has the right to like lessons
    """
    return user.is_leader_or_high or user.is_staff or user.has_operator_perm


def can_like_lesson(user, lesson):
    """
    Checking that the ``user`` has the right to like ``lesson``
    """
    return (user.is_leader_or_high and user.hierarchy.level >= lesson.access_level) or user.is_staff or user.has_operator_perm
