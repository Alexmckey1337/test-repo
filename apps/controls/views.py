from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from apps.payment.models import Currency
from apps.zmail.models import ZMailTemplate
from apps.summit.models import SummitType


@login_required(login_url='entry')
def db_access_list(request):
    if not request.user.is_staff:
        return redirect('/')

    ctx = {}

    return render(request, 'controls/db_access_list.html', context=ctx)


@login_required(login_url='entry')
def db_access_detail(request, pk):
    if not request.user.is_staff:
        return redirect('/')

    ctx = {}

    return render(request, 'controls/db_access_detail.html', context=ctx)


@login_required(login_url='entry')
def summit_panel_list(request):
    if not request.user.is_staff:
        return redirect('/')

    ctx = {
        'currencies': Currency.objects.all(),
        'zmail_templates': ZMailTemplate.objects.all(),
        'summit_types': SummitType.objects.all()
    }

    return render(request, 'controls/summit_panel_list.html', context=ctx)