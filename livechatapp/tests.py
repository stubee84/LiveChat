from django.urls import reverse
from rest_framework import test, status
from .models import User

class UserCreateTest(test.APITestCase):
    def setUp(self):
        self.test_user = User.objects.create(email='testuser@testaccount.com', password='Newp@ss123')
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
        