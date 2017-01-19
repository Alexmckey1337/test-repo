# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from account.models import CustomUser
from hierarchy.models import Department, Hierarchy
from location.models import Country, Region, City
from partnership.models import Partnership
from status.models import Division
from summit.models import SummitType
from tv_crm.views import sync_user_call
from group.models import Church, HomeGroup
from django.db.models import Count


def entry(request):
    return render(request, 'login/login.html')


def edit_pass(request, activation_key=None):
    return render(request, 'login/editpass.html')


@login_required(login_url='entry')
def events(request):
    return render(request, 'event/events.html')


@login_required(login_url='entry')
def deals(request):
    return render(request, 'partner/deals.html')


@login_required(login_url='entry')
def partner_stats(request):
    partner = request.user.partnership
    if not partner or partner.level > Partnership.MANAGER:
        raise Http404('Статистику можно просматривать только менеджерам.')
    return render(request, 'partner/partner_stats.html')


@login_required(login_url='entry')
def account(request, id):
    if not request.user.is_staff and not request.user.get_descendants(include_self=True).filter(id=id).exists():
        return redirect('/')
    ctx = {
        'account': get_object_or_404(CustomUser, pk=id)
    }
    return render(request, 'account/anketa.html', context=ctx)


@login_required(login_url='entry')
def account_edit(request, user_id):
    if not request.user.is_staff and not request.user.get_descendants(include_self=True).filter(id=user_id).exists():
        return redirect('/')
    user = get_object_or_404(CustomUser, pk=user_id)
    ctx = {
        'account': user,
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'divisions': Division.objects.all(),
        'countries': Country.objects.all(),
        'regions': Region.objects.filter(country__title=user.country),
        'cities': City.objects.filter(region__title=user.region),
        'partners': Partnership.objects.all(),
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
        'summit_type': SummitType.objects.get(id=summit_id)
    }
    return render(request, 'summit/summit_info.html', context=ctx)


@login_required(login_url='entry')
def churches(request):
    user = request.user
    if not user.is_staff and user.hierarchy.level < 2:
        raise Http404('У Вас нет прав для просмотра данной страницы.')
    ctx = {}
    return render(request, 'group/churches.html', context=ctx)


@login_required(login_url='entry')
def church_detail(request, church_id):
    user = request.user
    church = get_object_or_404(Church, id=church_id)

    if not user.is_staff and user.hierarchy.level < 1:
        raise Http404('У Вас нет прав для просмотра данной страницы.')

    ctx = {
        'church': church,
        'parishioners_count': church.users.filter(hierarchy__level=0).count(),
        'leaders_count': church.users.filter(hierarchy__level=1).count(),
        'home_groups_count': church.home_group.count(),
        'fathers_count': church.users.filter(spiritual_level=3).count() + HomeGroup.objects.filter(
            church__id=church_id).filter(users__spiritual_level=3).count(),
        'juniors_count': church.users.filter(spiritual_level=2).count() + HomeGroup.objects.filter(
            church__id=church_id).filter(users__spiritual_level=2).count(),
        'babies_count': church.users.filter(spiritual_level=1).count() + HomeGroup.objects.filter(
            church__id=church_id).filter(users__spiritual_level=1).count(),
        'partners_count': church.users.filter(partnership__is_active=True).count(),
    }
    return render(request, 'group/church_detail.html', context=ctx)


@login_required(login_url='entry')
def home_group_detail(request, church_id, group_id):
    home_group = HomeGroup.objects.filter(church=church_id).get(id=group_id)

    ctx = {
        'home_group': home_group,
        'opening_date': home_group.opening_date,
        'church': home_group.church,
        'leader': home_group.leader,
        'address': home_group.address,
        'phone_number': home_group.phone_number,
        'website': home_group.website,
        'users_count': home_group.users.count(),
        'fathers_count': home_group.users.filter(spiritual_level=3).count(),
        'juniors_count': home_group.users.filter(spiritual_level=2).count(),
        'babies_count': home_group.users.filter(spiritual_level=1).count(),
        'partners_count': home_group.users.filter(partnership__is_active=True).count(),
    }
    return render(request, 'group/group_detail.html', context=ctx)


@login_required(login_url='entry')
def index(request):
    user = request.user
    ctx = {
        'departments': Department.objects.all(),
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
    return render(request, 'database/main.html', context=ctx)


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
    sync_user_call()
    return HttpResponse('ok')
