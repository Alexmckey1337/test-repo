# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView

from account.models import CustomUser
from account.permissions import CanAccountObjectRead, CanAccountObjectEdit
from event.models import MeetingType
from group.models import Church, HomeGroup
from hierarchy.models import Department, Hierarchy
from location.models import Country, Region, City
from partnership.models import Partnership, Deal
from payment.models import Currency
from status.models import Division
from summit.models import SummitType


def entry(request):
    return render(request, 'login/login.html')


def edit_pass(request):
    return render(request, 'login/edit_password.html')


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
        'leaders': CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct(),
        'meeting_type': get_object_or_404(MeetingType, code=code),
    }
    return render(request, 'event/meeting_report_create.html', context=ctx)


# partner


class CanSeePartnersView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_churches():
            raise PermissionDenied
        return super(CanSeePartnersView, self).dispatch(request, *args, **kwargs)


class CanSeeDealsView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_churches():
            raise PermissionDenied
        return super(CanSeeDealsView, self).dispatch(request, *args, **kwargs)


class CanSeePartnerStatsView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_churches():
            raise PermissionDenied
        return super(CanSeePartnerStatsView, self).dispatch(request, *args, **kwargs)


class PartnerListView(LoginRequiredMixin, CanSeePartnersView, ListView):
    model = Partnership
    context_object_name = 'partners'
    template_name = 'partner/partners.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(PartnerListView, self).get_context_data(**kwargs)

        extra_context = {
            'departments': Department.objects.all(),
            'hierarchies': Hierarchy.objects.order_by('level'),
        }

        ctx.update(extra_context)
        return ctx


class DealListView(LoginRequiredMixin, CanSeeDealsView, ListView):
    model = Deal
    context_object_name = 'deals'
    template_name = 'partner/deals.html'
    login_url = 'entry'


class PartnerStatisticsListView(LoginRequiredMixin, CanSeePartnerStatsView, ListView):
    model = Partnership
    context_object_name = 'partners'
    template_name = 'partner/stats.html'
    login_url = 'entry'


# account


@login_required(login_url='entry')
def account(request, id):
    user = get_object_or_404(CustomUser, pk=id)
    has_perm = CanAccountObjectRead().has_object_permission(request, None, user)
    currencies = Currency.objects.all()
    if not has_perm:
        raise PermissionDenied
    ctx = {
        'account': user,
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'divisions': Division.objects.all(),
        'currencies': currencies,
        'partners': Partnership.objects.filter(level__lte=Partnership.MANAGER),
        'churches': Church.objects.all()
    }
    return render(request, 'account/anketa.html', context=ctx)


@login_required(login_url='entry')
def account_edit(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    has_perm = CanAccountObjectEdit().has_object_permission(request, None, user)
    currencies = Currency.objects.all()
    if not has_perm:
        if user_id:
            return redirect(user.get_absolute_url)
        raise PermissionDenied
    ctx = {
        'account': user,
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'divisions': Division.objects.all(),
        'countries': Country.objects.all(),
        'regions': Region.objects.filter(country__title=user.country),
        'cities': City.objects.filter(region__title=user.region),
        'partners': Partnership.objects.filter(level__lte=Partnership.MANAGER),
        'currencies': currencies
    }
    return render(request, 'account/edit.html', context=ctx)


# account


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
        'summit_type': SummitType.objects.get(id=summit_id),
    }
    return render(request, 'summit/summit_info.html', context=ctx)


# database


class CanSeeChurchesView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_churches():
            raise PermissionDenied
        return super(CanSeeChurchesView, self).dispatch(request, *args, **kwargs)


class CanSeeHomeGroupsView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_home_groups():
            raise PermissionDenied
        return super(CanSeeHomeGroupsView, self).dispatch(request, *args, **kwargs)


class ChurchListView(LoginRequiredMixin, CanSeeChurchesView, ListView):
    model = Church
    context_object_name = 'churches'
    template_name = 'database/churches.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(ChurchListView, self).get_context_data(**kwargs)

        ctx['departments'] = Department.objects.all()
        ctx['church_all_pastors'] = CustomUser.objects.filter(church__pastor__id__isnull=False).distinct()
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)

        return ctx


class HomeGroupListView(LoginRequiredMixin, CanSeeHomeGroupsView, ListView):
    model = HomeGroup
    context_object_name = 'home_groups'
    template_name = 'database/home_groups.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(HomeGroupListView, self).get_context_data(**kwargs)

        ctx['churches'] = Church.objects.all()
        ctx['leaders'] = CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct()
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)

        return ctx


class ChurchDetailView(LoginRequiredMixin, CanSeeChurchesView, DetailView):
    model = Church
    context_object_name = 'church'
    template_name = 'group/church_detail.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(ChurchDetailView, self).get_context_data(**kwargs)

        extra_context = {
            'currencies': Currency.objects.all(),
            'pastors': CustomUser.objects.filter(hierarchy__level__gt=1),
            'church_users': self.object.users.count(),
            'church_all_users': self.object.users.count() + HomeGroup.objects.filter(
                church_id=self.object.id).aggregate(home_users=Count('users'))['home_users'],
            'parishioners_count': self.object.users.filter(hierarchy__level=0).count(),
            'leaders_count': self.object.users.filter(hierarchy__level=1).count(),
            'home_groups_count': self.object.home_group.count(),
            'fathers_count': self.object.users.filter(
                spiritual_level=CustomUser.FATHER).count() + HomeGroup.objects.filter(
                church__id=self.object.id).filter(users__spiritual_level=3).count(),
            'juniors_count': self.object.users.filter(
                spiritual_level=CustomUser.JUNIOR).count() + HomeGroup.objects.filter(
                church__id=self.object.id).filter(users__spiritual_level=2).count(),
            'babies_count': self.object.users.filter(
                spiritual_level=CustomUser.BABY).count() + HomeGroup.objects.filter(
                church__id=self.object.id).filter(users__spiritual_level=1).count(),
            'partners_count': self.object.users.filter(partnership__is_active=True).count(),
        }
        ctx.update(extra_context)

        return ctx


class HomeGroupDetailView(LoginRequiredMixin, CanSeeHomeGroupsView, DetailView):
    model = HomeGroup
    context_object_name = 'home_group'
    template_name = 'group/home_group_detail.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(HomeGroupDetailView, self).get_context_data(**kwargs)

        extra_context = {
            'users_count': self.object.users.count(),
            'fathers_count': self.object.users.filter(spiritual_level=CustomUser.FATHER).count(),
            'juniors_count': self.object.users.filter(spiritual_level=CustomUser.JUNIOR).count(),
            'babies_count': self.object.users.filter(spiritual_level=CustomUser.BABY).count(),
            'partners_count': self.object.users.filter(partnership__is_active=True).count(),
        }
        ctx.update(extra_context)

        return ctx


@login_required(login_url='entry')
def people(request):
    user = request.user
    currencies = Currency.objects.all()
    ctx = {
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'currencies': currencies
    }
    if user.is_staff:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    elif not user.hierarchy:
        ctx['masters'] = list()
    elif user.hierarchy.level < 2:
        ctx['masters'] = user.get_descendants(include_self=True).filter(is_active=True, hierarchy__level__gte=1)
    else:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    return render(request, 'database/people.html', context=ctx)


@login_required(login_url='entry')
def index(request):
    user = request.user
    ctx = {
        'departments': Department.objects.all(),
        'summits': SummitType.objects.all(),
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
    return render(request, 'home/main.html', context=ctx)


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
    return HttpResponse('ok')
