from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from faker import Faker


faker = Faker()


class BaseApiTest(APITestCase):
    def setUp(self):
        self.user = self.create_test_user()

        self.token = self.get_access_token()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def create_test_user(self):
        return get_user_model().objects.create_user(
            username='testuser',
            user_handle='testuser',
            password='testpassword',
            email=faker.email(),
            first_name='perror',
            last_name='Malongo',
            is_active=True,
        )

    def get_access_token(self):
        response = self.client.post(
            '/token/', {'email': self.user.username, 'password': 'testpassword'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials()
        return response.data['access']

    def test_setup(self):
        pass
