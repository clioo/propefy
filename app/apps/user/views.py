from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from apps.user.serializers import (UserSerializer, AuthTokenSerializer,
                                   RecoveryPasswordSerializer,
                                   SendVerificationEmail)
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from apps.utils.tasks import send_email_template
from apps.core.models import User
from django.utils.http import urlsafe_base64_decode
from apps.core.tokens import account_activation_token
from django.utils.encoding import force_text
from django.http import HttpResponse

class CreateUserView(generics.CreateAPIView, ObtainAuthToken):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation.'
                            ' Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


class SendVerificationEmailView(generics.GenericAPIView):
    serializer_class = SendVerificationEmail

    def post(self, request):
        """Sends a recovery password email."""
        email = request.data.get('email')
        resp_dict = {'message': ''}
        try:
            mail_subject = 'Propefy recovery email'
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            url = settings.FRONTEND_RECOVERY_URL.format(
                base_url=settings.FRONTEND_BASE_URL,
                uid=uid,
                token=token
            )
            send_email_template.delay(
                mail_subject=mail_subject, to=[email],
                context={
                    'username': user.name,
                    'url': url
                },
                template_name="d-7a2265281aa4483b8c091ed3c4523aff"
            )
            status_code = status.HTTP_200_OK
            message = _('Email sent.')
        except Exception as e:
            message = _('An error occured, please try later.')
            if settings.DEBUG:
                resp_dict['error_message'] = str(e)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        resp_dict['message'] = message
        return Response(resp_dict, status_code)


class PasswordRecoveryValidateView(generics.GenericAPIView):
    serializer_class = RecoveryPasswordSerializer

    def get(self, request, uidb64, token):
        """Returns whether the activation link is still valid."""
        resp_dict = {'message': ''}
        try:
            message = _('The activation link is valid.')
            status_code = status.HTTP_200_OK
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            message = _('The activation link is not valid.')
            status_code = status.HTTP_400_BAD_REQUEST
        resp_dict['message'] = message
        return Response(resp_dict, status_code)


class PasswordRecoverySetView(generics.GenericAPIView):
    serializer_class = RecoveryPasswordSerializer

    def post(self, request):
        """Changes the user password by a validation email
           containing the token and the uidb64 variables."""
        resp_dict = {'message': ''}
        token = request.data.get('token')
        uidb64 = request.data.get('uidb64')
        password = request.data.get('password')
        message = ''
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user,
                                                                     token):
            user.set_password(password)
            user.save()
            token, created = Token.objects.get_or_create(user=user)
            message = _('Your password has been changed.')
            status_code = status.HTTP_200_OK
        else:
            message = _('Activation link is invalid!')
            status_code = status.HTTP_400_BAD_REQUEST
        if status_code == status.HTTP_200_OK:
            resp_dict['token'] = token.key
        resp_dict['message'] = message
        return Response(resp_dict, status_code)
