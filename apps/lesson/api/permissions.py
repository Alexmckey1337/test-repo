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


def can_see_lesson_months(user):
    """
    Checking that the ``user`` has the right to see lesson months
    """
    return user.is_leader_or_high


def can_see_lessons(user):
    """
    Checking that the ``user`` has the right to see lessons
    """
    return user.is_leader_or_high


def can_see_lesson(user, lesson):
    """
    Checking that the ``user`` has the right to see ``lesson``
    """
    return user.is_leader_or_high
