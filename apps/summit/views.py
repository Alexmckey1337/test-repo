from collections import defaultdict

from celery.result import AsyncResult
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import PermissionDenied, MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Case, When, BooleanField, Value
from django.db.models.functions import Concat
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from apps.account.models import CustomUser
from apps.hierarchy.models import Department, Hierarchy
from apps.notification.backend import RedisBackend
from apps.summit.models import Summit, SummitTicket, SummitAnket, AnketEmail


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
            r = RedisBackend()
            r.srem('summit:ticket:{}'.format(request.user.id), *list(
                self.get_queryset().values_list('id', flat=True)))
        except Exception as err:
            print(err)

        return response

    def get_queryset(self):
        code = self.request.GET.get('code', '')
        qs = super(SummitTicketListView, self).get_queryset()
        try:
            r = RedisBackend()
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
            r = RedisBackend()
            r.srem('summit:ticket:{}'.format(request.user.id), self.object.id)
        except Exception as err:
            print(err)

        return response


class SummitProfileDetailView(LoginRequiredMixin, CanSeeSummitProfileMixin, DetailView):
    model = SummitAnket
    context_object_name = 'profile'
    template_name = 'summit/profile.html'
    login_url = 'entry'


class SummitProfileEmailDetailView(LoginRequiredMixin, CanSeeSummitProfileMixin, DetailView):
    model = AnketEmail
    context_object_name = 'email'
    template_name = 'summit/emails/detail.html'
    login_url = 'entry'


class SummitProfileEmailTextView(LoginRequiredMixin, CanSeeSummitProfileMixin, DetailView):
    model = AnketEmail
    context_object_name = 'email'
    template_name = 'summit/emails/text.html'
    login_url = 'entry'


class SummitProfileEmailListView(LoginRequiredMixin, CanSeeSummitProfileMixin, ListView):
    model = AnketEmail
    context_object_name = 'emails'
    template_name = 'summit/emails/list.html'
    login_url = 'entry'

    profile = None

    def dispatch(self, request, *args, **kwargs):
        self.profile = get_object_or_404(SummitAnket, pk=kwargs.get('profile_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(anket=self.profile)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['profile'] = self.profile

        return ctx


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


class SummitEmailTasksView(LoginRequiredMixin, TemplateView):
    template_name = 'summit/summit_email_tasks.html'
    login_url = 'entry'

    summit_id = None

    def get(self, request, *args, **kwargs):
        self.summit_id = kwargs.get('summit_id')
        return super().get(request, *args, **kwargs)

    def get_statuses(self):
        r = RedisBackend()
        statuses = defaultdict(list)
        for profile_id in r.scan_iter('summit:email:sending:{}:*'.format(self.summit_id)):
            tasks = r.smembers(profile_id)
            for task_id in tasks:
                result = AsyncResult(task_id)
                statuses[int(profile_id.decode('utf8').rsplit(':', 1)[-1])].append(
                    (result.status, task_id.decode('utf8')))
        return statuses

    def get_profiles(self):
        summit = get_object_or_404(Summit, pk=self.summit_id)
        profiles = summit.ankets.all()
        # emails = AnketEmail.objects.filter(is_success=False, anket_id=OuterRef('pk'))
        # profiles = profiles.annotate(email_exist=Exists(emails)).filter(email_exist=True)
        profiles = profiles.annotate(
            email_statuses=ArrayAgg('emails__is_success'),
            full_name=Concat(
                'user__last_name', Value(' '), 'user__first_name', Value(' '), 'user__middle_name'))
        profiles = list(profiles.values('id', 'code', 'email_statuses', 'user_id', 'full_name', 'user__email'))
        statuses = self.get_statuses()
        for profile in profiles:
            profile['statuses'] = statuses[profile['id']]
        return profiles

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        profiles = self.get_profiles()

        ctx['statuses'] = sorted(profiles, key=lambda p: len(p['statuses']), reverse=True)

        return ctx


class SummitScheduleTasksView(LoginRequiredMixin, TemplateView):
    template_name = 'summit/summit_schedule_tasks.html'
    login_url = 'entry'

    summit_id = None

    def get(self, request, *args, **kwargs):
        self.summit_id = kwargs.get('summit_id')
        return super().get(request, *args, **kwargs)

    def get_statuses(self):
        r = RedisBackend()
        statuses = defaultdict(list)
        for profile_id in r.scan_iter('summit:schedule:sending:{}:*'.format(self.summit_id)):
            tasks = r.smembers(profile_id)
            for task_id in tasks:
                result = AsyncResult(task_id)
                statuses[int(profile_id.decode('utf8').rsplit(':', 1)[-1])].append(
                    (result.status, task_id.decode('utf8')))
        return statuses

    def get_profiles(self):
        summit = get_object_or_404(Summit, pk=self.summit_id)
        profiles = summit.ankets.all()
        # emails = AnketEmail.objects.filter(is_success=False, anket_id=OuterRef('pk'))
        # profiles = profiles.annotate(email_exist=Exists(emails)).filter(email_exist=True)
        profiles = profiles.annotate(
            full_name=Concat(
                'user__last_name', Value(' '), 'user__first_name', Value(' '), 'user__middle_name'))
        profiles = list(profiles.values('id', 'code', 'user_id', 'full_name', 'user__email'))
        statuses = self.get_statuses()
        for profile in profiles:
            profile['statuses'] = statuses[profile['id']]
        return profiles

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        profiles = self.get_profiles()

        ctx['statuses'] = sorted(profiles, key=lambda p: len(p['statuses']), reverse=True)

        return ctx
