from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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
def account(request, id):
    return render(request, 'anketa.html')


@login_required(login_url='entry')
def account_edit(request, user_id):
    return render(request, 'edit.html')


@login_required(login_url='entry')
def summits(request):
    return render(request, 'summits.html')


@login_required(login_url='entry')
def summit_info(request, summit_id):
    return render(request, 'summit_info.html')


@login_required(login_url='entry')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='entry')
def reports(request):
    return render(request, 'reports.html')


@login_required(login_url='entry')
def event_info(request):
    return render(request, 'event_info.html')



from create import create_participations, create_reports
from django.utils import timezone
from datetime import timedelta

@login_required(login_url='entry')
def synchronize(request):
    weekday = timezone.now().weekday() + 1
    #create_participations()
    #create_reports(weekday)
    sync_user_call()
    return HttpResponse('ok')
