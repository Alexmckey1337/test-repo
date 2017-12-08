import coreapi
import coreschema
import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import get_object_or_404

from account.models import CustomUser
from group.models import Church, HomeGroup
from hierarchy.models import Department


class ChurchAllUserFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        church_id = view.kwargs.get('pk')
        church = get_object_or_404(Church, pk=church_id)
        queryset = queryset.filter(
            Q(cchurch=church) | Q(hhome_group__in=church.home_group.all()))

        return queryset


class HomeGroupFilter(django_filters.FilterSet):
    church = django_filters.ModelChoiceFilter(name='church', queryset=Church.objects.all())
    leader = django_filters.ModelChoiceFilter(name='leader', queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())

    class Meta:
        model = HomeGroup
        fields = ('church', 'leader', 'opening_date', 'city')


class HomeGroupsDepartmentFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        department_id = request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(church__department_id=department_id)

        return queryset


class ChurchFilter(django_filters.FilterSet):
    department = django_filters.ModelMultipleChoiceFilter(name="department",
                                                          queryset=Department.objects.all())

    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct())

    class Meta:
        model = Church
        fields = ('department', 'pastor', 'is_open', 'opening_date', 'country',
                  'city')


class CommonGroupMasterTreeFilter(BaseFilterBackend):
    level = None
    search = None

    def filter_queryset(self, request, queryset, view):
        master_id = request.query_params.get('master_tree', None)
        try:
            master = CustomUser.objects.get(pk=master_id)
        except ObjectDoesNotExist:
            return queryset

        if master.is_leaf():
            return queryset.filter(pk=master_id, hierarchy__level__gte=self.level)

        users = CustomUser.get_tree(master).filter(hierarchy__level__gte=self.level)

        return queryset.filter(**{self.search: [user.id for user in users]})


class FilterChurchMasterTree(CommonGroupMasterTreeFilter):
    level = 2
    search = 'pastor_id__in'


class FilterChurchPartnerMasterTree(CommonGroupMasterTreeFilter):
    level = 2
    search = 'church__pastor_id__in'


class FilterHomeGroupMasterTree(CommonGroupMasterTreeFilter):
    level = 1
    search = 'leader_id__in'


class FilterHGLeadersByMasterTree(BaseFilterBackend):
    query_name = 'master_tree'

    def filter_queryset(self, request, queryset, view):
        master_tree_id = request.query_params.get(self.query_name)
        if not master_tree_id and request.user.is_staff:
            return queryset
        master = self._get_master(request.user, master_tree_id)
        return queryset.intersection(master.__class__.get_tree(master))

    @staticmethod
    def _get_master(master, master_tree_id):
        if not master_tree_id and not master.is_staff:
            return master
        try:
            if master.is_staff:
                return CustomUser.objects.get(pk=master_tree_id)
            return master.__class__.get_tree(master).get(pk=master_tree_id)
        except ValueError:
            raise exceptions.ValidationError({'detail': _("master_tree_id is incorrect.")})
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(
                {'detail': _("You are don't have permissions for filter by this master.")})

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=self.query_name,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title="Master tree id",
                    description="Id of user for filter by ``master_tree``,"
                                "default: ``current_user.id`` if current_user is not staff else is ``empty``"
                )
            )
        ]


class FilterPotentialHGLeadersByMasterTree(FilterHGLeadersByMasterTree):
    pass


class FilterHGLeadersByChurch(BaseFilterBackend):
    query_name = 'church'

    def filter_queryset(self, request, queryset, view):
        church_id = request.query_params.get(self.query_name)
        if not church_id:
            return queryset
        return queryset.filter(home_group__church=church_id)

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=self.query_name,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title="Church",
                    description="Church id"
                )
            )
        ]


class FilterPotentialHGLeadersByChurch(BaseFilterBackend):
    query_name = 'church'

    def filter_queryset(self, request, queryset, view):
        return queryset
        # church_id = request.query_params.get(self.query_name)
        #  if not church_id:
        #     return queryset
        # return queryset.filter(
        #     (Q(hhome_group__isnull=True) | Q(hhome_group__church_id=church_id)) &
        #     (Q(cchurch__isnull=True) | Q(cchurch_id=church_id)))

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=self.query_name,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title="Church",
                    description="User can be leader of church.home_group if "
                                "he is member of this church or he not member of any church"
                )
            )
        ]


class FilterHGLeadersByDepartment(BaseFilterBackend):
    query_name = 'department'

    def filter_queryset(self, request, queryset, view):
        department_id = request.query_params.get(self.query_name)
        if not department_id:
            return queryset
        return queryset.filter(departments=department_id)

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name=self.query_name,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title="Department",
                    description="Department id"
                )
            )
        ]


class FilterPotentialHGLeadersByDepartment(FilterHGLeadersByDepartment):
    pass


# class GroupDetailSearchFilter():
#     def _get_potential_users(self, request, filter, *args):
#         params = request.query_params
#         search = params.get('search', '').strip()
#         if len(search) < 3:
#             return Response({'search': _('Length of search query must be > 2')},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         users = filter(*args).annotate(full_name=Concat(
#             'last_name', V(' '), 'first_name', V(' '), 'middle_name'))
#
#         search_queries = map(lambda s: s.strip(), search.split(' '))
#         for s in search_queries:
#             users = users.filter(
#                 Q(first_name__istartswith=s) | Q(last_name__istartswith=s) |
#                 Q(middle_name__istartswith=s) | Q(search_name__icontains=s))
