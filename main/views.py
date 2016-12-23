# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from account.models import CustomUser
from event.models import MeetingType
from hierarchy.models import Department
from partnership.models import Partnership
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
        'meeting_type': get_object_or_404(MeetingType, code=code),
    }
    if request.user.hierarchy.level > 1:
        ctx['leaders'] = request.user.get_descendant_leaders()
    return render(request, 'event/meeting_create_report.html', context=ctx)


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
    return render(request, 'account/edit.html')


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
    ctx = {
        'departments': Department.objects.all()
    }
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
