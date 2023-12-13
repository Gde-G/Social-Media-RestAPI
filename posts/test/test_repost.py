import pdb

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from core.test.test_setup import BaseApiTest
from .factories import PostFactory
from ..models import Repost


class NoAuthRepostsTestCase(APITestCase, PostFactory):
    def test_fail_noauth_get_repost_from_post(self):
        post = self.create_post()

        url = reverse('reposts-post', kwargs={'pk': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_create_repost_from_post(self):
        post = self.create_post()

        url = reverse('reposts-post', kwargs={'pk': post.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_delete_repost_from_post(self):
        post = self.create_post()

        url = reverse('reposts-post', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthRepostSuccessfulTestCase(BaseApiTest, PostFactory):
    def test_create_repost_in_random_post(self):
        post = self.create_post()
        url = reverse('reposts-post', kwargs={'pk': post.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Repost.objects.filter(
            post=post, user=self.user).exists())
        post.refresh_from_db()
        self.assertEqual(post.num_repost, 1)

    def test_create_repost_in_own_post(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body()
        )
        url = reverse('reposts-post', kwargs={'pk': post.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Repost.objects.filter(
            post=post, user=self.user).exists())
        post.refresh_from_db()
        self.assertEqual(post.num_repost, 1)

    def test_list_repost_in_random_post(self):
        post = self.create_post()
        Repost.objects.create(post=post, user=self.user)

        url = reverse('reposts-post', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIsInstance(response.data, list)
        self.assertIn('username', response.data[0])

    def test_list_repost_in_own_post(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body()
        )
        Repost.objects.create(post=post, user=self.user)
        url = reverse('reposts-post', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIsInstance(response.data, list)
        self.assertIn('username', response.data[0])

    def test_delete_repost_in_random_post(self):
        post = self.create_post()
        post.num_repost = 1
        post.save()

        Repost.objects.create(post=post, user=self.user)
        url = reverse('reposts-post', kwargs={'pk': post.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        post.refresh_from_db()
        self.assertEqual(post.num_repost, 0)
        self.assertFalse(Repost.objects.filter(
            post=post, user=self.user).exists())

    def test_delete_repost_in_own_post(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            num_repost=1
        )

        Repost.objects.create(post=post, user=self.user)
        url = reverse('reposts-post', kwargs={'pk': post.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        post.refresh_from_db()
        self.assertEqual(post.num_repost, 0)
        self.assertFalse(Repost.objects.filter(
            post=post, user=self.user).exists())


class AuthRepostsFailTestCase(BaseApiTest, PostFactory):
    def test_create_repost_in_post_nonexistent(self):
        url = reverse('reposts-post', kwargs={'pk': 230984})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_repost_in_post_nonexistent(self):
        url = reverse('reposts-post', kwargs={'pk': 230984})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_repost_in_post_nonexistent(self):
        url = reverse('reposts-post', kwargs={'pk': 230984})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_repost_in_post_that_not_existent_repost(self):
        post = self.create_post()
        url = reverse('reposts-post', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
