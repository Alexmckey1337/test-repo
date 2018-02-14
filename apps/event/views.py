from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from apps.account.models import CustomUser
from apps.event.models import MeetingType, Meeting, ChurchReport
from apps.group.models import Church, HomeGroup
from apps.hierarchy.models import Department
from apps.payment.models import Currency


@login_required(login_url='entry')
def meeting_report_list(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    owners = CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct()
    churches = Church.objects.all()
    hg = HomeGroup.objects.all()
    ctx = {
        'departments': Department.objects.all(),
        'churches': churches,
        'church_options': [{'id': c.pk, 'title': c.get_title} for c in churches],
        'home_groups': hg,
        'hg_options': [{'id': h.pk, 'title': h.get_title} for h in hg],
        'owners': owners,
        'owner_options': [{'id': u.pk, 'title': u.fullname} for u in owners],
        'types': MeetingType.objects.all()
    }

    return render(request, 'event/home_reports.html', context=ctx)


@login_required(login_url='entry')
def meeting_report_detail(request, pk):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    ctx = {
        'home_report': get_object_or_404(Meeting, pk=pk),
        'leader': request.user,
    }
    return render(request, 'event/home_report_detail.html', context=ctx)


@login_required(login_url='entry')
def meeting_report_statistics(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    owners = CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct()
    churches = Church.objects.all()
    hg = HomeGroup.objects.all()
    ctx = {
        'departments': Department.objects.all(),
        'churches': churches,
        'church_options': [{'id': c.pk, 'title': c.get_title} for c in churches],
        'home_groups': hg,
        'hg_options': [{'id': h.pk, 'title': h.get_title} for h in hg],
        'owners': owners,
        'owner_options': [{'id': u.pk, 'title': u.fullname} for u in owners],
        'types': MeetingType.objects.all()
    }

    return render(request, 'event/home_statistics.html', context=ctx)


@login_required(login_url='entry')
def meetings_summary(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')
    ctx = {
        'departments': Department.objects.all()
    }

    return render(request, 'event/meetings_summary.html', context=ctx)


@login_required(login_url='entry')
def church_report_list(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 2):
        return redirect('/')

    ctx = {
        'departments': Department.objects.all(),
        'deal_status_options': [
            {'id': '0', 'title': 'Hе оплачена'},
            {'id': '1', 'title': 'Оплачена частично'},
            {'id': '2', 'title': 'Оплачена полностью'},
        ],
    }

    return render(request, 'event/church_reports.html', context=ctx)


@login_required(login_url='entry')
def church_report_detail(request, pk):
    if not request.user.hierarchy or request.user.hierarchy.level < 2:
        return redirect('/')

    ctx = {
        'church_report': get_object_or_404(ChurchReport, pk=pk),
        'pastor': request.user,
    }

    return render(request, 'event/church_report_detail.html', context=ctx)


@login_required(login_url='entry')
def church_statistics(request):
    if not request.user.hierarchy or request.user.hierarchy.level < 2:
        return redirect('/')

    ctx = {
        'departments': Department.objects.all(),
    }

    return render(request, 'event/church_statistics.html', context=ctx)


@login_required(login_url='entry')
def reports_summary(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 2):
        return redirect('/')
    ctx = {
        'departments': Department.objects.all()
    }

    return render(request, 'event/reports_summary.html', context=ctx)


@login_required(login_url='entry')
def report_payments(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 2):
        return redirect('/')
    ctx = {
        'currencies': Currency.objects.all(),
        'currency_options': [{'id': c.id, 'title': c.name} for c in Currency.objects.all()],
        'managers': CustomUser.objects.filter(partner_role__level__lte=2).distinct(),
        'manager_options': [{'id': u.pk, 'title': u.fullname} for u in CustomUser.objects.filter(
            partner_role__level__lte=2).distinct()],
        'pastors': CustomUser.objects.filter(hierarchy__level__gt=1),
        'pastor_options': [{'id': u.pk, 'title': u.fullname} for u in CustomUser.objects.filter(
            hierarchy__level__gt=1)],
    }

    return render(request, 'event/report_payments.html', context=ctx)
