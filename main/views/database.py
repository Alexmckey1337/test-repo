from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.views.generic.base import ContextMixin

from account.models import CustomUser
from group.models import Church, HomeGroup
from hierarchy.models import Department, Hierarchy
from partnership.models import PartnerGroup
from payment.models import Currency


__all__ = [
    'PeopleListView', 'ChurchListView', 'ChurchDetailView',
    'HomeGroupListView', 'HomeGroupDetailView',
]


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
            'currencies': Currency.objects.all(),
            'churches': Church.objects.all(),
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
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)

        return ctx


class HomeGroupListView(LoginRequiredMixin, TabsMixin, CanSeeHomeGroupsMixin, TemplateView):
    template_name = 'database/home_groups.html'
    login_url = 'entry'
    active_tab = 'home_groups'

    def get_context_data(self, **kwargs):
        ctx = super(HomeGroupListView, self).get_context_data(**kwargs)
        ctx['departments'] = Department.objects.all()
        ctx['churches'] = Church.objects.all()
        ctx['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)

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
            'partners_count': church.uusers.filter(partners__isnull=False).count() + CustomUser.objects.filter(
                hhome_group__church_id=church.id, partners__isnull=False).count(),
            'no_partners_count': church.uusers.filter(partners__isnull=True).count() + CustomUser.objects.filter(
                hhome_group__church_id=church.id, partners__isnull=True).count(),
            'partner_groups': PartnerGroup.objects.all(),
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
            'partners_count': home_group.uusers.filter(partners__is_active=True).count(),
        }
        ctx.update(extra_context)

        return ctx
