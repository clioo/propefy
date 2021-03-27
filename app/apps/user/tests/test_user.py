import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from apps.core import models
from apps.utils.test_utils.utils import get_random_phone, get_random_username


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create a sample user"""
    if not params.get('email'):
        params['email'] = get_random_username() + '@test.com'
    if not params.get('password'):
        params['password'] = 'test123'
    if not params.get('username'):
        params['username'] = get_random_username()
    if not params.get('phone'):
        params['phone'] = get_random_phone()
    return get_user_model().objects.create_user(
        **params
    )



class PublicApiUser(TestCase):
    """Testing public API endpoints."""
    def setUp(self):
        self.client = APIClient()

    def test_get_me_invalid(self):
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiUserCreateTests(TestCase):
    """Testing the public user api endpoints"""

    def setUp(self):
        self.client = APIClient()


class PrivateApiUserProfile(TestCase):
    """
    Assert that the token is generated and validated.
    """

    def setUp(self):
        payload = {
            'email': 'test1@test3.com',
            'username': 'testusername3',
            'phone': '+526681596075',
            'password': 'password12345',
            'name': 'rodolfo'
        }
        user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_get_me_valid(self):
        """Test that a token is created for the user"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('token', response.data)
