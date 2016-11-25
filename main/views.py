# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect

from partnership.models import Partnership
from tv_crm.views import sync_user_call


def entry(request):
    return render(request, 'entry.html')


def edit_pass(request, activation_key=None):
    return render(request, 'editpass.html')


@login_required(login_url='entry')
def events(request):
    return render(request, 'events.html')


@login_required(login_url='entry')
def deals(request):
    return render(request, 'deals.html')


@login_required(login_url='entry')
def partner_stats(request):
    partner = request.user.partnership
    if not partner or partner.level > Partnership.MANAGER:
        raise Http404('Статистику можно просматривать только менеджерам.')
    return render(request, 'partner_stats.html')


@login_required(login_url='entry')
def account(request, id):
    return render(request, 'anketa.html')


@login_required(login_url='entry')
def account_edit(request, user_id):
    if not request.user.is_staff:
        if user_id:
            return redirect(reverse('account', args=[user_id]))
        return redirect('/')
    return render(request, 'edit.html')


@login_required(login_url='entry')
def summits(request):
    return render(request, 'summits.html')


@login_required(login_url='entry')
def summit_info(request, summit_id):
    return render(request, 'summit_info.html')


@login_required(login_url='entry')
def index(request):
    return render(request, 'main.html')


@login_required(login_url='entry')
def reports(request):
    return render(request, 'reports.html')


@login_required(login_url='entry')
def event_info(request):
    return render(request, 'event_info.html')


@login_required(login_url='entry')
def synchronize(request):
    # weekday = timezone.now().weekday() + 1
    # create_participations()
    # create_reports(weekday)
    sync_user_call()
    return HttpResponse('ok')
