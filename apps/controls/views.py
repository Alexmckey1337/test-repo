from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.hierarchy.models import Hierarchy
from apps.payment.models import Currency
from apps.summit.models import SummitType
from apps.zmail.models import ZMailTemplate


@login_required(login_url='entry')
def db_access_list(request):
    if not request.user.is_staff:
        return redirect('/')

    ctx = {
        'hierarchies': Hierarchy.objects.all()
    }

    return render(request, 'controls/db_access_list.html', context=ctx)


@login_required(login_url='entry')
def db_access_detail(request, pk):
    if not request.user.is_staff:
        return redirect('/')

    ctx = {
        'payment_status_options': [
            {'id': '0', 'title': 'Hе оплачена'},
            {'id': '1', 'title': 'Оплачена частично'},
            {'id': '2', 'title': 'Оплачена полностью'},
        ]
    }

    return render(request, 'controls/db_access_detail.html', context=ctx)


@login_required(login_url='entry')
def summit_panel_list(request):
    if not request.user.is_staff:
        return redirect('/')

    ctx = {
        'currencies': Currency.objects.all(),
        'zmail_templates': ZMailTemplate.objects.all(),
        'summit_types': SummitType.objects.all(),
        'status_options': [{'id': 'open', 'title': 'Открытые'}, {'id': 'close', 'title': 'Закрытые'}]
    }

    return render(request, 'controls/summit_panel_list.html', context=ctx)
