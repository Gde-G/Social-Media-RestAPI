import pdb
import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.test.test_setup import BaseApiTest
from users.models import Block
from .factories import PostFactory
from ..models import PollPost, OptionPollPost, VoteOptionPoll


class NoAuthVoteOptionPollTestCase(APITestCase, PostFactory):
    def test_fail_noauth_vote_option_in_poll(self):
        post = self.create_post()
        post.have_poll = True

        poll = PollPost.objects.create(
            post=post,
        )
        for _ in range(2):
            OptionPollPost.objects.create(
                poll=poll,
                option=self.option()
            )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthVoteOptionPollSuccessfulTestCase(BaseApiTest, PostFactory):
    def test_create_vote_option_in_own_poll_with_2_options(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True
        )
        poll = PollPost.objects.create(
            post=post
        )
        opt1 = OptionPollPost.objects.create(
            option='My option jeje.',
            poll=poll
        )
        OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt1.option
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        poll.refresh_from_db()
        opt1.refresh_from_db()

        self.assertEqual(opt1.votes, 1)
        self.assertEqual(poll.total_votes, 1)
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user).exists())
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user, option=opt1).exists())

    def test_create_vote_option_in_own_poll_with_3_options(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True
        )
        poll = PollPost.objects.create(
            post=post
        )
        for _ in range(2):
            OptionPollPost.objects.create(
                option=self.option(),
                poll=poll
            )

        opt3 = OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt3.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        poll.refresh_from_db()
        opt3.refresh_from_db()

        self.assertEqual(opt3.votes, 1)
        self.assertEqual(poll.total_votes, 1)
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user).exists())
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user, option=opt3).exists())

    def test_create_vote_option_in_own_poll_with_4_options(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True
        )
        poll = PollPost.objects.create(
            post=post
        )

        for _ in range(3):
            OptionPollPost.objects.create(
                option=self.option(),
                poll=poll
            )

        opt4 = OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt4.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        poll.refresh_from_db()

        opt4.refresh_from_db()

        self.assertEqual(opt4.votes, 1)
        self.assertEqual(poll.total_votes, 1)
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user).exists())
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user, option=opt4).exists())

    def test_create_vote_option_in_random_poll_with_2_options(self):
        post = self.create_post()
        post.have_poll = True
        post.save()
        poll = PollPost.objects.create(
            post=post
        )
        opt1 = OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )
        OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt1.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        poll.refresh_from_db()
        opt1.refresh_from_db()

        self.assertEqual(opt1.votes, 1)
        self.assertEqual(poll.total_votes, 1)
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user).exists())
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user, option=opt1).exists())

    def test_create_vote_option_in_random_poll_with_3_options(self):
        post = self.create_post()
        post.have_poll = True
        post.save()
        poll = PollPost.objects.create(
            post=post
        )

        for _ in range(2):
            OptionPollPost.objects.create(
                option=self.option(),
                poll=poll
            )

        opt3 = OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt3.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        poll.refresh_from_db()
        opt3.refresh_from_db()

        self.assertEqual(opt3.votes, 1)
        self.assertEqual(poll.total_votes, 1)
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user).exists())
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user, option=opt3).exists())

    def test_create_vote_option_in_random_poll_with_4_options(self):
        post = self.create_post()
        post.have_poll = True
        post.save()
        poll = PollPost.objects.create(
            post=post
        )
        for _ in range(3):
            OptionPollPost.objects.create(
                option=self.option(),
                poll=poll
            )

        opt4 = OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt4.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        poll.refresh_from_db()

        opt4.refresh_from_db()

        self.assertEqual(opt4.votes, 1)
        self.assertEqual(poll.total_votes, 1)
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user).exists())
        self.assertTrue(VoteOptionPoll.objects.filter(
            poll=poll, user=self.user, option=opt4).exists())


class AuthVoteOptionPollFailTestCase(BaseApiTest, PostFactory):
    def test_fail_create_vote_option_already_exists(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True
        )
        poll = PollPost.objects.create(
            post=post
        )
        opt1 = OptionPollPost.objects.create(
            poll=poll,
            option=self.option()
        )
        OptionPollPost.objects.create(
            poll=poll,
            option=self.option()
        )

        VoteOptionPoll.objects.create(
            user=self.user,
            poll=poll,
            option=opt1
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})

        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt1.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data['detail'][0], 'You have already voted on an option of this poll.')

    def test_fail_create_vote_option_expired_limit_time(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True
        )
        poll = PollPost.objects.create(
            post=post,
            end_time=timezone.now() - datetime.timedelta(hours=2)
        )
        opt1 = OptionPollPost.objects.create(
            poll=poll,
            option=self.option()
        )
        OptionPollPost.objects.create(
            poll=poll,
            option=self.option()
        )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})

        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt1.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['poll'][0], 'Voting for this poll has ended.')

    def test_fail_create_vote_option_poll_not_exists(self):
        post = self.create_post()

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': 23234,
                'option': 'ejjeje'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Post with poll not found.')

    def test_fail_create_vote_option_option_not_exists(self):
        post = self.create_post_kwargs(
            user=self.user,
            body=self.body(),
            have_poll=True
        )
        poll = PollPost.objects.create(
            post=post
        )

        for _ in range(3):
            OptionPollPost.objects.create(
                poll=poll,
                option=self.option()
            )

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': 'Non exists option.'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['option'], 'Option not found.')

    def test_fail_create_vote_option_auth_user_is_block(self):
        post, user = self.create_post_and_user()
        post.have_poll = True
        post.save()

        poll = PollPost.objects.create(
            post=post
        )
        for _ in range(3):
            OptionPollPost.objects.create(
                option=self.option(),
                poll=poll
            )
        opt4 = OptionPollPost.objects.create(
            option=self.option(),
            poll=poll
        )

        Block.objects.create(blocked_by=user, blocked_user=self.user)

        url = reverse('vote-poll-post', kwargs={'pk': post.id})
        response = self.client.post(
            url,
            {
                'poll': poll.id,
                'option': opt4.option
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'], 'You do not have permission to access this information.')

    def test_fail_get_vote_option_not_allow_method(self):
        url = reverse('vote-poll-post', kwargs={'pk': 34})
        response = self.client.get(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_fail_update_vote_option_not_allow_method(self):
        url = reverse('vote-poll-post', kwargs={'pk': 34})
        response = self.client.patch(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_fail_delete_vote_option_not_allow_method(self):
        url = reverse('vote-poll-post', kwargs={'pk': 34})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
