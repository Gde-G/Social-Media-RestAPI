import pdb

from django.urls import reverse

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from rest_framework import status
from rest_framework.test import APITestCase

from core.test.test_setup import BaseApiTest
from .factories import UserFactory
from ..models import User, Follower, Block


class NoAuthUserTestCase(APITestCase, UserFactory):
    def test_create_user_all_fields(self):
        url = reverse('users-list')
        profile_img_data = self.profile_img().file.getvalue()
        header_img_data = self.header_img().file.getvalue()
        profile_img_file = SimpleUploadedFile(
            'profile_img.jpg', profile_img_data, content_type='image/jpeg'),
        header_img_file = SimpleUploadedFile(
            'header_img.jpg', header_img_data, content_type='image/jpeg'),
        response = self.client.post(
            path=url,
            data={
                'password': 'Belgrano1905',
                'password2': 'Belgrano1905',
                'first_name': self.first_name(),
                'last_name': self.last_name(),
                'username': self.username(),
                'user_handle': self.user_handle(),
                'email': self.email(),
                'email_substitute': self.email_substitute(),
                'biography': self.biography(),
                'website': self.website(),
                'location': self.location(),
                'gender': self.gender(),
                'birth_date': self.birth_date(),
                'profile_img': profile_img_file,
                'header_photo': header_img_file
            },
        )

        created_user = User.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual('', created_user.profile_img)
        self.assertNotEqual('', created_user.header_photo)

    def test_create_user_needed_fields(self):
        url = reverse('users-list')

        response = self.client.post(
            path=url,
            data={
                'password': 'Belgrano1905',
                'password2': 'Belgrano1905',
                'first_name': self.first_name(),
                'last_name': self.last_name(),
                'username': self.username(),
                'user_handle': self.user_handle(),
                'email': self.email(),
                'gender': self.gender()
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_create_user_wrong_confirm_password(self):
        url = reverse('users-list')

        response = self.client.post(
            path=url,
            data={
                'password': 'Belgrano1905',
                'password2': 'Belgrano190',
                'first_name': self.first_name(),
                'last_name': self.last_name(),
                'username': self.username(),
                'user_handle': self.user_handle(),
                'email': self.email(),
                'gender': self.gender()
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_create_user_needed_fields_not_send(self):
        url = reverse('users-list')

        response = self.client.post(
            path=url,
            data={
                'password': 'Belgrano1905',
                'password2': 'Belgrano1905',
                'first_name': self.first_name(),

                'username': self.username(),
                'user_handle': self.user_handle(),

                'gender': self.gender()
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_create_user_field_unique_already_exist(self):
        url = reverse('users-list')
        data = {
            'password': 'Belgrano1905',
            'password2': 'Belgrano1905',
            'first_name': self.first_name(),
            'last_name': self.last_name(),
            'username': self.username(),
            'user_handle': self.user_handle(),
            'email': self.email(),
            'gender': self.gender()
        }
        response = self.client.post(
            path=url,
            data=data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(
            path=url,
            data=data,
            format='json',
        )

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)


class AuthUserTestCase(BaseApiTest, UserFactory):

    def test_get_users(self):

        url = reverse('users-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user(self):
        url = reverse('users-detail',
                      kwargs={'user_handle': self.user.user_handle})

        response = self.client.get(
            url,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        url = reverse('users-detail',
                      kwargs={'user_handle': self.user.user_handle})

        response = self.client.patch(
            url,
            {'first_name': 'Arty'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(user_handle=self.user.user_handle)

        self.assertTrue(user.first_name == 'Arty')

    def test_fail_update_other_user(self):
        url = reverse('users-list')

        response = self.client.post(
            path=url,
            data={
                'password': 'Belgrano1905',
                'password2': 'Belgrano1905',
                'first_name': self.first_name(),
                'last_name': self.last_name(),
                'username': self.username(),
                'user_handle': 'test_to_upd',
                'email': self.email(),
                'gender': self.gender(),
                'is_active': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url2 = reverse('users-detail', kwargs={'user_handle': 'test_to_upd'})
        response = self.client.patch(
            url2,
            {'first_name': 'Arty'}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user(self):
        url = reverse('users-detail',
                      kwargs={'user_handle': self.user.user_handle})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(user_handle=self.user.user_handle)

        self.assertFalse(user.is_active)


class NoAuthBlockTestCase(APITestCase, UserFactory):

    def test_fail_noauth_get_block_users(self):
        url = reverse('block-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_create_block_to_user(self):
        user = self.create_active_user()
        url = reverse('block-list')

        response = self.client.post(
            url,
            {
                'user_handle': user.user_handle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_delete_block_to_user(self):
        user = self.create_active_user()
        url = reverse('block-detail', kwargs={'user_handle': user.user_handle})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthBlockTestCase(BaseApiTest, UserFactory):

    def test_get_block_users(self):
        user = self.create_active_user()
        Block.objects.create(blocked_by=self.user, blocked_user=user)

        url = reverse('block-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_create_block_to_user(self):
        user = self.create_active_user()
        url = reverse('block-list')

        response = self.client.post(
            url,
            {
                'blocked_user': user.user_handle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Block.objects.filter(
            blocked_by=self.user, blocked_user=user).exists())

    def test_delete_block_to_user(self):
        user = self.create_active_user()
        url = reverse('block-detail', kwargs={'user_handle': user.user_handle})

        with transaction.atomic():
            Block.objects.create(blocked_by=self.user, blocked_user=user)
            response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Block.objects.filter(
            blocked_by=self.user, blocked_user=user).exists())


class NoAuthFollowerTestCase(APITestCase, UserFactory):

    def test_fail_noauth_create_follow(self):
        user = self.create_active_user()
        url = reverse('follows-list')
        response = self.client.post(
            url,
            {
                'following': user.user_handle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_delete_follow(self):
        user = self.create_active_user()
        url = reverse('follows-list')
        response = self.client.post(
            url,
            {
                'following': user.user_handle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_get_followers(self):

        user = self.create_active_user()
        url = reverse('follows-get-followers',
                      kwargs={'user_handle': user.user_handle})
        response = self.client.get(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_get_followings(self):

        user = self.create_active_user()
        url = reverse('follows-get-followings',
                      kwargs={'user_handle': user.user_handle})
        response = self.client.get(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthFollowerTestCase(BaseApiTest, UserFactory):
    def test_create_follow(self):
        user = self.create_active_user()

        url = reverse('follows-list')

        response = self.client.post(
            url,
            {
                'following': user.user_handle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(Follower.objects.filter(
            follower=self.user.user_handle, following=user.user_handle).exists())

    def test_delete_follow(self):
        user = self.create_active_user()

        url = reverse('follows-detail',
                      kwargs={'user_handle': user.user_handle})

        with transaction.atomic():
            Follower.objects.create(follower=self.user, following=user)

            response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(Follower.objects.filter(
            follower=self.user.user_handle, following=user.user_handle).exists())

    def test_get_followers(self):
        user = self.create_active_user()
        Follower.objects.create(follower=self.user, following=user)
        url = reverse('follows-get-followers',
                      kwargs={'user_handle': user.user_handle})
        response = self.client.get(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_get_followings(self):
        user = self.create_active_user()
        Follower.objects.create(follower=self.user, following=user)
        url = reverse('follows-get-followings',
                      kwargs={'user_handle': self.user.user_handle})
        response = self.client.get(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_fail_block_create_follow(self):
        user = self.create_active_user()
        Block.objects.create(blocked_by=user, blocked_user=self.user)

        url = reverse('follows-list')

        response = self.client.post(
            url,
            {
                'following': user.user_handle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(Follower.objects.filter(
            follower=self.user.user_handle, following=user.user_handle).exists())
