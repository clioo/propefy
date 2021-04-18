from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from apps.core.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from rest_framework.authtoken.models import Token
from django.conf import settings
from apps.utils.tasks import send_email_template


class UserSerializer(serializers.ModelSerializer):
    """Serializers for the user object."""
    token = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ('token', 'email', 'password', 'name', 'last_name', 'phone')
        read_only_fields = ('token',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8,
                                     'max_length': 16},
                        'token': {'read_only': True}}

    def get_token(self, user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        validated_data['is_active'] = True
        user = get_user_model().objects.create_user(**validated_data)
        current_site = settings.FRONTEND_BASE_URL
        mail_subject = 'Activa tu cuenta propefy'
        to_email = validated_data.get('email')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        url = settings.FRONTEND_RECOVERY_URL.format(base_url=settings.FRONTEND_BASE_URL,
            uid=uid, token=token)
        context = {
            'user': validated_data.get('name'),
            'domain': current_site,
            'url': url
        }
        send_email_template.delay(
            mail_subject=mail_subject, to=[to_email],
            context=context, template_name='registration_email.html'
        )
        return user

    def update(self, instance, validated_data):
        """Update the user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs


class RecoveryPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    uidb64 = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        trim_whitespace=False,
        style={'input_type': 'password'},
        min_length=5,
        max_length=18
    )


class SendVerificationEmail(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=13)
