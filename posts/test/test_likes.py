import pdb

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from core.test.test_setup import BaseApiTest
from .factories import PostFactory
from ..models import Likes


class NoAuthLikesTestCase(APITestCase, PostFactory):
    def test_fail_noauth_get_like_from_post(self):
        post = self.create_post()

        url = reverse('likes-post', kwargs={'pk': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_create_like_from_post(self):
        post = self.create_post()

        url = reverse('likes-post', kwargs={'pk': post.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_delete_like_from_post(self):
        post = self.create_post()

        url = reverse('likes-post', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthLikesSuccessfulTestCase(BaseApiTest, PostFactory):
    def test_create_like_in_random_post(self):
        post = self.create_post()
        url = reverse('likes-post', kwargs={'pk': post.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Likes.objects.filter(
            post=post, user=self.user).exists())
        post.refresh_from_db()
        self.assertEqual(post.num_likes, 1)

    def test_create_like_in_own_post(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body()
        )
        url = reverse('likes-post', kwargs={'pk': post.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Likes.objects.filter(
            post=post, user=self.user).exists())
        post.refresh_from_db()
        self.assertEqual(post.num_likes, 1)

    def test_list_like_in_random_post(self):
        post = self.create_post()
        Likes.objects.create(post=post, user=self.user)

        url = reverse('likes-post', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIsInstance(response.data, list)
        self.assertIn('username', response.data[0])

    def test_list_like_in_own_post(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body()
        )
        Likes.objects.create(post=post, user=self.user)
        url = reverse('likes-post', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIsInstance(response.data, list)
        self.assertIn('username', response.data[0])

    def test_delete_like_in_random_post(self):
        post = self.create_post()
        post.num_likes = 1
        post.save()

        Likes.objects.create(post=post, user=self.user)
        url = reverse('likes-post', kwargs={'pk': post.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        post.refresh_from_db()
        self.assertEqual(post.num_likes, 0)
        self.assertFalse(Likes.objects.filter(
            post=post, user=self.user).exists())

    def test_delete_like_in_own_post(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            num_likes=1
        )

        Likes.objects.create(post=post, user=self.user)
        url = reverse('likes-post', kwargs={'pk': post.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        post.refresh_from_db()
        self.assertEqual(post.num_likes, 0)
        self.assertFalse(Likes.objects.filter(
            post=post, user=self.user).exists())


class AuthLikesFailTestCase(BaseApiTest, PostFactory):
    def test_create_like_in_post_nonexistent(self):
        url = reverse('likes-post', kwargs={'pk': 230984})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_like_in_post_nonexistent(self):
        url = reverse('likes-post', kwargs={'pk': 230984})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_like_in_post_nonexistent(self):
        url = reverse('likes-post', kwargs={'pk': 230984})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_like_in_post_that_not_existent_like(self):
        post = self.create_post()
        url = reverse('likes-post', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
