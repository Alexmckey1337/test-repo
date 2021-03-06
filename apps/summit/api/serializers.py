from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.account.api.serializers import UserTableSerializer, UserShortSerializer, UserForSelectSerializer
from apps.account.models import CustomUser as User, CustomUser
from apps.summit.models import (
    Summit, SummitAnket, SummitType, SummitAnketNote, SummitLesson, AnketEmail,
    SummitTicket, SummitVisitorLocation, SummitEventTable, SummitAttend, AnketStatus, TelegramPayment)
from common.fields import ListCharField, ReadOnlyChoiceWithKeyField


class ImageWithoutHostField(serializers.ImageField):
    def to_representation(self, value):
        url = super().to_representation(value)
        return settings.MEDIA_URL + url if url else url


class SummitAnketNoteSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = SummitAnketNote
        fields = ('summit_anket', 'text', 'owner', 'date_created', 'owner_name')
        read_only_fields = ('owner', 'date_created', 'id')
        extra_kwargs = {'summit_anket': {'write_only': True}}


class AnketEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnketEmail
        fields = ('id', 'created_at')


class SummitAnketSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.IntegerField(source='user.user_ptr_id')
    emails = AnketEmailSerializer(many=True, read_only=True)
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=0)
    full_name = serializers.CharField()
    email = serializers.CharField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    social = ListCharField(fields=('user.facebook', 'user.vkontakte', 'user.odnoklassniki', 'user.skype'))
    region = serializers.CharField(source='user.region')
    district = serializers.CharField(source='user.district')
    address = serializers.CharField(source='user.address')
    born_date = serializers.CharField(source='user.born_date')
    repentance_date = serializers.CharField(source='user.repentance_date')
    spiritual_level = serializers.CharField(source='get_spiritual_level_display')
    ticket_status = ReadOnlyChoiceWithKeyField(choices=SummitAnket.TICKET_STATUSES, read_only=True)
    e_ticket = serializers.BooleanField(source='status.reg_code_requested', read_only=True)
    reg_code = serializers.CharField()
    has_email = serializers.BooleanField()
    has_achievement = serializers.BooleanField()
    author = UserForSelectSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user_id', 'full_name', 'responsible', 'spiritual_level',
                  'divisions_title', 'department', 'hierarchy_title', 'phone_number', 'email', 'social',
                  'country', 'city', 'region', 'district', 'address', 'born_date', 'repentance_date',
                  'code', 'value', 'description',
                  'emails',
                  'visited',
                  'link',
                  'ticket_status',

                  'total_sum', 'e_ticket',
                  'reg_code',
                  'has_email', 'has_achievement',
                  'author',
                  )


class SummitUserDeviceSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.IntegerField(source='user.user_ptr_id')
    email = serializers.CharField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    device_code = serializers.CharField()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user_id', 'phone_number', 'email', 'device_code')


class ProfileTableSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.IntegerField(source='user.user_ptr_id')
    emails = AnketEmailSerializer(many=True, read_only=True)
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=0)
    full_name = serializers.CharField()
    email = serializers.CharField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    social = ListCharField(fields=('user.facebook', 'user.vkontakte', 'user.odnoklassniki', 'user.skype'))
    region = serializers.CharField(source='user.region')
    district = serializers.CharField(source='user.district')
    address = serializers.CharField(source='user.address')
    born_date = serializers.CharField(source='user.born_date')
    repentance_date = serializers.CharField(source='user.repentance_date')
    spiritual_level = serializers.CharField(source='get_spiritual_level_display')
    ticket_status = ReadOnlyChoiceWithKeyField(choices=SummitAnket.TICKET_STATUSES, read_only=True)
    e_ticket = serializers.BooleanField(source='status.reg_code_requested', read_only=True)
    reg_code = serializers.CharField()
    has_email = serializers.BooleanField()
    has_achievement = serializers.BooleanField()
    author = UserForSelectSerializer()

    class Meta:
        model = SummitAnket
        required_fields = ['id', 'link', 'has_achievement', 'user_id', 'code', 'reg_code', 'full_name', 'responsible',
                           'value']
        fields = ('id', 'user_id', 'full_name', 'responsible', 'spiritual_level',
                  'divisions_title', 'department', 'hierarchy_title', 'phone_number', 'email', 'social',
                  'country', 'city', 'region', 'district', 'address', 'born_date', 'repentance_date',
                  'code', 'value', 'description',
                  'link',
                  'ticket_status',
                  'e_ticket',
                  'reg_code',
                  'has_email',
                  'has_achievement',
                  'author',

                  'emails',
                  'visited',
                  'total_sum',
                  )

    def get_field_names(self, declared_fields, info):
        fields = getattr(self.Meta, 'fields', None)
        if self.context.get('request') is not None:
            columns = self.context.get('columns', [])
            return (self.Meta.required_fields +
                    [c for c in columns.keys() if columns[c]['active'] and c != 'action'] +
                    list(self._context.get('extra_fields', [])))
        return fields


class SummitProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitAnket
        fields = ('description', 'author')


class SummitProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitAnket
        fields = ('summit', 'user', 'author', 'description',)

    def validate_summit(self, summit):
        if summit.status == Summit.CLOSE:
            raise serializers.ValidationError(
                {'message': _('Нельзя добавлять пользователей в закрытый саммит.')})
        return summit

    def validate(self, attrs):
        author = attrs.get('author')
        user = attrs.get('user')
        if author is None and user.hierarchy.level < 50:  # Главный епископ
            raise serializers.ValidationError(
                {'message': _('Автор регистрации обязательное поле')}
            )
        if author is not None and not SummitAnket.objects.filter(summit=attrs['summit'], user=author).exists():
            raise serializers.ValidationError(
                {'message': _('Автор регистрации должен быть зарегестрирован на саммит')}
            )
        return attrs


class SummitAnketStatisticsSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    phone_number = serializers.CharField(source='user.phone_number')
    attended = serializers.CharField()
    active = serializers.BooleanField(source='status.active')
    author = UserForSelectSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user_id', 'full_name', 'responsible', 'author', 'link',
                  'department', 'phone_number', 'code', 'attended', 'active')


class SummitAnketShortSerializer(serializers.HyperlinkedModelSerializer):
    user = UserTableSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'user', 'code', 'description', 'visited')


class SummitAnketForSelectSerializer(serializers.HyperlinkedModelSerializer):
    user = UserShortSerializer()

    class Meta:
        model = SummitAnket
        fields = ('id', 'role', 'user')


class UserWithLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'fullname', 'link')


class SummitAnketForTicketSerializer(serializers.HyperlinkedModelSerializer):
    user = UserWithLinkSerializer()
    is_active = serializers.BooleanField()

    class Meta:
        model = SummitAnket
        fields = ('id', 'code', 'user', 'is_active')


class SummitShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'title', 'description')


class SummitUnregisterUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'city', 'fullname', 'country', 'master_short_fullname',
                  'phone_number', 'email')


class SummitLessonSerializer(serializers.ModelSerializer):
    viewers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = SummitLesson
        fields = ('summit', 'name', 'viewers')
        # extra_kwargs = {'viewers': {'required': False}}


class SummitLessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitLesson
        fields = ('summit', 'name')


# UNUSED


class SummitSerializer(serializers.HyperlinkedModelSerializer):
    lessons = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'title', 'description', 'lessons', 'club_name',
                  'full_cost', 'special_cost')


class SummitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SummitType
        fields = ('id', 'title', 'image')


class SummitTypeTitleForAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitType
        fields = ('title',)


# FOR APP


class ChildrenLink(serializers.RelatedField):
    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            self.view_name = view_name
        assert self.view_name is not None, 'The `view_name` argument is required.'
        self.summit_id = kwargs.pop('summit_kwarg', 'summit_id')
        self.master_id = kwargs.pop('master_kwarg', 'master_id')

        super(ChildrenLink, self).__init__(**kwargs)

    def get_attribute(self, instance):
        summit_id = instance.summit_id
        master_id = instance.user_id
        has_children = instance.numchild > 0

        return summit_id, master_id, has_children

    def to_representation(self, value):
        summit_id, master_id, has_children = value
        if has_children:
            return reverse(self.view_name, kwargs={self.summit_id: summit_id, self.master_id: master_id})
        return None


class SummitVisitorLocationSerializer(serializers.ModelSerializer):
    visitor_id = serializers.IntegerField(source='visitor.id')

    class Meta:
        model = SummitVisitorLocation
        fields = ('visitor_id', 'date_time', 'longitude', 'latitude', 'type')


class AnketStatusSerializer(serializers.ModelSerializer):
    reg_code_requested_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = AnketStatus
        fields = ('reg_code_requested', 'reg_code_requested_date', 'active')

    def get_attribute(self, instance):
        instance = super().get_attribute(instance)
        if instance is None:
            return AnketStatus()
        return instance


class SummitProfileTreeForAppSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    master_fio = serializers.CharField(source='responsible')
    user_id = serializers.IntegerField(source='user.user_ptr_id')
    phone_number = serializers.CharField(source='user.phone_number')
    extra_phone_numbers = serializers.ListField(source='user.extra_phone_numbers')
    children = ChildrenLink(view_name='summit-app-profile-list-master',
                            queryset=SummitAnket.objects.all())
    photo = ImageWithoutHostField(source='user.image', use_url=False)
    status = AnketStatusSerializer(serializers.ModelSerializer)

    class Meta:
        model = SummitAnket
        fields = (
            'id', 'user_id', 'master_id',
            'full_name', 'country', 'city', 'phone_number', 'extra_phone_numbers',
            'master_fio', 'hierarchy_id',
            'children',
            'photo',
            'status'
        )


class SummitTicketSerializer(serializers.ModelSerializer):
    summit_type = serializers.IntegerField(source='summit.type.id')
    summit = SummitSerializer()
    owner = UserShortSerializer()

    class Meta:
        model = SummitTicket
        fields = ('id', 'title', 'summit', 'summit_type', 'owner', 'attachment',
                  'status', 'get_status_display')


class SummitForAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'description')


class SummitTypeForAppSerializer(serializers.ModelSerializer):
    summits = SummitForAppSerializer(many=True, read_only=True)

    class Meta:
        model = SummitType
        fields = ('title', 'summits')


class OpenSummitsForAppSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='type.title', read_only=True)

    class Meta:
        model = Summit
        fields = ('id', 'title', 'status')


class UserForAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name', 'country', 'city',
                  'email', 'phone_number', 'email')  # + ('region', 'district', 'address', 'image_source')


class VisitorsMasterForAppSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)
    hierarchy = serializers.CharField(read_only=True)
    fullname = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('user_id', 'fullname', 'hierarchy')


class SummitAnketForAppSerializer(serializers.ModelSerializer):
    user = UserForAppSerializer()
    ticket_id = serializers.CharField(source='code')
    visitor_id = serializers.IntegerField(source='id')
    avatar_url = ImageWithoutHostField(source='user.image', use_url=False)
    status = AnketStatusSerializer(read_only=True)
    master = VisitorsMasterForAppSerializer()

    class Meta:
        model = SummitAnket
        fields = ('visitor_id', 'user', 'ticket_id', 'reg_code', 'avatar_url',
                  'status', 'master')


class SummitAnketDrawForAppSerializer(serializers.ModelSerializer):
    user = UserForAppSerializer()
    ticket_id = serializers.CharField(source='code')
    visitor_id = serializers.IntegerField(source='id')
    avatar_url = ImageWithoutHostField(source='user.image', use_url=False)
    status = AnketStatusSerializer(read_only=True)
    master = VisitorsMasterForAppSerializer()
    count = serializers.CharField(source='c')

    class Meta:
        model = SummitAnket
        fields = ('visitor_id', 'user', 'ticket_id', 'reg_code', 'avatar_url',
                  'status', 'master', 'count')


class SummitAnketLocationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.fullname')

    class Meta:
        model = SummitAnket
        fields = ('id', 'fullname')


class SummitEventTableSerializer(serializers.ModelSerializer):
    summit_id = serializers.IntegerField(source='summit.id')

    class Meta:
        model = SummitEventTable
        fields = ('summit_id', 'hide_time', 'date', 'time', 'name_ru', 'author_ru', 'name_en',
                  'author_en', 'name_de', 'author_de')


class SummitAnketCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitAnket
        fields = ('code',)


class SummitNameAnketCodeSerializer(SummitAnketCodeSerializer):
    name = serializers.CharField(source='summit.__str__', read_only=True)
    title = serializers.CharField(source='summit.description', read_only=True)

    class Meta(SummitAnketCodeSerializer.Meta):
        fields = SummitAnketCodeSerializer.Meta.fields + ('name', 'title', 'summit_id')


class SummitAttendSerializer(serializers.ModelSerializer):
    # time = serializers.TimeField()
    code = serializers.CharField(source='anket.code', read_only=True)

    class Meta:
        model = SummitAttend
        fields = ('anket', 'code', 'date')


class SummitAcceptMobileCodeSerializer(serializers.ModelSerializer):
    visitor_id = serializers.IntegerField(source='id', read_only=True)
    avatar_url = ImageWithoutHostField(source='user.image', use_url=False)
    ticket_id = serializers.CharField(source='code', read_only=True)
    passes_count = serializers.IntegerField(source='get_passes_count', read_only=True)
    active = serializers.BooleanField(source='status.active', read_only=True)

    class Meta:
        model = SummitAnket
        fields = ('visitor_id', 'fullname', 'avatar_url', 'ticket_id', 'passes_count', 'active')


class AnketActiveStatusSerializer(serializers.ModelSerializer):
    active = serializers.IntegerField(source='status.active')
    anket_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = SummitAnket
        fields = ('anket_id', 'active')


class MasterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ('id', 'full_name')


class TelegramPaymentSerializer(serializers.ModelSerializer):
    summit = SummitSerializer()

    class Meta:
        model = TelegramPayment
        fields = ('id', 'fullname', 'phone_number', 'summit', 'reg_date', 'amount',
                  'currency', 'paid', 'paid_date', 'ticket_given', 'secret',
                  'liqpay_payment_id', 'liqpay_order_id', 'liqpay_payment_url', 'chat_id')
