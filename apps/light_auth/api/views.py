from django.utils.translation import ugettext_lazy as _
from rest_framework import generics
from rest_framework import status, exceptions, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.account.api.serializers import VoUserSerializer
from apps.light_auth.api.permissions import CanCreateLightAuth, \
    CanConfirmPhoneNumberLightAuth, CanChangeLightAuthPassword, CanVerifyPhoneLightAuth, CanResetPasswordLightAuth, \
    CanLightLogin, CanLightPing
from apps.light_auth.api.serializers import LightAuthSerializer, VerifyPhoneSerializer, PasswordChangeSerializer, \
    ResetPhoneSerializer, LightTokenSerializer, LightLoginSerializer
from apps.light_auth.models import PhoneNumber, LightAuthUser, PhoneConfirmation, LightToken
from apps.light_auth.utils import get_light_auth_user_model, make_phone_number

UserModel = get_light_auth_user_model()


class LightAuthCreateView(generics.CreateAPIView):
    queryset = UserModel.objects.filter(is_active=True)
    serializer_class = LightAuthSerializer
    permission_classes = (IsAuthenticated, CanCreateLightAuth)

    def get_response_data(self, auth_user):
        return {"detail": _("Verification phone number for user %s sent.") % str(auth_user)}

    def create(self, request, *args, **kwargs):
        user = self.get_object()
        data = {'user': user}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        auth_user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(auth_user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        auth_user = serializer.save(request=self.request)
        phone = PhoneNumber.objects.get_primary(auth_user)
        phone.send_confirmation(reset_password=True)
        return auth_user


class LightAuthConfirmPhoneNumberView(generics.GenericAPIView):
    queryset = UserModel.objects.filter(is_active=True)
    permission_classes = (IsAuthenticated, CanConfirmPhoneNumberLightAuth)

    def get_response_data(self, auth_user, reset_password=False):
        if reset_password:
            return {"detail": _("Reset password for user %s sent.") % str(auth_user)}
        return {"detail": _("Verification phone number for user %s sent.") % str(auth_user)}

    def post(self, request, *args, **kwargs):
        reset_password = request.query_params.get('reset_password', 'false')
        reset_password = reset_password.lower() in ('true', 't', '1', 'yes', 'y', 'on')
        user = self.get_object()
        try:
            auth_user = LightAuthUser.objects.get(user=user)
        except LightAuthUser.DoesNotExist:
            raise exceptions.ValidationError(_('LightAuthUser does not exist.'))
        phone = PhoneNumber.objects.get_primary(auth_user)
        if phone is None:
            new_phone = make_phone_number(user.phone_number)
            if not new_phone:
                raise exceptions.ValidationError(_("User don't have phone number."))
            if PhoneNumber.objects.filter(phone=new_phone).exclude(auth_user=auth_user).exists():
                raise exceptions.ValidationError(_("User with phone number %s already exist.") % user.phone_number)
            phone = PhoneNumber.objects.add_phone(
                request, auth_user, new_phone, confirm=True, reset_password=reset_password)
            # phone.set_as_primary()
            # raise exceptions.ValidationError(_('Phone number does not confirmation'))
        else:
            phone.send_confirmation(reset_password=reset_password)

        return Response(self.get_response_data(auth_user, reset_password=reset_password))


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = (CanResetPasswordLightAuth,)

    def get_response_data(self, auth_user, reset_password=False):
        return {"detail": _("Reset password for user %s sent.") % str(auth_user)}

    def post(self, request, *args, **kwargs):
        reset_password = True
        serializer = ResetPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            phone = PhoneNumber.objects.get(
                phone=serializer.validated_data['phone_number'], primary=True, verified=True)
        except PhoneNumber.DoesNotExist:
            raise exceptions.ValidationError(
                _('User with phone %s does not exist.') % serializer.validated_data['phone_number'])
        else:
            phone.send_confirmation(reset_password=reset_password)

        return Response(self.get_response_data(phone.auth_user, reset_password=reset_password))


class VerifyPhoneView(views.APIView):
    permission_classes = (CanVerifyPhoneLightAuth,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyPhoneSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation = self.get_object(serializer.validated_data)
        confirmation.confirm(self.request)
        self.set_password(serializer.validated_data, confirmation.phone_number.auth_user)
        return Response({'detail': _('ok')}, status=status.HTTP_200_OK)

    def get_queryset(self):
        qs = PhoneConfirmation.objects.all_valid()
        qs = qs.select_related("phone_number__auth_user")
        return qs

    def get_object(self, data, queryset=None):
        key = data['key']
        phone = data['phone_number']
        if queryset is None:
            queryset = self.get_queryset()
        try:
            phone_confirmation = queryset.get(key=key.lower(), phone_number__phone=phone)
        except PhoneConfirmation.DoesNotExist:
            err_code = 'invalid_phone_or_key'
            raise exceptions.ValidationError(detail={
                'detail': _('Invalid phone number or key'),
                # 'code': err_code
            }, code=err_code)
        return phone_confirmation

    def set_password(self, data, auth_user):
        new_password = data.get('new_password')
        if new_password:
            auth_user.set_password(new_password)
            auth_user.save()


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (CanChangeLightAuthPassword,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("New password has been saved.")})


class LightLoginView(generics.GenericAPIView):
    serializer_class = LightLoginSerializer
    permission_classes = (CanLightLogin,)

    def login(self):
        self.light_user = self.serializer.validated_data['user']
        self.token, _ = LightToken.objects.get_or_create(user=self.light_user)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)

        self.login()
        serializer = LightTokenSerializer(instance=self.token, context={'request': self.request})
        data = VoUserSerializer(self.light_user.user).data
        data.update(serializer.data)
        return Response(data=data, status=status.HTTP_200_OK)


class CheckLightTokenView(generics.GenericAPIView):
    permission_classes = (CanLightPing,)

    def post(self, request, *args, **kwargs):

        try:
            token = LightToken.objects.get(key=request.data['key'])
        except LightToken.DoesNotExist:
            raise exceptions.ValidationError({
                'detail': _('Key invalid'),
                'code': 'invalid_key'
            })
        user = token.user
        phone_number = PhoneNumber.objects.get_primary(auth_user=user)

        return Response({
            'phone_number': phone_number.phone if phone_number else ''
        }, status=status.HTTP_200_OK)
