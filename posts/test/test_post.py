import pdb
import datetime

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.test.test_setup import BaseApiTest
from users.models import User, Follower
from .factories import PostFactory
from ..models import (
    Post, PostReply, Hashtag, HashtagsPost, UserMention,
    PollPost, OptionPollPost, Likes, Repost
)


class NoAuthPostTestCase(APITestCase, PostFactory):

    def test_fail_noauth_create_post(self):
        url = reverse('post-list')

        data = {
            'body': self.body(),
            'is_public': True,
        }

        response = self.client.post(
            url,
            data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_get_posts(self):
        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_get_post(self):
        url = reverse('post-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_noauth_update_post(self):
        url = reverse('post-detail', kwargs={'pk': 1})

        response = self.client.patch(
            url,
            data={'body': 'bag'}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthPostCreateSuccessfulTestCase(BaseApiTest, PostFactory):

    def test_create_post_necessary_field(self):
        url = reverse('post-list')

        data = {
            'body': self.body(),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_post_video(self):
        url = reverse('post-list')

        data = {
            'body': self.body(),
            'video': self.video()
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

        created_post = Post.objects.first()

        self.assertEqual(created_post.body, data['body'])
        self.assertIsNotNone(created_post.video)
        self.assertTrue(created_post.have_media)

    def test_create_post_img1(self):
        url = reverse('post-list')
        img1_data = self.image().file.getvalue()
        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')

        data = {
            'body': self.body(),
            'img1': img1_file
        }

        response = self.client.post(
            path=url,
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

        created_post = Post.objects.first()

        self.assertEqual(created_post.body, data['body'])
        self.assertIsNotNone(created_post.img1)
        self.assertTrue(created_post.have_media)

    def test_create_post_img1_to_img2(self):
        url = reverse('post-list')
        img1_data = self.image().file.getvalue()
        img2_data = self.image().file.getvalue()

        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')
        img2_file = SimpleUploadedFile(
            'img2.jpg', img2_data, content_type='image/jpeg')

        data = {
            'body': self.body(),
            'img1': img1_file,
            'img2': img2_file
        }

        response = self.client.post(
            path=url,
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

        created_post = Post.objects.first()

        self.assertEqual(created_post.body, data['body'])
        self.assertIsNotNone(created_post.img1)
        self.assertIsNotNone(created_post.img2)
        self.assertTrue(created_post.have_media)

    def test_create_post_img1_to_img3(self):
        url = reverse('post-list')
        img1_data = self.image().file.getvalue()
        img2_data = self.image().file.getvalue()
        img3_data = self.image().file.getvalue()

        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')
        img2_file = SimpleUploadedFile(
            'img2.jpg', img2_data, content_type='image/jpeg')
        img3_file = SimpleUploadedFile(
            'img3.jpg', img3_data, content_type='image/jpeg')

        data = {
            'body': self.body(),
            'img1': img1_file,
            'img2': img2_file,
            'img3': img3_file
        }

        response = self.client.post(
            path=url,
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

        created_post = Post.objects.first()

        self.assertEqual(created_post.body, data['body'])
        self.assertIsNotNone(created_post.img1)
        self.assertIsNotNone(created_post.img2)
        self.assertIsNotNone(created_post.img3)
        self.assertTrue(created_post.have_media)

    def test_create_post_img1_to_img4(self):
        url = reverse('post-list')
        img1_data = self.image().file.getvalue()
        img2_data = self.image().file.getvalue()
        img3_data = self.image().file.getvalue()
        img4_data = self.image().file.getvalue()

        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')
        img2_file = SimpleUploadedFile(
            'img2.jpg', img2_data, content_type='image/jpeg')
        img3_file = SimpleUploadedFile(
            'img3.jpg', img3_data, content_type='image/jpeg')
        img4_file = SimpleUploadedFile(
            'img4.jpg', img4_data, content_type='image/jpeg')

        data = {
            'body': self.body(),
            'img1': img1_file,
            'img2': img2_file,
            'img3': img3_file,
            'img4': img4_file
        }

        response = self.client.post(
            path=url,
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

        created_post = Post.objects.first()

        self.assertEqual(created_post.body, data['body'])
        self.assertIsNotNone(created_post.img1)
        self.assertIsNotNone(created_post.img2)
        self.assertIsNotNone(created_post.img3)
        self.assertIsNotNone(created_post.img4)
        self.assertTrue(created_post.have_media)

    def test_create_post_gif(self):
        url = reverse('post-list')
        gif = self.gif().file.getvalue()

        gif_file = SimpleUploadedFile(
            'gif.jpg', gif, content_type='image/gif')

        data = {
            'body': self.body(),
            'gif': gif_file
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

        created_post = Post.objects.first()

        self.assertEqual(created_post.body, data['body'])
        self.assertIsNotNone(created_post.gif)
        self.assertTrue(created_post.have_media)

    def test_create_post_with_quote(self):
        post = Post.objects.create(
            user=self.user,
            body=self.body()
        )

        url = reverse('post-list')

        response = self.client.post(
            url,
            data={
                'body': self.body(),
                'quote': post.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.get(id=post.id).num_repost > 0)
        self.assertEqual(Post.objects.count(), 2)

        post_quote = Post.objects.all().exclude(id=post.id).first()

        self.assertEqual(post_quote.quote, post)

    def test_create_post_with_parent(self):
        post = self.create_post()
        data = {
            'body': self.body(),
            'parent': post.id,
        }

        url = reverse('post-list')
        response = self.client.post(
            url,
            data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        child_post = Post.objects.all().exclude(id=post.id).first()

        self.assertTrue(PostReply.objects.filter(
            parent=post, reply=child_post).exists())

        self.assertEqual(Post.objects.get(id=post.id).num_replies, 1)

    def test_create_post_with_hashtag(self):
        url_post = reverse('post-list')

        data = {
            'body': self.body_with_hashtag(),
        }

        response_post = self.client.post(url_post, data)

        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)

        created_post = Post.objects.first()
        url_hashtag = reverse('hashtags')
        response_hashtag = self.client.post(
            url_hashtag,
            {'post': created_post.id}
        )

        self.assertEqual(response_hashtag.status_code, status.HTTP_201_CREATED)
        created_hashtag = Hashtag.objects.first()

        self.assertEqual(Hashtag.objects.count(), 1)
        self.assertTrue(HashtagsPost.objects.filter(
            hashtag=created_hashtag, post=created_post).exists())

    def test_create_post_with_mention(self):
        url_post = reverse('post-list')

        data = {
            'body': self.body_with_mention(),
        }

        response_post = self.client.post(url_post, data)

        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        created_post = Post.objects.first()

        url_mention = reverse('user-mention')
        response_mention = self.client.post(
            url_mention,
            {'post': created_post.id}
        )
        created_mention = User.objects.all().exclude(id=self.user.id).first()

        self.assertEqual(response_mention.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserMention.objects.count(), 1)
        self.assertTrue(UserMention.objects.filter(
            user=created_mention, post=created_post).exists())

    def test_create_post_with_poll_opt1_to_opt2(self):
        url = reverse('post-list')

        data = {
            'body': self.body(),
            'opt1': self.option(),
            'opt2': self.option(),

        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_post = Post.objects.first()
        created_poll = PollPost.objects.filter(post=created_post).first()

        self.assertTrue(created_poll)
        self.assertEqual(OptionPollPost.objects.filter(
            poll=created_poll).count(), 2)
        self.assertTrue(created_post.have_poll)

    def test_create_post_with_poll_opt1_to_opt3(self):
        url = reverse('post-list')

        data = {
            'body': self.body(),
            'opt1': self.option(),
            'opt2': self.option(),
            'opt3': self.option(),

        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_post = Post.objects.first()
        created_poll = PollPost.objects.filter(post=created_post).first()

        self.assertTrue(created_poll)
        self.assertEqual(OptionPollPost.objects.filter(
            poll=created_poll).count(), 3)
        self.assertTrue(created_post.have_poll)

    def test_create_post_with_poll_opt1_to_opt4(self):
        url = reverse('post-list')

        data = {
            'body': self.body(),
            'opt1': self.option(),
            'opt2': self.option(),
            'opt3': self.option(),
            'opt4': self.option(),
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_post = Post.objects.first()
        created_poll = PollPost.objects.filter(post=created_post).first()

        self.assertTrue(created_poll)
        self.assertEqual(OptionPollPost.objects.filter(
            poll=created_poll).count(), 4)
        self.assertTrue(created_post.have_poll)


class AuthPostCreateFailTestCase(BaseApiTest, PostFactory):
    def test_fail_create_post_no_parse_necessary_field(self):
        url = reverse('post-list')

        response = self.client.post(
            url,
            data={}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_create_post_body_empty_str(self):

        url = reverse('post-list')
        response = self.client.post(
            url,
            data={'body': ''}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Error on create post')
        self.assertIn('body', response.data['errors'])

    def test_fail_create_post_video_and_img(self):
        url = reverse('post-list')

        img1_data = self.image().file.getvalue()
        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')

        data = {
            'body': self.body(),
            'video': self.video(),
            'img1': img1_file
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('video' in response.data['errors'].keys())

    def test_fail_create_post_video_and_gif(self):
        url = reverse('post-list')

        gif_data = self.gif().file.getvalue()
        gif_file = SimpleUploadedFile(
            'gif1.gif', gif_data, content_type='image/gif')

        data = {
            'body': self.body(),
            'video': self.video(),
            'gif': gif_file
        }

        response = self.client.post(
            url,
            data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('video' in response.data['errors'].keys())

    def test_fail_create_post_gif_and_img(self):
        url = reverse('post-list')

        gif_data = self.gif().file.getvalue()
        img1_data = self.image().file.getvalue()
        gif_file = SimpleUploadedFile(
            'gif1.gif', gif_data, content_type='image/gif')
        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')

        data = {
            'body': self.body(),
            'gif': gif_file,
            'img1': img1_file
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('gif' in response.data['errors'].keys())

    def test_fail_create_post_poll_and_img(self):
        url = reverse('post-list')

        img1_data = self.image().file.getvalue()
        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')

        data = {
            'body': self.body(),
            'img1': img1_file,
            'opt1': self.option(),
            'opt2': self.option()
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('poll' in response.data['errors'].keys())

    def test_fail_create_post_poll_and_gif(self):
        url = reverse('post-list')

        gif_data = self.gif().file.getvalue()
        gif_file = SimpleUploadedFile(
            'img1.gif', gif_data, content_type='image/gif')

        data = {
            'body': self.body(),
            'gif': gif_file,
            'opt1': self.option(),
            'opt2': self.option()
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('poll' in response.data['errors'].keys())

    def test_fail_create_post_poll_and_video(self):
        url = reverse('post-list')

        data = {
            'body': self.body(),
            'video': self.video(),
            'opt1': self.option(),
            'opt2': self.option()
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('poll' in response.data['errors'].keys())

    def test_fail_create_post_quote_not_exist(self):

        url = reverse('post-list')

        response = self.client.post(
            url,
            data={
                'body': self.body(),
                'quote': 2342
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('quote' in response.data['errors'].keys())


class AuthPostListTestCase(BaseApiTest, PostFactory):

    def test_list_posts_no_follows(self):
        post = self.create_post()

        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] == 1)

    def test_list_posts_with_follows(self):
        post, user = self.create_post_and_user()

        Follower.objects.create(follower=self.user, following=user)

        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] == 1)
        self.assertEqual(
            response.data['results'][0]['user']['user_handle'], user.user_handle
        )

    def test_list_posts_and_likes(self):
        post, user = self.create_post_and_user()
        post1, user1 = self.create_post_and_user()

        Follower.objects.create(follower=self.user, following=user)
        Likes.objects.create(post=post1, user=user)

        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] == 2)

        self.assertEqual(
            response.data['results'][0]['user']['user_handle'], user.user_handle
        )
        self.assertTrue(
            'liked_by' in response.data['results'][1].keys()
        )

    def test_list_posts_and_repost(self):
        post, user = self.create_post_and_user()
        post1, user1 = self.create_post_and_user()

        Follower.objects.create(follower=self.user, following=user)
        Repost.objects.create(post=post1, user=user)

        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] == 2)

        self.assertEqual(
            response.data['results'][0]['user']['user_handle'], user.user_handle
        )
        self.assertTrue(
            'repost_by' in response.data['results'][1].keys()
        )

    def test_list_posts_likes_and_repost(self):
        post, user = self.create_post_and_user()
        post1 = self.create_post()
        post2 = self.create_post()

        Follower.objects.create(follower=self.user, following=user)
        Repost.objects.create(post=post1, user=user)
        Likes.objects.create(post=post2, user=user)

        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] == 3)

        self.assertEqual(
            response.data['results'][0]['user']['user_handle'], user.user_handle
        )
        self.assertTrue(
            'liked_by' in response.data['results'][1].keys()
        )
        self.assertTrue(
            'repost_by' in response.data['results'][2].keys()
        )

    def test_list_posts_likes_repost_and_others(self):
        post, user = self.create_post_and_user()
        post1 = self.create_post()
        post2 = self.create_post()
        post4 = self.create_post()

        Follower.objects.create(follower=self.user, following=user)
        Repost.objects.create(post=post1, user=user)
        Likes.objects.create(post=post2, user=user)

        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data['count'] == 4)

        self.assertEqual(
            response.data['results'][0]['user']['user_handle'], user.user_handle
        )
        self.assertTrue(
            'liked_by' in response.data['results'][1].keys()
        )
        self.assertTrue(
            'repost_by' in response.data['results'][2].keys()
        )

    def test_list_posts_paginator(self):

        posts = [Post.objects.create(
            user=self.user, body=self.body()) for _ in range(1, 21)]

        url = reverse('post-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['count'], len(posts))

        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

        if 'next' in response.data.keys():
            second_page_url = f"{url}?page=2"
            second_page_response = self.client.get(second_page_url)

            self.assertEqual(second_page_response.status_code,
                             status.HTTP_200_OK)

    def test_list_posts_that_have_hashtags(self):
        posts = [self.create_post_kwargs(
            user=self.user, body=self.body_with_hashtag()) for _ in range(5)]
        url_hashtags = reverse('hashtags')
        for post in posts:
            response = self.client.post(
                url_hashtags,
                {'post': post.id}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url_post = reverse('post-list')
        response_post = self.client.get(url_post)

        self.assertEqual(response_post.status_code, status.HTTP_200_OK)

        self.assertTrue(response_post.data['count'] == 5)
        self.assertIn('hashtags', response_post.data['results'][0])

    def test_list_posts_that_have_mentions(self):
        posts = [self.create_post_kwargs(
            user=self.user, body=self.body_with_mention()) for _ in range(5)]
        url_mention = reverse('user-mention')
        for post in posts:
            response = self.client.post(
                url_mention,
                {'post': post.id}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url_post = reverse('post-list')
        response_post = self.client.get(url_post)

        self.assertEqual(response_post.status_code, status.HTTP_200_OK)
        self.assertTrue(response_post.data['count'] == 5)
        self.assertIn('users-mention', response_post.data['results'][0])

    def test_list_posts_date_to_publish(self):
        post_published = self.create_post()
        post_not_published = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            date_to_publish=timezone.now() + datetime.timedelta(days=2)
        )

        url = reverse('post-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], post_published.id)


class AuthPostRetrieveSuccessfulTestCase(BaseApiTest, PostFactory):

    def test_retrieve_post(self):
        post = self.create_post()

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('post', response.data.keys())
        self.assertEqual(response.data['post']['id'], post.id)

    def test_retrieve_post_with_video(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_media=True,
            video=self.video()
        )

        url = reverse('post-detail', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('video', response.data['post']['media'])

    def test_retrieve_post_with_img1(self):
        img1_data = self.image().file.getvalue()
        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_media=True,
            img1=img1_file
        )

        url = reverse('post-detail', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('img1', response.data['post']['media'])

    def test_retrieve_post_with_img1_to_img2(self):
        img1_data = self.image().file.getvalue()
        img2_data = self.image().file.getvalue()
        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')
        img2_file = SimpleUploadedFile(
            'img2.jpg', img2_data, content_type='image/jpeg')
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_media=True,
            img1=img1_file,
            img2=img2_file
        )

        url = reverse('post-detail', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('img1', response.data['post']['media'])
        self.assertIn('img2', response.data['post']['media'])

    def test_retrieve_post_with_img1_to_img3(self):
        img1_data = self.image().file.getvalue()
        img2_data = self.image().file.getvalue()
        img3_data = self.image().file.getvalue()
        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')
        img2_file = SimpleUploadedFile(
            'img2.jpg', img2_data, content_type='image/jpeg')
        img3_file = SimpleUploadedFile(
            'img3.jpg', img3_data, content_type='image/jpeg')
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_media=True,
            img1=img1_file,
            img2=img2_file,
            img3=img3_file
        )

        url = reverse('post-detail', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('img1', response.data['post']['media'])
        self.assertIn('img2', response.data['post']['media'])
        self.assertIn('img3', response.data['post']['media'])

    def test_retrieve_post_with_img1_to_img4(self):
        img1_data = self.image().file.getvalue()
        img2_data = self.image().file.getvalue()
        img3_data = self.image().file.getvalue()
        img4_data = self.image().file.getvalue()

        img1_file = SimpleUploadedFile(
            'img1.jpg', img1_data, content_type='image/jpeg')
        img2_file = SimpleUploadedFile(
            'img2.jpg', img2_data, content_type='image/jpeg')
        img3_file = SimpleUploadedFile(
            'img3.jpg', img3_data, content_type='image/jpeg')
        img4_file = SimpleUploadedFile(
            'img4.jpg', img4_data, content_type='image/jpeg')

        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_media=True,
            img1=img1_file,
            img2=img2_file,
            img3=img3_file,
            img4=img4_file,
        )

        url = reverse('post-detail', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('img1', response.data['post']['media'])
        self.assertIn('img2', response.data['post']['media'])
        self.assertIn('img3', response.data['post']['media'])
        self.assertIn('img4', response.data['post']['media'])

    def test_retrieve_post_with_gif(self):
        gif = self.gif().file.getvalue()

        gif_file = SimpleUploadedFile(
            'gif.jpg', gif, content_type='image/gif')

        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_media=True,
            gif=gif_file
        )

        url = reverse('post-detail', kwargs={'pk': post.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('gif', response.data['post']['media'])

    def test_retrieve_post_with_quote(self):
        post = self.create_post()
        quote = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            quote=post
        )

        url = reverse('post-detail', kwargs={'pk': quote.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('body', response.data['post']['quote'])

    def test_retrieve_post_with_replies(self):
        reply = self.create_post()
        parent = self.create_post()

        post_reply = PostReply.objects.create(
            reply=reply,
            parent=parent
        )

        url = reverse('post-detail', kwargs={'pk': parent.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(len(response.data['replies']) == 0)

    def test_retrieve_post_with_poll_opt1_to_opt2(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True,
        )
        poll = PollPost.objects.create(
            post=post
        )
        for _ in range(2):
            OptionPollPost.objects.create(
                poll=poll,
                option=self.option()
            )
        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('poll', response.data['post'])
        self.assertIn('option1', response.data['post']['poll'])
        self.assertIn('option2', response.data['post']['poll'])

    def test_retrieve_post_with_poll_opt1_to_opt3(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True,
        )
        poll = PollPost.objects.create(
            post=post
        )
        for _ in range(3):
            OptionPollPost.objects.create(
                poll=poll,
                option=self.option()
            )

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('poll', response.data['post'])
        self.assertIn('option1', response.data['post']['poll'])
        self.assertIn('option2', response.data['post']['poll'])
        self.assertIn('option3', response.data['post']['poll'])

    def test_retrieve_post_with_poll_opt1_to_opt4(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True,
        )
        poll = PollPost.objects.create(
            post=post
        )
        for _ in range(4):
            OptionPollPost.objects.create(
                poll=poll,
                option=self.option()
            )

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('poll', response.data['post'])
        self.assertIn('option1', response.data['post']['poll'])
        self.assertIn('option2', response.data['post']['poll'])
        self.assertIn('option3', response.data['post']['poll'])
        self.assertIn('option4', response.data['post']['poll'])


class AuthPostDeleteSuccessfulTestCase(BaseApiTest, PostFactory):
    def test_delete_post(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body()
        )

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_delete_post_and_replies(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            num_replies=2
        )
        reply1 = self.create_post()
        reply2 = self.create_post()

        PostReply.objects.create(parent=post, reply=reply1)
        PostReply.objects.create(parent=post, reply=reply2)

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())
        self.assertFalse(PostReply.objects.filter(parent=post).exists())

    def test_delete_post_that_was_quoted(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            num_repost=1
        )

        quote = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            quote=post,
        )

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())
        self.assertIsNone(Post.objects.filter(id=quote.id).first().quote)

    def test_delete_post_with_poll(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True
        )
        poll = PollPost.objects.create(
            post=post,
        )
        for _ in range(2):
            OptionPollPost.objects.create(
                poll=poll,
                option=self.option()
            )

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PollPost.objects.filter(post=post).exists())
        self.assertFalse(OptionPollPost.objects.filter(poll=poll).exists())


class AuthPostDeleteFailTestCase(BaseApiTest, PostFactory):
    def test_fail_delete_post_other_owner(self):
        post = self.create_post()

        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fail_delete_post_not_exist(self):
        url = reverse('post-detail', kwargs={'pk': 56465})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
