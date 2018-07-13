from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.account.models import CustomUser
from apps.event.models import MeetingType, Meeting, ChurchReport
from apps.group.models import Church, HomeGroup
from apps.hierarchy.models import Department, Hierarchy
from apps.payment.models import Currency


@login_required(login_url='entry')
def meeting_report_list(request):
    if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    owners = CustomUser.objects.filter(home_group__leader__isnull=False).distinct()
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
    if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    ctx = {
        'home_report': get_object_or_404(Meeting, pk=pk),
        'leader': request.user,
    }
    return render(request, 'event/home_report_detail.html', context=ctx)


@login_required(login_url='entry')
def meeting_report_statistics(request):
    if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    owners = CustomUser.objects.filter(home_group__leader__isnull=False).distinct()
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
    if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')
    ctx = {
        'departments': Department.objects.all()
    }

    return render(request, 'event/meetings_summary.html', context=ctx)


class CanSeeUnstableUserListMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 1):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UnstableUserListView(LoginRequiredMixin, CanSeeUnstableUserListMixin, TemplateView):
    template_name = 'event/users.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        extra_ctx = {
            'departments': Department.objects.all(),
            'churches': Church.objects.all(),
            'hgs': HomeGroup.objects.all(),
            'sex_options': [
                {'id': 'male', 'title': _('Мужчина')},
                {'id': 'female', 'title': _('Женщина')},
            ],
            'meeting_type_options': [{'id': m.id, 'title': m.name} for m in MeetingType.objects.all()],
            'hierarchies_options': [{'id': m.code, 'title': m.title} for m in Hierarchy.objects.all()],
        }
        ctx.update(extra_ctx)

        return ctx


@login_required(login_url='entry')
def church_report_list(request):
    if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 2):
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
    if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 2):
        return redirect('/')
    ctx = {
        'departments': Department.objects.all()
    }

    return render(request, 'event/reports_summary.html', context=ctx)


@login_required(login_url='entry')
def report_payments(request):
    if not (request.user.is_staff or request.user.has_operator_perm) and (not request.user.hierarchy or request.user.hierarchy.level < 2):
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
