from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def entry(request):
    return render(request, 'entry.html')

@login_required(login_url='entry')
def events(request):
    return render(request, 'events.html')

@login_required(login_url='entry')
def account(request, id):
    return render(request, 'account.html')

@login_required(login_url='entry')
def account_create(request):
    return render(request, 'account_create.html')

@login_required(login_url='entry')
def account_edit(request, id):
    return render(request, 'account_edit.html')

@login_required(login_url='entry')
def notifications(request):
    return render(request, 'notifications.html')

@login_required(login_url='entry')
def reports(request):
    return render(request, 'reports.html')

@login_required(login_url='entry')
def settings(request):
    return render(request, 'settings.html')

@login_required(login_url='entry')
def settings_disciples(request):
    return render(request, 'settings_disciples.html')

@login_required(login_url='entry')
def settings_events(request):
    return render(request, 'settings_events.html')

from create import create_participations, create_reports
from django.utils import timezone
from datetime import timedelta

@login_required(login_url='entry')
def synchronize(request):
    weekday = timezone.now().weekday() + 1
    create_participations()
    create_reports(weekday)
    return HttpResponse('ok')

