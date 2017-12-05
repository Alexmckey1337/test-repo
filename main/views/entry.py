from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from account.models import CustomUser
from hierarchy.models import Department, Hierarchy
from summit.models import SummitType


__all__ = ['entry', 'index', 'restore', 'edit_pass']


@login_required(login_url='entry')
def index(request):
    user = request.user
    ctx = {
        'departments': Department.objects.all(),
        'summits': SummitType.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'current_user': user
    }

    if user.is_staff:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    elif not user.hierarchy:
        ctx['masters'] = list()
    elif user.hierarchy.level < 2:
        ctx['masters'] = user.__class__.get_tree(user).filter(is_active=True, hierarchy__level__gte=1)
    else:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    return render(request, 'home/main.html', context=ctx)


def entry(request):
    return render(request, 'login/login.html')


def restore(request):
    return render(request, 'login/restore_password.html')


def edit_pass(request, activation_key=None):
    return render(request, 'login/edit_password.html')
