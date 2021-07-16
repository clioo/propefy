from django.test import TestCase
from channels.testing import HttpCommunicator
from apps.user.consumers import MyConsumer

class MyTests(TestCase):
    async def test_my_consumer(self):
        communicator = HttpCommunicator(MyConsumer, "GET", "/test/")
        response = await communicator.get_response()
        self.assertEqual(response["body"], b"test response")
        self.assertEqual(response["status"], 200)
