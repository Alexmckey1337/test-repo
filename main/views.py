# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
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
    ctx = {
        'account': get_object_or_404(CustomUser, pk=id)
    }
    return render(request, 'account/anketa.html', context=ctx)


@login_required(login_url='entry')
def account_edit(request, user_id):
    if not request.user.is_staff:
        if user_id:
            return redirect(reverse('account', args=[user_id]))
        return redirect('/')
    if not request.user.get_descendants(include_self=True).filter(id=user_id).exists():
        if user_id:
            return redirect(reverse('account', args=[user_id]))
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
