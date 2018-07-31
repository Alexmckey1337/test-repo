from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

from apps.light_auth.models import LightAuthUser, PhoneNumber, LightToken, PhoneConfirmation
from apps.light_auth.utils import get_light_auth_user_model, setup_user_phone, make_phone_number

UserModel = get_light_auth_user_model()


class LightAuthSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(required=True, queryset=UserModel.objects.all())

    def validate_user(self, user):
        if LightAuthUser.objects.filter(user=user).exists():
            raise exceptions.ValidationError(_('LightAuthUser already exist.'))
        if not make_phone_number(user.phone_number):
            raise exceptions.ValidationError(_("User don't have phone number."))
        if PhoneNumber.objects.filter(phone=make_phone_number(user.phone_number)).exists():
            raise exceptions.ValidationError(_("User with phone number %s already exist.") % user.phone_number)
        return user

    def save(self, **kwargs):
        user = self.validated_data['user']
        auth_user = LightAuthUser(user=user)
        auth_user.set_password(None)
        auth_user.save()
        setup_user_phone(auth_user, [])
        return auth_user


class ResetPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, phone):
        phone = make_phone_number(phone)
        if phone is None:
            raise exceptions.ValidationError(_('Phone number invalid'))
        return phone


class VerifyPhoneSerializer(serializers.Serializer):
    key = serializers.CharField()
    phone_number = serializers.CharField()
    new_password = serializers.CharField(required=False)

    def validate_phone_number(self, phone):
        phone = make_phone_number(phone)
        if phone is None:
            raise exceptions.ValidationError(_('Phone number invalid'))
        return phone

    def validate_new_password(self, password):
        try:
            password_validation.validate_password(password, password_validators=[])
        except ValidationError as err:
            raise exceptions.ValidationError(err)
        return password


class PasswordChangeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def __init__(self, *args, **kwargs):
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

    def validate_phone_number(self, phone):
        phone = make_phone_number(phone)
        if phone is None:
            raise exceptions.ValidationError(_('Phone number invalid'))
        return phone

    def validate_new_password1(self, password):
        try:
            password_validation.validate_password(password, password_validators=[])
        except ValidationError as err:
            raise exceptions.ValidationError(err)
        return password

    def validate(self, attrs):
        auth_user = self.get_auth_user(attrs)
        auth_user.check_password(attrs['old_password'])

        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise exceptions.ValidationError(
                    _("The two password fields didn't match."),
                    code='password_mismatch',
                )
        return attrs

    def get_auth_user(self, attrs):
        try:
            phone_number = PhoneNumber.objects.get(
                phone=attrs['phone_number'], verified=True, primary=True
            )
        except PhoneNumber.DoesNotExist:
            raise exceptions.ValidationError(_('Phone number is unverified or not primary of the user'))
        except PhoneNumber.MultipleObjectsReturned:
            raise exceptions.ValidationError(_('Phone number is multiple'))
        return phone_number.auth_user

    def save(self):
        password = self.validated_data['new_password1']
        auth_user = self.get_auth_user(self.validated_data)
        auth_user.set_password(password)
        return auth_user.save()


class LightTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = LightToken
        fields = ('key',)


class LightLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(style={'input_type': 'password'}, required=True)

    def validate_phone_number(self, phone):
        phone = make_phone_number(phone)
        if phone is None:
            raise exceptions.ValidationError(_('Phone number invalid'))
        return phone

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = None

        # TODO

        #########################################################################
        # START = VERY BAD, DELETE IT
        #########################################################################
        confirmation = None
        try:
            phone = PhoneNumber.objects.get(phone=phone_number)
            confirmation = PhoneConfirmation.objects.filter(phone_number=phone).order_by('-created').first()
            user = phone.auth_user
        except PhoneNumber.DoesNotExist:
            pass

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
            if not confirmation or confirmation.key != password:
                raise exceptions.ValidationError({'detail': _('Password is invalid')})
        else:
            msg = _('User with phone %s does not exist.') % phone_number
            raise exceptions.ValidationError(msg)
        #########################################################################
        # END = VERY BAD, DELETE IT
        #########################################################################

        #########################################################################
        # START = GOOD, UNCOMMENT IT
        #########################################################################
        # try:
        #     phone = PhoneNumber.objects.get(phone=phone_number, primary=True, verified=True)
        #     user = phone.auth_user
        # except PhoneNumber.DoesNotExist:
        #     pass
        #
        # if user:
        #     if not user.is_active:
        #         msg = _('User account is disabled.')
        #         raise exceptions.ValidationError(msg)
        #     if not user.check_password(password):
        #         raise exceptions.ValidationError({'detail': _('Password is invalid')})
        # else:
        #     msg = _('User with phone %s does not exist.') % phone_number
        #     raise exceptions.ValidationError(msg)
        #########################################################################
        # END = GOOD, UNCOMMENT IT
        #########################################################################

        attrs['user'] = user
        return attrs
