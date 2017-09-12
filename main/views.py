# -*- coding: utf-8
from __future__ import unicode_literals

import redis
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Count, Case, When, BooleanField, Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin, TemplateView

from account.models import CustomUser
from analytics.models import LogRecord
from event.models import Meeting, ChurchReport
from event.models import MeetingType
from group.models import Church, HomeGroup
from hierarchy.models import Department, Hierarchy
from partnership.models import Partnership, Deal
from payment.models import Currency
from status.models import Division
from summit.models import SummitType, SummitTicket, SummitAnket, Summit


def entry(request):
    return render(request, 'login/login.html')


def restore(request):
    return render(request, 'login/restore_password.html')


def edit_pass(request, activation_key=None):
    return render(request, 'login/edit_password.html')


@login_required(login_url='entry')
def events(request):
    if not request.user.hierarchy or request.user.hierarchy.level < 1:
        return redirect('/')

    ctx = {
        'reports_in_progress': Meeting.objects.filter(status=1).count(),
        'reports_submitted': Meeting.objects.filter(status=2).count(),
        'reports_expired': Meeting.objects.filter(status=3).count(),
    }

    return render(request, 'event/EVENT_LIST.html', context=ctx)


@login_required(login_url='entry')
def meeting_report_list(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    ctx = {
        'departments': Department.objects.all(),
        'churches': Church.objects.all(),
        'home_groups': HomeGroup.objects.all(),
        'owners': CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct(),
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

    ctx = {
        'departments': Department.objects.all(),
        'churches': Church.objects.all(),
        'home_groups': HomeGroup.objects.all(),
        'owners': CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct(),
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
        'managers': CustomUser.objects.filter(partnership__level__lte=2).distinct(),
        'pastors': CustomUser.objects.filter(hierarchy__level__gt=1),
    }

    return render(request, 'event/report_payments.html', context=ctx)

# partner


class CanSeePartnersMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_partners():
            raise PermissionDenied
        return super(CanSeePartnersMixin, self).dispatch(request, *args, **kwargs)


class CanSeePartnerSummaryMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_partner_summary():
            raise PermissionDenied
        return super(CanSeePartnerSummaryMixin, self).dispatch(request, *args, **kwargs)


class CanSeeDealsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_deals():
            raise PermissionDenied
        return super(CanSeeDealsMixin, self).dispatch(request, *args, **kwargs)


class CanSeeDealPaymentsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_deal_payments():
            raise PermissionDenied
        return super(CanSeeDealPaymentsMixin, self).dispatch(request, *args, **kwargs)


class CanSeePartnerStatsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_partner_stats():
            raise PermissionDenied
        return super(CanSeePartnerStatsMixin, self).dispatch(request, *args, **kwargs)


class PartnerListView(LoginRequiredMixin, CanSeePartnersMixin, TemplateView):
    template_name = 'partner/partners.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(PartnerListView, self).get_context_data(**kwargs)

        extra_context = {
            'departments': Department.objects.all(),
            'hierarchies': Hierarchy.objects.order_by('level'),
            'currencies': Currency.objects.all()
        }
        user = self.request.user
        if user.is_staff:
            extra_context['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
        elif not user.hierarchy:
            extra_context['masters'] = list()
        elif user.hierarchy.level < 2:
            extra_context['masters'] = user.__class__.get_tree(
                user).filter(is_active=True, hierarchy__level__gte=1)
        else:
            extra_context['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)

        ctx.update(extra_context)
        return ctx


class PartnerSummaryView(LoginRequiredMixin, CanSeePartnerSummaryMixin, TemplateView):
    template_name = 'partner/partnership_summary.html'
    login_url = 'entry'


class DealListView(LoginRequiredMixin, CanSeeDealsMixin, TemplateView):
    template_name = 'partner/deals.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(DealListView, self).get_context_data(**kwargs)

        ctx['managers'] = CustomUser.objects.filter(partnership__level__lte=2).distinct()
        ctx['currencies'] = Currency.objects.all()

        return ctx


class PartnerStatisticsListView(LoginRequiredMixin, CanSeePartnerStatsMixin, TemplateView):
    template_name = 'partner/stats.html'
    login_url = 'entry'


class PartnerPaymentsListView(LoginRequiredMixin, CanSeeDealPaymentsMixin, TemplateView):
    template_name = 'partner/payments.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(PartnerPaymentsListView, self).get_context_data(**kwargs)

        ctx['currencies'] = Currency.objects.all()
        ctx['supervisors'] = CustomUser.objects.filter(checks__isnull=False).distinct()
        ctx['managers'] = Partnership.objects.filter(Q(
            level__lte=Partnership.MANAGER) | Q(disciples_deals__isnull=False)).distinct()

        return ctx


# account


class DealPaymentView(LoginRequiredMixin, DetailView):
    model = Deal
    context_object_name = 'deal'
    template_name = 'payment/deal.html'

    def get_queryset(self):
        return self.model.objects.base_queryset().annotate_full_name()

    def get_context_data(self, **kwargs):
        ctx = super(DealPaymentView, self).get_context_data(**kwargs)

        ctx['payments'] = self.object.payments.base_queryset().annotate_manager_name()
        # TODO test
        ctx['currencies'] = Currency.objects.all()
        ctx['partners'] = Partnership.objects.annotate_full_name().filter(
            pk__in=Partnership.objects.exclude(pk=self.object.partnership.id)[:11].values_list('id', flat=True))

        return ctx


class PartnerPaymentView(LoginRequiredMixin, DetailView):
    model = Partnership
    context_object_name = 'partner'
    template_name = 'payment/partner.html'

    def get_queryset(self):
        return self.model.objects.base_queryset().annotate_full_name()

    def get_context_data(self, **kwargs):
        ctx = super(PartnerPaymentView, self).get_context_data(**kwargs)

        ctx['payments'] = self.object.payments.base_queryset().annotate_manager_name()
        ctx['extra_payments'] = self.object.extra_payments.base_queryset().annotate_manager_name()
        ctx['deal_payments'] = self.object.deal_payments.base_queryset().annotate_manager_name()
        # TODO test
        ctx['partners'] = Partnership.objects.annotate_full_name().filter(
            pk__in=Partnership.objects.exclude(pk=self.object.id)[:11].values_list('id', flat=True))

        return ctx


@login_required(login_url='entry')
def account(request, id):
    user = get_object_or_404(CustomUser, pk=id)
    currencies = Currency.objects.all()
    if not request.user.can_see_account_page(user):
        raise PermissionDenied
    ctx = {
        'account': user,
        'departments': Department.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'divisions': Division.objects.all(),
        'currencies': currencies,
        'partners': Partnership.objects.filter(level__lte=Partnership.MANAGER),
        'churches': Church.objects.all(),
        'log_messages': LogRecord.objects.filter(
            object_id=id,
            content_type=ContentType.objects.get_for_model(user)
        ),
        'log_messages_iam': LogRecord.objects.filter(
            user_id=id,
            content_type=ContentType.objects.get_for_model(user)
        )
    }
    return render(request, 'account/anketa.html', context=ctx)


class UserLogsListView(LoginRequiredMixin, ListView):
    model = LogRecord
    context_object_name = 'log_messages'
    template_name = 'account/logs/user.html'
    login_url = 'entry'

    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(CustomUser, pk=kwargs.get('user_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return LogRecord.objects.filter(
            object_id=self.user.id,
            content_type=ContentType.objects.get_for_model(self.user)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user'] = self.user
        return ctx


class OwnerLogsListView(UserLogsListView):
    template_name = 'account/logs/owner.html'

    def get_queryset(self):
        return LogRecord.objects.filter(
            user_id=self.user.id,
            content_type=ContentType.objects.get_for_model(self.user)
        )


class UserLogDetailView(LoginRequiredMixin, DetailView):
    model = LogRecord
    context_object_name = 'log_message'
    template_name = 'account/logs/detail.html'
    login_url = 'entry'
    pk_url_kwarg = 'log_id'


# summit


class CanSeeSummitMixin(View):
    def dispatch(self, request, *args, **kwargs):
        summit = kwargs.get('pk')
        if not (summit and request.user.can_see_summit(summit)):
            raise PermissionDenied
        return super(CanSeeSummitMixin, self).dispatch(request, *args, **kwargs)


class CanSeeSummitTicketMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_any_summit_ticket():
            raise PermissionDenied
        return super(CanSeeSummitTicketMixin, self).dispatch(request, *args, **kwargs)


class CanSeeSummitReportByBishopsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_report_by_bishop_or_high(kwargs.get('pk')):
            raise PermissionDenied
        return super(CanSeeSummitReportByBishopsMixin, self).dispatch(request, *args, **kwargs)


class CanSeeSummitProfileMixin(View):
    def dispatch(self, request, *args, **kwargs):
        return super(CanSeeSummitProfileMixin, self).dispatch(request, *args, **kwargs)


class CanSeeSummitHistoryStatsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        summit = kwargs.get('pk')
        if not (summit and request.user.can_see_summit_history_stats(summit)):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SummitDetailView(LoginRequiredMixin, CanSeeSummitMixin, DetailView):
    model = Summit
    context_object_name = 'summit'
    template_name = 'summit/detail.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(SummitDetailView, self).get_context_data(**kwargs)
        extra_context = {
            'departments': Department.objects.all(),
            'masters': CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1),
            'hierarchies': Hierarchy.objects.order_by('level'),
        }
        ctx.update(extra_context)
        return ctx


class SummitStatisticsView(SummitDetailView):
    template_name = 'summit/stats.html'


class SummitListMixin(LoginRequiredMixin, ListView):
    model = Summit
    context_object_name = 'summits'
    login_url = 'entry'
    template_name = None
    status = None

    def get_queryset(self):
        return super(SummitListMixin, self).get_queryset().order_by(
            '-start_date').for_user(self.request.user).filter(status=self.status)


class OpenSummitListView(SummitListMixin):
    template_name = 'summit/open/list.html'
    status = Summit.OPEN

    def get(self, request, *args, **kwargs):
        try:
            summit = self.get_queryset().get()
        except MultipleObjectsReturned:
            return super(OpenSummitListView, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return super(OpenSummitListView, self).get(request, *args, **kwargs)
        else:
            return redirect(summit.get_absolute_url())


class ClosedSummitListView(SummitListMixin):
    template_name = 'summit/closed/list.html'
    status = Summit.CLOSE


class SummitTicketListView(LoginRequiredMixin, CanSeeSummitTicketMixin, ListView):
    model = SummitTicket
    context_object_name = 'tickets'
    template_name = 'summit/ticket/list.html'
    login_url = 'entry'

    def dispatch(self, request, *args, **kwargs):
        response = super(SummitTicketListView, self).dispatch(request, *args, **kwargs)
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            r.srem('summit:ticket:{}'.format(request.user.id), *list(
                self.get_queryset().values_list('id', flat=True)))
        except Exception as err:
            print(err)

        return response

    def get_queryset(self):
        code = self.request.GET.get('code', '')
        qs = super(SummitTicketListView, self).get_queryset()
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            ticket_ids = r.smembers('summit:ticket:{}'.format(self.request.user.id))
        except Exception as err:
            ticket_ids = None
            print(err)
        if ticket_ids:
            qs = qs.annotate(
                is_new=Case(
                    When(id__in=ticket_ids, then=True),
                    default=False,
                    output_field=BooleanField(),
                ),
            )
        if code:
            return qs.filter(users__code=code).distinct()
        return qs


class SummitTicketDetailView(LoginRequiredMixin, CanSeeSummitTicketMixin, DetailView):
    model = SummitTicket
    context_object_name = 'ticket'
    template_name = 'summit/ticket/detail.html'
    login_url = 'entry'

    def dispatch(self, request, *args, **kwargs):
        response = super(SummitTicketDetailView, self).dispatch(request, *args, **kwargs)
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
            r.srem('summit:ticket:{}'.format(request.user.id), self.object.id)
        except Exception as err:
            print(err)

        return response


class SummitProfileDetailView(LoginRequiredMixin, CanSeeSummitProfileMixin, DetailView):
    model = SummitAnket
    context_object_name = 'profile'
    template_name = 'summit/profile.html'
    login_url = 'entry'


class SummitBishopReportView(LoginRequiredMixin, CanSeeSummitReportByBishopsMixin, TemplateView):
    template_name = 'summit/bishop_report.html'
    login_url = 'entry'
    summit_id = None

    def get(self, request, *args, **kwargs):
        self.summit_id = kwargs.get('pk')
        return super(SummitBishopReportView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(SummitBishopReportView, self).get_context_data(**kwargs)

        ctx['summit'] = get_object_or_404(Summit, pk=self.summit_id)
        ctx['departments'] = Department.objects.all()
        ctx['hierarchies'] = Hierarchy.objects.order_by('level')

        return ctx


class SummitHistoryStatisticsView(LoginRequiredMixin, CanSeeSummitHistoryStatsMixin, TemplateView):
    template_name = 'summit/history/stats.html'
    login_url = 'entry'
    summit_id = None

    def get(self, request, *args, **kwargs):
        self.summit_id = kwargs.get('pk')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['summit'] = get_object_or_404(Summit, pk=self.summit_id)
        ctx['departments'] = Department.objects.all()

        return ctx


# database


class CanSeeUserListMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_user_list():
            raise PermissionDenied
        return super(CanSeeUserListMixin, self).dispatch(request, *args, **kwargs)


class CanSeeChurchesMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_churches():
            raise PermissionDenied
        return super(CanSeeChurchesMixin, self).dispatch(request, *args, **kwargs)


class CanSeeChurchMixin(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            church = self.get_object()
        except Http404:
            raise PermissionDenied
        if not request.user.can_see_church(church):
            raise PermissionDenied
        return super(CanSeeChurchMixin, self).dispatch(request, *args, **kwargs)


class CanSeeHomeGroupsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_home_groups():
            raise PermissionDenied
        return super(CanSeeHomeGroupsMixin, self).dispatch(request, *args, **kwargs)


class TabsMixin(ContextMixin):
    active_tab = None

    def get_context_data(self, **kwargs):
        return super(TabsMixin, self).get_context_data(**{'active_tab': self.active_tab})


class PeopleListView(LoginRequiredMixin, TabsMixin, CanSeeUserListMixin, TemplateView):
    template_name = 'database/people.html'
    login_url = 'entry'
    active_tab = 'people'

    def get_context_data(self, **kwargs):
        ctx = super(PeopleListView, self).get_context_data(**kwargs)
        extra_ctx = {
            'departments': Department.objects.all(),
            'hierarchies': Hierarchy.objects.order_by('level'),
            'currencies': Currency.objects.all()
        }
        user = self.request.user
        if user.is_staff:
            extra_ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
        elif not user.hierarchy:
            extra_ctx['masters'] = list()
        elif user.hierarchy.level < 2:
            extra_ctx['masters'] = user.__class__.get_tree(
                user).filter(is_active=True, hierarchy__level__gte=1)
        else:
            extra_ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
        ctx.update(extra_ctx)

        return ctx


class ChurchListView(LoginRequiredMixin, TabsMixin, CanSeeChurchesMixin, TemplateView):
    template_name = 'database/churches.html'
    login_url = 'entry'
    active_tab = 'churches'

    def get_context_data(self, **kwargs):
        ctx = super(ChurchListView, self).get_context_data(**kwargs)

        ctx['departments'] = Department.objects.all()
        ctx['currencies'] = Currency.objects.all()

        return ctx


class HomeGroupListView(LoginRequiredMixin, TabsMixin, CanSeeHomeGroupsMixin, TemplateView):
    template_name = 'database/home_groups.html'
    login_url = 'entry'
    active_tab = 'home_groups'

    def get_context_data(self, **kwargs):
        ctx = super(HomeGroupListView, self).get_context_data(**kwargs)
        ctx['departments'] = Department.objects.all()
        ctx['churches'] = Church.objects.all()

        return ctx


class ChurchDetailView(LoginRequiredMixin, CanSeeChurchMixin, DetailView):
    model = Church
    context_object_name = 'church'
    template_name = 'group/church_detail.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(ChurchDetailView, self).get_context_data(**kwargs)

        church = self.object
        extra_context = {
            'currencies': Currency.objects.all(),
            'pastors': CustomUser.objects.filter(hierarchy__level__gt=1),
            'church_users': church.uusers.count(),
            'church_all_users': church.uusers.count() + HomeGroup.objects.filter(
                church_id=church.id).aggregate(home_users=Count('uusers'))['home_users'],
            'parishioners_count': church.uusers.filter(hierarchy__level=0).count() + CustomUser.objects.filter(
                hhome_group__church_id=church.id, hierarchy__level=0).count(),
            'leaders_count': CustomUser.objects.filter(
                home_group__church_id=church.id, home_group__leader__isnull=False).distinct().count(),
            'home_groups_count': church.home_group.count(),
            'fathers_count': church.uusers.filter(
                spiritual_level=CustomUser.FATHER).count() + HomeGroup.objects.filter(
                church__id=church.id, uusers__spiritual_level=3).count(),
            'juniors_count': church.uusers.filter(
                spiritual_level=CustomUser.JUNIOR).count() + HomeGroup.objects.filter(
                church__id=church.id, uusers__spiritual_level=2).count(),
            'babies_count': church.uusers.filter(
                spiritual_level=CustomUser.BABY).count() + HomeGroup.objects.filter(
                church__id=church.id, uusers__spiritual_level=1).count(),
            'partners_count': church.uusers.filter(partnership__is_active=True).count() + CustomUser.objects.filter(
                hhome_group__church_id=church.id, partnership__is_active=True).count(),

        }
        ctx.update(extra_context)

        return ctx


class HomeGroupDetailView(LoginRequiredMixin, CanSeeHomeGroupsMixin, DetailView):
    model = HomeGroup
    context_object_name = 'home_group'
    template_name = 'group/home_group_detail.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(HomeGroupDetailView, self).get_context_data(**kwargs)

        home_group = self.object
        extra_context = {
            'users_count': home_group.uusers.count(),
            'fathers_count': home_group.uusers.filter(spiritual_level=CustomUser.FATHER).count(),
            'juniors_count': home_group.uusers.filter(spiritual_level=CustomUser.JUNIOR).count(),
            'babies_count': home_group.uusers.filter(spiritual_level=CustomUser.BABY).count(),
            'partners_count': home_group.uusers.filter(partnership__is_active=True).count(),
        }
        ctx.update(extra_context)

        return ctx


@login_required(login_url='entry')
def index(request):
    user = request.user
    ctx = {
        'departments': Department.objects.all(),
        'summits': SummitType.objects.all(),
        'hierarchies': Hierarchy.objects.order_by('level'),
        'current_user': user
    }

    if user.is_staff:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    elif not user.hierarchy:
        ctx['masters'] = list()
    elif user.hierarchy.level < 2:
        ctx['masters'] = user.__class__.get_tree(user).filter(is_active=True, hierarchy__level__gte=1)
    else:
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
    return render(request, 'home/main.html', context=ctx)


@login_required(login_url='entry')
def event_info(request):
    return render(request, 'event/event_info.html')


@login_required(login_url='entry')
def synchronize(request):
    # weekday = timezone.now().weekday() + 1
    # create_participations()
    # create_reports(weekday)
    return HttpResponse('ok')
