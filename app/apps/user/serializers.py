from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from apps.core.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage


class UserSerializer(serializers.ModelSerializer):
    """Serializers for the user object."""
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name', 'phone')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        validated_data['is_active'] = False
        user = get_user_model().objects.create_user(**validated_data)
        current_site = '127.0.0.1:8000'
        mail_subject = 'Activa tu cuenta propefy'
        message = render_to_string('acc_active_email.html', {
            'user': validated_data.get('name'),
            'domain': current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = validated_data.get('email')
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.send()
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