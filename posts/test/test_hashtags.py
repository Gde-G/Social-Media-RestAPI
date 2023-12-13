import pdb
import random

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from core.test.test_setup import BaseApiTest
from .factories import PostFactory, HashtagFactory
from ..models import Hashtag, HashtagsPost


class NoAuthHashtagsTestCase(APITestCase, PostFactory, HashtagFactory):
    def test_fail_noauth_create_hashtag(self):
        url = reverse('hashtags')
        response = self.client.post(
            url,
            {
                'post': 1
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_create_hashtag_body_not_have(self):

        url = reverse('hashtags')
        response = self.client.post(
            url,
            {
                'post': 1
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_get_hashtags_less_than_15(self):
        for _ in range(14):
            Hashtag.objects.create(
                tag=self.hashtag(),
                amount_use=random.randint(0, 14)
            )

        url = reverse('hashtags')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_get_hashtags_greater_than_15(self):
        for _ in range(26):
            Hashtag.objects.create(
                tag=self.hashtag(),
                amount_use=random.randint(0, 14)
            )

        url = reverse('hashtags')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthHashtagsTestCase(BaseApiTest, PostFactory, HashtagFactory):
    def test_create_hashtag(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body_with_hashtag()
        )

        url = reverse('hashtags')
        response = self.client.post(
            url,
            {
                'post': post.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Hashtag.objects.all().count(), 1)
        self.assertTrue(HashtagsPost.objects.filter(post=post).exists())

    def test_create_hashtag_body_not_have(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body()
        )

        url = reverse('hashtags')
        response = self.client.post(
            url,
            {
                'post': post.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Hashtag.objects.all().count(), 0)
        self.assertFalse(HashtagsPost.objects.filter(post=post).exists())

    def test_get_hashtags_paginated(self):
        for _ in range(14):
            Hashtag.objects.create(
                tag=self.hashtag(),
                amount_use=random.randint(0, 14)
            )

        url = reverse('hashtags')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 14)
        self.assertIsNotNone(response.data['next'])

    # def test_get_hashtags_paginated_page_size(self):
        # pass


class AuthHashtagsFailTestCase(BaseApiTest, PostFactory, HashtagFactory):

    def test_fail_create_hashtag_post_not_found(self):

        url = reverse('hashtags')
        response = self.client.post(
            url,
            {
                'post': 234235
            }
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_fail_create_hashtag_post_not_found(self):

        url = reverse('hashtags')
        response = self.client.post(
            url,
            {}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_update_hashtag_not_allow_method(self):
        hashtag = Hashtag.objects.create(tag='#MongoLo')
        url = reverse('hashtags')
        response = self.client.patch(
            url,
            {
                'tag': '#MoangoLo'
            }
        )

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_fail_delete_hashtag_not_allow_method(self):
        hashtag = Hashtag.objects.create(tag='#MongoLo')
        url = reverse('hashtags')
        response = self.client.delete(
            url
        )

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
