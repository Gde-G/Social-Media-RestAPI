import pdb

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from core.test.test_setup import BaseApiTest
from .factories import PostFactory
from ..models import UserMention


class NoAuthUserMentionTestCase(APITestCase, PostFactory):
    def test_create_mention(self):
        post = self.create_post()

        url = reverse('user-mention')
        response = self.client.post(
            url,
            {
                'post': post.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_mention_body_not_have(self):
        post = self.create_post()

        url = reverse('user-mention')
        response = self.client.post(
            url,
            {
                'post': post.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthUserMentionTestCase(BaseApiTest, PostFactory):
    def test_create_mention(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body_with_mention()
        )

        url = reverse('user-mention')
        response = self.client.post(
            url,
            {
                'post': post.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserMention.objects.filter(post=post).exists())

    def test_create_mention_body_not_have(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body()
        )

        url = reverse('user-mention')
        response = self.client.post(
            url,
            {
                'post': post.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(UserMention.objects.filter(post=post).exists())


class AuthUserMentionFailTestCase(BaseApiTest):
    def test_fail_create_hashtag_post_not_found(self):

        url = reverse('user-mention')
        response = self.client.post(
            url,
            {
                'post': 234235
            }
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_fail_create_hashtag_post_not_found(self):

        url = reverse('user-mention')
        response = self.client.post(
            url,
            {}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_update_hashtag_not_allow_method(self):

        url = reverse('user-mention')
        response = self.client.patch(
            url,
            {
                'tag': '#MoangoLo'
            }
        )

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_fail_delete_hashtag_not_allow_method(self):

        url = reverse('user-mention')
        response = self.client.delete(
            url
        )

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
