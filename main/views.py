# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from account.models import CustomUser
from event.models import MeetingType
from hierarchy.models import Department
from account.permissions import CanAccountObjectRead, CanAccountObjectEdit
from group.models import Church, HomeGroup
from hierarchy.models import Department, Hierarchy
from location.models import Country, Region, City
from partnership.models import Partnership
from status.models import Division
from summit.models import SummitType
from payment.models import Currency


def entry(request):
    return render(request, 'login/login.html')


def edit_pass(request, activation_key=None):
    return render(request, 'login/editpass.html')


@login_required(login_url='entry')
def events(request):
    return render(request, 'event/events.html')


@login_required(login_url='entry')
def meeting_types(request):
    ctx = {
        'meeting_types': MeetingType.objects.all(),
    }
    return render(request, 'event/meeting_types.html', context=ctx)


@login_required(login_url='entry')
def meeting_type_detail(request, code):
    ctx = {
        'meeting_type': get_object_or_404(MeetingType, code=code),
    }
    return render(request, 'event/meeting_type_detail.html', context=ctx)


@login_required(login_url='entry')
def meeting_report(request, code):
    if not request.user.hierarchy or request.user.hierarchy.level < 1:
        return redirect('/')
    ctx = {
        'leaders': CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct(),
        'meeting_type': get_object_or_404(MeetingType, code=code),
    }
    return render(request, 'event/meeting_report_create.html', context=ctx)


@login_required(login_url='entry')
def partner(request):
    ctx = {
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
    }
    return render(request, 'partner/partners.html', context=ctx)


@login_required(login_url='entry')
def deals(request):
    return render(request, 'partner/deals.html')


@login_required(login_url='entry')
def stats(request):
    return render(request, 'partner/stats.html')


@login_required(login_url='entry')
def partner_stats(request):
    partner = request.user.partnership
    if not partner or partner.level > Partnership.MANAGER:
        raise Http404('Статистику можно просматривать только менеджерам.')
    return render(request, 'partner/partner_stats.html')


@login_required(login_url='entry')
def account(request, id):
    user = get_object_or_404(CustomUser, pk=id)
    has_perm = CanAccountObjectRead().has_object_permission(request, None, user)
    if not has_perm:
        raise PermissionDenied
    ctx = {
        'account': user
    }
    return render(request, 'account/anketa.html', context=ctx)


@login_required(login_url='entry')
def account_edit(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    has_perm = CanAccountObjectEdit().has_object_permission(request, None, user)
    currencies = Currency.objects.all()
    if not has_perm:
        if user_id:
            get_object_or_404(CustomUser, pk=user_id)
            return redirect(reverse('account', args=(user_id,)))
        raise PermissionDenied
    ctx = {
        'account': user,
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'divisions': Division.objects.all(),
        'countries': Country.objects.all(),
        'regions': Region.objects.filter(country__title=user.country),
        'cities': City.objects.filter(region__title=user.region),
        'partners': Partnership.objects.filter(level__lte=Partnership.MANAGER),
        'currencies': currencies
    }
    return render(request, 'account/edit.html', context=ctx)


@login_required(login_url='entry')
def summits(request):
    ctx = {
        'summit_types': SummitType.objects.exclude(id=3)
    }
    return render(request, 'summit/summits.html', context=ctx)


@login_required(login_url='entry')
def summit_info(request, summit_id):
    ctx = {
        'departments': Department.objects.all(),
        'summit_type': SummitType.objects.get(id=summit_id),
    }
    return render(request, 'summit/summit_info.html', context=ctx)


@login_required(login_url='entry')
def churches(request):
    user = request.user
    if not user.is_staff and user.hierarchy.level < 1:
        raise Http404('У Вас нет прав для просмотра данной страницы.')
    ctx = {
        'departments': Department.objects.all(),
        'pastors': CustomUser.objects.filter(hierarchy__level__gt=1),
    }
    return render(request, 'database/churches.html', context=ctx)


@login_required(login_url='entry')
def church_detail(request, church_id):
    user = request.user
    church = get_object_or_404(Church, id=church_id)
    currencies = Currency.objects.all()
    if not user.is_staff and user.hierarchy.level < 1:
        raise Http404('У Вас нет прав для просмотра данной страницы.')

    ctx = {
        'church': church,
        'pastors': CustomUser.objects.filter(hierarchy__level__gt=1),
        'church_users': church.users.count(),
        'church_all_users': church.users.count() + HomeGroup.objects.filter(church_id=church_id).aggregate(
            home_users=Count('users'))['home_users'],
        'parishioners_count': church.users.filter(hierarchy__level=0).count(),
        'leaders_count': church.users.filter(hierarchy__level=1).count(),
        'home_groups_count': church.home_group.count(),
        'fathers_count': church.users.filter(spiritual_level=CustomUser.FATHER).count() + HomeGroup.objects.filter(
            church__id=church_id).filter(users__spiritual_level=3).count(),
        'juniors_count': church.users.filter(spiritual_level=CustomUser.JUNIOR).count() + HomeGroup.objects.filter(
            church__id=church_id).filter(users__spiritual_level=2).count(),
        'babies_count': church.users.filter(spiritual_level=CustomUser.BABY).count() + HomeGroup.objects.filter(
            church__id=church_id).filter(users__spiritual_level=1).count(),
        'partners_count': church.users.filter(partnership__is_active=True).count(),
        'currencies': currencies
    }
    return render(request, 'group/church_detail.html', context=ctx)


@login_required(login_url='entry')
def home_groups(request):
    user = request.user
    if not user.is_staff and user.hierarchy.level < 1:
        raise Http404('У Вас нет прав для просмотра данной страницы.')
    ctx = {
        'churches': Church.objects.all(),
        'leaders': CustomUser.objects.filter(hierarchy__level__gt=0),
    }
    return render(request, 'database/home_groups.html', context=ctx)


@login_required(login_url='entry')
def home_group_detail(request, group_id):
    user = request.user
    home_group = get_object_or_404(HomeGroup, id=group_id)
    if not user.is_staff and user.hierarchy.level < 1:
        raise Http404('У Вас нет прав для просмотра данной страницы.')

    ctx = {
        'home_group': home_group,
        'users_count': home_group.users.count(),
        'fathers_count': home_group.users.filter(spiritual_level=CustomUser.FATHER).count(),
        'juniors_count': home_group.users.filter(spiritual_level=CustomUser.JUNIOR).count(),
        'babies_count': home_group.users.filter(spiritual_level=CustomUser.BABY).count(),
        'partners_count': home_group.users.filter(partnership__is_active=True).count(),
    }
    return render(request, 'group/home_group_detail.html', context=ctx)


@login_required(login_url='entry')
def people(request):
    user = request.user
    currencies = Currency.objects.all()
    ctx = {
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'currencies': currencies
    }
    if user.is_staff:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    elif not user.hierarchy:
        ctx['masters'] = list()
    elif user.hierarchy.level < 2:
        ctx['masters'] = user.get_descendants(include_self=True).filter(is_active=True, hierarchy__level__gte=1)
    else:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    return render(request, 'database/people.html', context=ctx)


@login_required(login_url='entry')
def index(request):
    user = request.user
    ctx = {
        'departments': Department.objects.all(),
        'summits': SummitType.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
    }
    if user.is_staff:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    elif not user.hierarchy:
        ctx['masters'] = list()
    elif user.hierarchy.level < 2:
        ctx['masters'] = user.get_descendants(include_self=True).filter(is_active=True, hierarchy__level__gte=1)
    else:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    return render(request, 'home/main.html', context=ctx)


@login_required(login_url='entry')
def reports(request):
    return render(request, 'report/reports.html')


@login_required(login_url='entry')
def event_info(request):
    return render(request, 'event/event_info.html')


@login_required(login_url='entry')
def synchronize(request):
    # weekday = timezone.now().weekday() + 1
    # create_participations()
    # create_reports(weekday)
    return HttpResponse('ok')
