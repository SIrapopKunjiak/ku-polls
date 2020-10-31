"""Unittest for testing authentication"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from polls.models import Question


def create_user(username, email, password):
    User.objects.create_user(username=username, email=email, password=password)


class LoginTest(TestCase):
    """Class for test login system"""

    def test_simple_login(self):
        """If user must be authenticated in website"""
        create_user("Test_User1", "Test_User1@gmail.com", "isp123456")
        response = self.client.post(reverse('login'), {'username': 'Test_User1', 'password': 'isp123456'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)