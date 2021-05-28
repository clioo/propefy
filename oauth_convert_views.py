# -*- coding: utf-8 -*-
import json

from braces.views import CsrfExemptMixin
from django.db import IntegrityError
from oauthlib.oauth2.rfc6749.endpoints.token import TokenEndpoint
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import Application, AccessToken
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.models import RefreshToken
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from apps.core.models import User
from .oauth2_backends import KeepRequestCore
from .oauth2_endpoints import SocialTokenServer


class TokenView(CsrfExemptMixin, OAuthLibMixin, APIView):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:

    * Authorization code
    * Password
    * Client credentials
    """
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = OAuthLibCore
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # Use the rest framework `.data` to fake the post body of the django request.
        request._request.POST = request._request.POST.copy()
        for key, value in request.data.items():
            request._request.POST[key] = value

        url, headers, body, status = self.create_token_response(request._request)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v
        return response


class ConvertTokenView(CsrfExemptMixin, OAuthLibMixin, APIView):
    """
    Implements an endpoint to convert a provider token to an access token

    The endpoint is used in the following flows:

    * Authorization code
    * Client credentials
    """
    server_class = SocialTokenServer
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = KeepRequestCore
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # Use the rest framework `.data` to fake the post body of the django request.
        request._request.POST = request._request.POST.copy()
        for key, value in request.data.items():
            request._request.POST[key] = value

        headers = {'Content-Type': 'application/json',
                    'Cache-Control': 'no-store', 'Pragma': 'no-cache'}
        try:
            url, headers, body, status = self.create_token_response(request._request)
            body = json.loads(body)
            token = RefreshToken.objects.get(token=body.get('refresh_token'))
            user = token.user
        except IntegrityError as e:
            # we obtain email from integrity error
            message = str(e)
            splitted_str = message.split('Key (email)=(')
            if len(splitted_str) == 1:
                status = 400
                body = {'message': 'Bad request.', 'error_message': str(e)}
            else:
                message = splitted_str[1]
                splitted_str = message.split(')')
                email = splitted_str[0]
                user = User.objects.get(email=email)
                status = 200
        except Exception as e:
            status = 400
            body = {'message': 'Bad request.', 'error_message': str(e)}

        # Obtaining and retrieving rest_framework token
        try:
            token, created = Token.objects.get_or_create(user=user)
            body = {
                'id': token.user.id,
                'email': token.user.email,
                'token': token.key,
                'new_user': created
            }
            response = Response(data=body, status=status)
        except:
            response = Response(data=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response


class RevokeTokenView(CsrfExemptMixin, OAuthLibMixin, APIView):
    """
    Implements an endpoint to revoke access or refresh tokens
    """
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = OAuthLibCore
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # Use the rest framework `.data` to fake the post body of the django request.
        request._request.POST = request._request.POST.copy()
        for key, value in request.data.items():
            request._request.POST[key] = value

        url, headers, body, status = self.create_revocation_response(request._request)
        response = Response(data=json.loads(body) if body else '', status=status if body else 204)

        for k, v in headers.items():
            response[k] = v
        return response


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
@permission_classes([permissions.IsAuthenticated])
def invalidate_sessions(request):
    client_id = request.POST.get("client_id", None)
    if client_id is None:
        return Response({
            "client_id": ["This field is required."]
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        app = Application.objects.get(client_id=client_id)
    except Application.DoesNotExist:
        return Response({
            "detail": "The application linked to the provided client_id could not be found."
        }, status=status.HTTP_400_BAD_REQUEST)

    tokens = AccessToken.objects.filter(user=request.user, application=app)
    tokens.delete()
    return Response({}, status=status.HTTP_204_NO_CONTENT)
