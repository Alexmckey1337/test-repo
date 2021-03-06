import pytest
from django.core.exceptions import FieldError
from django.urls import reverse
from rest_framework import status

from apps.group.api.serializers import (
    ChurchTableSerializer, ChurchSerializer, HomeGroupSerializer, HomeGroupReadSerializer)
from apps.group.api.views import ChurchViewSet, HomeGroupViewSet


def create_church_users(church, count, user_factory):
    user_list = user_factory.create_batch(count, cchurch=church)
    return user_list


def create_home_group_users(home_group, count, user_factory):
    user_list = user_factory.create_batch(count, hhome_group=home_group)
    return user_list


def create_home_group_of_church_users(church, user_factory, count):
    users = list()
    for home_group in church.home_group.all():
        user_list = user_factory.create_batch(count, hhome_group=home_group)
        users += user_list
    return users


def create_home_group_of_church(church, home_group_factory, count):
    return home_group_factory.create_batch(count, church=church)


def create_users_for_potential_users_search(church, user_factory, name_type, user=None, count=1):
    user_list = user_factory.create_batch(count, **{name_type: 'batman', 'cchurch': church, 'master': user})
    return user_list


@pytest.mark.django_db
class TestChurchViewSet:
    def test_all_users_one_page(self, api_login_client, church, church_factory, user_factory, home_group_factory):
        create_church_users(church, 4, user_factory)  # users_count +4, = 4
        create_home_group_of_church(church, home_group_factory, 2)  # home_group_count +2, = 2
        create_home_group_of_church_users(church, user_factory, 3)  # users_count +2*3, = 10

        other_church = church_factory()

        create_church_users(other_church, 3, user_factory)  # users_count +0, = 10 | other_users +3, =3
        create_home_group_of_church(other_church, home_group_factory, 4)
        create_home_group_of_church_users(
            other_church, user_factory, 1)  # users_count +0, = 10 | other_users +1*4, =7

        url = reverse('church-all-users', kwargs={'pk': church.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10
        assert response.data['count'] == 10

    def test_all_users_multi_page(self, api_login_client, church, church_factory, user_factory, home_group_factory):
        create_church_users(church, 40, user_factory)  # users_count +40, = 40
        create_home_group_of_church(church, home_group_factory, 2)  # home_group_count +2, = 2
        create_home_group_of_church_users(church, user_factory, 30)  # users_count +2*30, = 100

        other_church = church_factory()

        create_church_users(other_church, 30, user_factory)  # users_count +0, = 100 | other_users +30, =30
        create_home_group_of_church(other_church, home_group_factory, 4)
        create_home_group_of_church_users(
            other_church, user_factory, 10)  # users_count +0, = 100 | other_users +1*40, =70

        url = reverse('church-all-users', kwargs={'pk': church.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30
        assert response.data['count'] == 100

    def test_home_groups_one_page(self, monkeypatch, api_login_client, church, church_factory, home_group_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        create_home_group_of_church(church, home_group_factory, 4)  # home_group_count +4, = 4

        other_church = church_factory()
        create_home_group_of_church(other_church, home_group_factory, 2)  # home_group_count +0, = 4

        url = reverse('church-home-groups', kwargs={'pk': church.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4
        assert response.data['count'] == 4

    def test_home_groups_multi_page(self, monkeypatch, api_login_client, church, church_factory, home_group_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        create_home_group_of_church(church, home_group_factory, 40)  # home_group_count +40, = 40

        other_church = church_factory()
        create_home_group_of_church(other_church, home_group_factory, 20)  # home_group_count +0, = 40

        url = reverse('church-home-groups', kwargs={'pk': church.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30
        assert response.data['count'] == 40

    def test_users_one_page(self, monkeypatch, api_login_client, church, church_factory, user_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        create_church_users(church, 4, user_factory)  # users_count +4, = 4

        other_church = church_factory()
        create_church_users(other_church, 3, user_factory)  # users_count +0, = 4 | other_users +3, =3

        url = reverse('church-users', kwargs={'pk': church.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4
        assert response.data['count'] == 4

    def test_users_multi_page(self, monkeypatch, api_login_client, church, church_factory, user_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        create_church_users(church, 40, user_factory)  # users_count +40, = 40

        other_church = church_factory()
        create_church_users(other_church, 30, user_factory)  # users_count +0, = 40 | other_users +30, =30

        url = reverse('church-users', kwargs={'pk': church.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30
        assert response.data['count'] == 40

    @pytest.mark.parametrize('search_query', (None, '', 'u', 'us'), ids=('without', 'len_0', 'len_1', 'len_2'))
    @pytest.mark.parametrize('is_detail,url_name', (
            (False, 'church-potential-users-church'),
            (True, 'church-potential-users-group')
    ), ids=('church', 'group'))
    def test_potential_users_church_with_incorrect_search_request(
            self, api_login_client, church, search_query, is_detail, url_name):

        if is_detail:
            url = reverse(url_name, kwargs={'pk': church.id})
        else:
            url = reverse(url_name)

        data = {'search': search_query} if search_query is not None else dict()
        response = api_login_client.get(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'search' in response.data.keys()

    @pytest.mark.parametrize('name_type', ('last_name', 'first_name', 'middle_name', 'search_name'))
    @pytest.mark.parametrize('is_detail,url_name', (
            (False, 'church-potential-users-church'),
            (True, 'church-potential-users-group')
    ), ids=('church', 'group'))
    def test_potential_users_search_by_name(
            self, api_client, church, church_factory, user_factory, name_type, is_detail, url_name):

        user = user_factory(is_staff=True)
        user_factory.create_batch(4, **{name_type: 'batman', 'master': user})  # users count +4, = 4

        create_users_for_potential_users_search(
            church, user_factory, name_type, user, count=3)  # users count +0|3, = 4|7 (church|group)

        other_church = church_factory()
        create_users_for_potential_users_search(
            other_church, user_factory, name_type, user, count=6)  # users count +0|3, = 4|7 (church|group)

        if is_detail:
            url = reverse(url_name, kwargs={'pk': church.id})
        else:
            url = reverse(url_name)

        api_client.force_login(user)
        response = api_client.get(url, data={'search': 'batm'}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert response.data['count'] == 13

    @pytest.mark.parametrize('first_name', ('batman', 'loki', 'mario'))
    @pytest.mark.parametrize('last_name', ('batman', 'loki', 'mario'))
    @pytest.mark.parametrize('middle_name', ('batman', 'loki', 'mario'))
    @pytest.mark.parametrize('is_detail,url_name', (
            (False, 'church-potential-users-church'),
            (True, 'church-potential-users-group')
    ), ids=('church', 'group'))
    def test_potential_users_search_by_full_name(
            self, api_login_client, church, user_factory,
            first_name, last_name, middle_name,
            is_detail, url_name):

        user_factory.create_batch(4, first_name=first_name, last_name=last_name,
                                  middle_name=middle_name)  # users count +4, = 4

        if is_detail:
            url = reverse(url_name, kwargs={'pk': church.id})
        else:
            url = reverse(url_name)

        data = {'search': '{} {} {}'.format(last_name, middle_name, first_name)}
        response = api_login_client.get(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4

    @pytest.mark.parametrize('is_detail,url_name', (
            (False, 'church-potential-users-church'),
            (True, 'church-potential-users-group')
    ), ids=('church', 'group'))
    def test_potential_users_search_by_name_and_department(
            self, api_login_client, church, user_factory, department, department_factory,
            is_detail, url_name):

        users = user_factory.create_batch(4, first_name='batman', last_name='loki')  # users count +4, = 4
        for u in users:
            u.departments.set([department])
        users = user_factory.create_batch(6, first_name='batman', last_name='loki')  # users count +0, = 4
        for u in users:
            u.departments.set([department_factory()])

        if is_detail:
            url = reverse(url_name, kwargs={'pk': church.id})
        else:
            url = reverse(url_name)

        data = {'search': 'batm lok', 'department': department.id}
        response = api_login_client.get(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4

    @pytest.mark.parametrize('is_detail,url_name', (
            (False, 'church-potential-users-church'),
            (True, 'church-potential-users-group')
    ), ids=('church', 'group'))
    def test_potential_users_search_max_30_results(
            self, api_login_client, church, user_factory,
            is_detail, url_name):

        user_factory.create_batch(
            40, first_name='batman', last_name='loki')  # users count +40, = 40, but show only 30

        if is_detail:
            url = reverse(url_name, kwargs={'pk': church.id})
        else:
            url = reverse(url_name)

        response = api_login_client.get(url, data={'search': 'batm lok'}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert response.data['count'] == 40

    def test_add_user_without_user_id(self, monkeypatch, api_login_client, church):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-add-user', kwargs={'pk': church.id})

        response = api_login_client.post(url, data={}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_user_with_non_exist_user_id(self, monkeypatch, api_login_client, church, user_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-add-user', kwargs={'pk': church.id})
        user = user_factory()
        non_exist_user_id = user.id
        user.delete()

        response = api_login_client.post(url, data={'user_id': non_exist_user_id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not church.uusers.filter(id=user.id).exists()

    def test_add_user_with_other_church(self, monkeypatch, api_login_client, church, church_factory, user):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-add-user', kwargs={'pk': church.id})
        other_church = church_factory()
        user.cchurch = other_church
        user.save()

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not church.uusers.filter(id=user.id).exists()

    def test_add_user_with_home_group(self, monkeypatch, api_login_client, church, user, home_group_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-add-user', kwargs={'pk': church.id})
        group = home_group_factory(church=church)
        user.hhome_group = group
        user.save()

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not church.uusers.filter(id=user.id).exists()

    def test_add_user_success(self, monkeypatch, api_login_client, church, user):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-add-user', kwargs={'pk': church.id})

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert church.uusers.filter(id=user.id).exists()

    def test_del_user_without_user_id(self, monkeypatch, api_login_client, church):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-del-user', kwargs={'pk': church.id})

        response = api_login_client.post(url, data={}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_del_user_with_non_exist_user_id(self, monkeypatch, api_login_client, church, user_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-del-user', kwargs={'pk': church.id})
        user = user_factory()
        non_exist_user_id = user.id
        user.delete()

        response = api_login_client.post(url, data={'user_id': non_exist_user_id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_del_user_with_other_church(self, monkeypatch, api_login_client, church, user):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-del-user', kwargs={'pk': church.id})

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_del_user_success(self, monkeypatch, api_login_client, church, user_factory):
        monkeypatch.setattr(ChurchViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('church-del-user', kwargs={'pk': church.id})
        user = user_factory()
        user.cchurch = church
        user.save()

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not church.uusers.filter(id=user.id).exists()

    @pytest.mark.xfail
    @pytest.mark.parametrize('method,action,serializer_class', (
            ('get', 'list', ChurchTableSerializer),
            ('post', 'create', ChurchSerializer),
            ('get', 'retrieve', ChurchSerializer),
            ('put', 'update', ChurchSerializer),
            ('patch', 'partial_update', ChurchSerializer),
    ), ids=('get-list', 'post-create', 'get-retrieve', 'put-update', 'patch-partial_update'))
    def test_get_serializer_class(self, rf, fake_church_view_set, method, action, serializer_class, user_factory):
        method_action = getattr(rf, method)
        request = method_action('/')
        request.user = user_factory(is_staff=True)
        view = fake_church_view_set.as_view({method: action})

        instance = view(request)

        assert instance.get_serializer_class() == serializer_class

    @pytest.mark.xfail
    @pytest.mark.parametrize('annotate_field_name', ('count_groups', 'count_users'))
    @pytest.mark.parametrize('method,action,has_field', (
            ('get', 'list', True),
            ('post', 'create', False),
            ('get', 'retrieve', False),
            ('put', 'update', False),
            ('patch', 'partial_update', False),
    ), ids=('get-list', 'post-create', 'get-retrieve', 'put-update', 'patch-partial_update'))
    def test_get_queryset(self, rf, fake_church_view_set, method, action, has_field, annotate_field_name, user_factory):
        method_action = getattr(rf, method)
        request = method_action('/', pk=1)
        request.user = user_factory(is_staff=True)
        view = fake_church_view_set.as_view({method: action})

        instance = view(request)

        if has_field:
            instance.get_queryset().values(annotate_field_name)
        else:
            with pytest.raises(FieldError):
                instance.get_queryset().values(annotate_field_name)


@pytest.mark.django_db
class TestHomeGroupViewSet:
    def test_users_one_page(self, monkeypatch, api_login_client, home_group, home_group_factory, user_factory):
        monkeypatch.setattr(HomeGroupViewSet, 'get_queryset', lambda s: s.queryset)
        create_home_group_users(home_group, 4, user_factory)  # users_count +4, = 4

        other_home_group = home_group_factory()
        create_home_group_users(other_home_group, 3, user_factory)  # users_count +0, = 4 | other_users +3, =3

        url = reverse('homegroup-users', kwargs={'pk': home_group.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4
        assert response.data['count'] == 4

    def test_users_multi_page(self, monkeypatch, api_login_client, home_group, home_group_factory, user_factory):
        monkeypatch.setattr(HomeGroupViewSet, 'get_queryset', lambda s: s.queryset)
        create_home_group_users(home_group, 40, user_factory)  # users_count +40, = 40

        other_home_group = home_group_factory()
        create_home_group_users(other_home_group, 30, user_factory)  # users_count +0, = 40 | other_users +30, =30

        url = reverse('homegroup-users', kwargs={'pk': home_group.id})

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30
        assert response.data['count'] == 40

    def test_add_user_without_user_id(self, api_login_client, home_group):
        url = reverse('homegroup-add-user', kwargs={'pk': home_group.id})

        response = api_login_client.post(url, data={}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_user_with_non_exist_user_id(self, api_login_client, home_group, user_factory):
        url = reverse('homegroup-add-user', kwargs={'pk': home_group.id})
        user = user_factory()
        non_exist_user_id = user.id
        user.delete()

        response = api_login_client.post(url, data={'user_id': non_exist_user_id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not home_group.uusers.filter(id=user.id).exists()

    def test_add_user_with_other_home_group(self, api_login_client, home_group, home_group_factory, user):
        url = reverse('homegroup-add-user', kwargs={'pk': home_group.id})
        other_home_group = home_group_factory()
        user.hhome_group = other_home_group
        user.save()

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not home_group.uusers.filter(id=user.id).exists()

    def test_add_user_with_church(self, api_login_client, home_group, user, church_factory):
        url = reverse('homegroup-add-user', kwargs={'pk': home_group.id})
        church = church_factory()
        user.cchurch = church
        user.save()

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not home_group.uusers.filter(id=user.id).exists()

    def test_add_user_to_home_group_and_delete_from_church(self, api_login_client, home_group, user):
        url = reverse('homegroup-add-user', kwargs={'pk': home_group.id})
        church = home_group.church
        user.cchurch = church
        user.save()

        api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert not church.uusers.filter(id=user.id).exists()

    def test_add_user_success(self, api_login_client, home_group, user):
        url = reverse('homegroup-add-user', kwargs={'pk': home_group.id})

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert home_group.uusers.filter(id=user.id).exists()

    def test_del_user_without_user_id(self, monkeypatch, api_login_client, home_group):
        monkeypatch.setattr(HomeGroupViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('homegroup-del-user', kwargs={'pk': home_group.id})

        response = api_login_client.post(url, data={}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_del_user_with_non_exist_user_id(self, monkeypatch, api_login_client, home_group, user_factory):
        monkeypatch.setattr(HomeGroupViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('homegroup-del-user', kwargs={'pk': home_group.id})
        user = user_factory()
        non_exist_user_id = user.id
        user.delete()

        response = api_login_client.post(url, data={'user_id': non_exist_user_id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_del_user_with_other_home_group(self, monkeypatch, api_login_client, home_group, user):
        monkeypatch.setattr(HomeGroupViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('homegroup-del-user', kwargs={'pk': home_group.id})

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_del_user_from_home_group_and_add_to_church_success(
            self, monkeypatch, api_login_client, home_group, user_factory):
        monkeypatch.setattr(HomeGroupViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('homegroup-del-user', kwargs={'pk': home_group.id})
        user = user_factory()
        user.hhome_group = home_group
        user.save()

        api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert home_group.church.uusers.filter(id=user.id).exists()

    def test_del_user_success(self, monkeypatch, api_login_client, home_group, user_factory):
        monkeypatch.setattr(HomeGroupViewSet, 'get_queryset', lambda s: s.queryset)
        url = reverse('homegroup-del-user', kwargs={'pk': home_group.id})
        user = user_factory()
        user.hhome_group = home_group
        user.save()

        response = api_login_client.post(url, data={'user_id': user.id}, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not home_group.uusers.filter(id=user.id).exists()

    @pytest.mark.parametrize('method,action,serializer_class', (
            ('post', 'create', HomeGroupSerializer),
            ('get', 'retrieve', HomeGroupReadSerializer),
            ('put', 'update', HomeGroupSerializer),
            ('patch', 'partial_update', HomeGroupSerializer),
    ), ids=('post-create', 'get-retrieve', 'put-update', 'patch-partial_update'))
    def test_get_serializer_class(self, rf, fake_home_group_view_set, method, action, serializer_class, user_factory):
        method_action = getattr(rf, method)
        request = method_action('/')
        request.user = user_factory(is_staff=True)
        view = fake_home_group_view_set.as_view({method: action})

        instance = view(request, pk=1)

        assert instance.get_serializer_class() == serializer_class
