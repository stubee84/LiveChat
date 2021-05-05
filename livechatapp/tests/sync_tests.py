from collections import OrderedDict
from django.urls import reverse
from django.test import TestCase
from rest_framework import test, status
# from asgiref.sync import async_to_sync
# from unittest import mock
from ..models import User, Caller, Message
from ..controllers.main import password_management

class UserCreateTest(test.APITestCase):
    def setUp(self):
        self.test_user: User = User.objects.create(email='testuser@testaccount.com', password=password_management(password='Newp@ss123').hash())
        self.create_url = reverse('register')
    
    def test_create_user(self):
        data = {
            'email': 'emailuser@email.com',
            'password': 'testP4ss1'
        }

        response = self.client.post(path=self.create_url, data=data, format='json')

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], data['email'])
        self.assertFalse('password' in response.data)

class UserLoginTest(test.APITestCase):
    def setUp(self):
        self.test_user = User.objects.create(email='testuser@testaccount.com', password=password_management('Newp@ss123').hash())
        self.login_url = reverse('login')
    
    def test_get_user(self):
        data = {
            'email': 'testuser@testaccount.com',
            'password': 'Newp@ss123'
        }
        
        response = self.client.post(path=self.login_url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], data['email'])
        self.assertFalse('password' in response.data)

class GetNumbersTest(UserLoginTest):
    def setUp(self):
        super().setUp()
        
        Caller.objects.create(number=19194442222,country='USA',city='Miami',state='FL')
        Caller.objects.create(number=14243335555,country='USA',city='Boston',state='MA')
        self.numbers_url = reverse('numbers')

    def test_get_numbers(self):
        super().test_get_user()
        data = [{'number':19194442222},{'number':14243335555}]
        response = self.client.get(path=self.numbers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)

class GetMessagesTest(UserLoginTest):
    messages = [{'message':'This is my first basic text message for testing.'},{'message':'This is my second basic text message for testing.'}]
    def setUp(self):
        super().setUp()

        Message.objects.create(number=19194442222,call_id=1, message_type='S', message=self.messages[0])
        Message.objects.create(number=14243335555,call_id=2, message_type='S', message=self.messages[1])
        self.messages_url = reverse('messages',args=['19194442222'])

    def test_get_messages(self):
        super().test_get_user()

        response = self.client.get(path=self.messages_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['message'], str(self.messages[0]))