from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, UpdateAPIView, RetrieveUpdateAPIView, \
	get_object_or_404
from rest_framework.response import Response

from apps.manager.models import GroupsManager
from apps.manager.api.serializers import GroupManagerListSerializer, GroupManagerWriteSerializer, GroupManagerDetailSerializer
from apps.manager.api.paginations import StandardPagination
from apps.account.api.permissions import HasUserTokenPermission


class GroupManagerListView(ListCreateAPIView):
    model = GroupsManager
    permission_classes = (HasUserTokenPermission,)    # TODO: ADD PERMISSIONS FOR THIS ACTIONS
    serializer_class = GroupManagerListSerializer
    queryset = GroupsManager.objects.all()
    pagination_class = StandardPagination

    def create(self, request, *args, **kwargs):
        write_serializer = GroupManagerWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()
        read_serializer = GroupManagerListSerializer(write_serializer.instance)
        return Response(read_serializer.data)


class GroupManagerDetailView(RetrieveUpdateAPIView):
    model = GroupsManager
    permission_classes = (HasUserTokenPermission,)  # TODO: ADD PERMISSIONS FOR THIS ACTIONS
    serializer_class = GroupManagerDetailSerializer
    queryset = GroupsManager.objects.all()

    def update(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(GroupsManager, pk=pk)
        write_serializer = GroupManagerWriteSerializer(instance, data=request.data)
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()
        read_serializer = GroupManagerDetailSerializer(write_serializer.instance)
        return Response(read_serializer.data)