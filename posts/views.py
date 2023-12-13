import re

from django.db.models import Q, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, OpenApiParameter

from users.models import User, Follower, Block
from core.utils import GenericPagination
from .serializers import (CreatePostSerializer, ListPostSerializer,
                          ListPostRepliesSerializer, ListSimpleUserSerializer,
                          ListRepostPostSerializer, ListLikedPostSerializer, ListHashtagsSerializer,
                          CreateVoteOptionPollSerializer, ListNotificationsSerializer, DummySerializer)
from .models import (Post, PostReply, UserMention, Hashtag, HashtagsPost, Likes,
                     Repost, Notification)
from .utils import is_request_user_blocked


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = CreatePostSerializer
    permission_classes = [IsAuthenticated,]
    pagination_class = PostPagination

    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostSerializer
        elif self.action == 'list':
            return ListPostSerializer, ListLikedPostSerializer, ListRepostPostSerializer
        elif self.action == 'retrieve':
            return ListPostRepliesSerializer

        return super().get_serializer_class()

    def get_queryset(self, lookup=None, search=None, **kwargs):
        blockeds = Block.objects.select_related(
            'blocked_user').filter(blocked_by=self.request.user)

        if search:
            posts = Post.objects.filter(
                Q(body__icontains=search) &
                ~Q(user__in=[blocked.blocked_user for blocked in blockeds])
            )

            return posts

        users = Follower.objects.select_related(
            'following').filter(follower=self.request.user)
        users = [user.following for user in users]

        if lookup == None and (users == None or users == []):
            posts = Post.objects.filter(
                Q(date_to_publish__lte=timezone.now())).order_by('?')

            return posts

        elif lookup == None and users != []:

            posts = Post.objects.filter(
                Q(user__in=users) &
                Q(date_to_publish__lte=timezone.now()
                  )).order_by('-date_to_publish')
            liked_posts = Likes.objects.select_related('post').filter(
                Q(user__in=users) & ~Q(post__in=posts) &
                Q(post__date_to_publish__lte=timezone.now()))

            reposted_posts = Repost.objects.select_related('post').filter(
                Q(user__in=users) & ~Q(post__in=posts) &
                ~Q(post__in=liked_posts.values('post')) &
                Q(post__date_to_publish__lte=timezone.now()))

            others = Post.objects.filter(
                ~Q(id__in=posts) &
                ~Q(id__in=liked_posts.values('post')) &
                ~Q(id__in=reposted_posts.values('post')) &
                ~Q(user__in=[blocked.blocked_user for blocked in blockeds]) &
                Q(date_to_publish__lte=timezone.now())
            ).annotate(max_views=Max('num_views'))

            return {
                'posts': posts,
                'liked_posts': liked_posts,
                'reposted_posts': reposted_posts,
                'others': others
            }

        elif lookup != None:
            post = get_object_or_404(
                Post, id=lookup, date_to_publish__lte=timezone.now())
            replies = PostReply.objects.select_related(
                'reply').filter(parent=post)
            return post, replies

        else:
            return None

    def _posts_add_view(self, posts_ids=None):

        posts = Post.objects.filter(id__in=posts_ids)
        for post in posts:
            post.num_views += 1
            post.save()

    @extend_schema(
        responses={200: DummySerializer},
        parameters=[
            OpenApiParameter(
                name='search', description='Filtering by body content.', type=str),
            OpenApiParameter(
                name='page', description='Page number.', type=int),
            OpenApiParameter(
                name='page_size', description='Amount of results per page.', type=int),
        ],
    )
    def list(self, request: Request, *args, **kwargs):
        """
        List posts.\n

        ### URL Parameters :\n
        - `search` (str): To find posts that contains in his body the "value".\n
        - `page` (int): Page to get.\n
        - `page_size` (int): Amount of posts to get.\n

        ### Response (Success):\n
        - `200 OK`:\n

        - #### Post Object:\n
            - `id` (int): Unique identifier for the post.\n
            - `body` (str): Content of the post.\n
            - `date_to_publish` (str): Date and time when the post is scheduled to be published.\n
            - `num_replies` (int): Number of replies to the post.\n
            - `num_repost` (int): Number of times the post has been reposted.\n
            - `num_likes` (int): Number of likes on the post.\n
            - `num_views` (int): Number of views on the post.\n
            - `user` (object): User who created the post.\n
                - `user_handle` (str): User handle.\n
                - `username` (str): Username.\n
                - `profile_image` (str): URL of the user's profile image.\n
                - `biography` (str): Profile Biography.\n
                - `follower_amount` (int): Number of followers for the user.\n
                - `following_amount` (int): Number of users the user is following.\n
            - `hashtags` (list, optional): List of hashtags.\n
                - `tag` (str): Hashtag.\n
                - `amount_use` (int): Number of times the hashtag is used.\n
            - `users-mention` (list, optional): \n
                - List of mentioned users, each have the same structure of user. \n
            - `media` (object, optional): Media attachments to the post, one of the three options.\n
                - `video` (str, optional): URL of the video attachment, if present.\n
                - `img1`, `img2`, `img3`, `img4` (str, optional): URLs of image attachments, if present.\n
                - `gif` (str, optional): URL of the gif attachment, if present.\n
            - `poll` (object, optional): Poll information if the post includes a poll.\n
                - `id` (int): Unique identifier for the poll.\n
                - `total_votes` (int): Total number of votes in the poll.\n
                - `end_time` (str): Date and time when the poll ends.\n
                - `option1` to `option4` (object): Information about each poll option.\n
                    - `option` (str): Text of the poll option.\n
                    - `votes` (int): Number of votes for the option.\n
            - `quote` (object, optional): Information about the quoted post.\n\n
        - #### Liked Post Objects:\n
            - `liked_by` (object): User who liked or reposted the post.\n
                - Fields are the same as the user object.\n
            - `post` (object): Information about the liked or reposted post.\n
                - Fields are the same as the main post object.\n\n
        - #### Repost Post Objects:\n
            - `repost_by` (object): User who liked or reposted the post.\n
                - Fields are the same as the user object.\n
            - `post` (object): Information about the liked or reposted post.\n
                - Fields are the same as the main post object.\n\n

        ### Response (Failure):\n
        - `400 Bad Request`:
        If the request is invalid.\n
        - `401 Unauthorized`: 
        If the user is not authenticated.\n

        """
        lookup_search = self.request.GET.get('search', None)

        if lookup_search:
            posts = self.get_queryset(search=lookup_search)
            if not posts.exists():
                return Response(
                    {'detail': f'Not found post that contains {lookup_search}.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            posts_serializer = ListPostSerializer(posts, many=True)
            serialized_data = posts_serializer.data

        else:
            rest_query = self.get_queryset()

            posts_serializer, liked_serializer, repost_serializer = self.get_serializer_class()
            if type(rest_query) == dict:

                posts,  liked, repost, other = rest_query['posts'], rest_query[
                    'liked_posts'], rest_query['reposted_posts'], rest_query['others']

                posts_serializer_data = posts_serializer(posts, many=True)
                liked_serializer_data = liked_serializer(liked, many=True)
                repost_serializer_data = repost_serializer(repost, many=True)
                other_posts_serializer_data = posts_serializer(
                    other, many=True)

                serialized_data = posts_serializer_data.data + \
                    liked_serializer_data.data + repost_serializer_data.data

                serialized_data += other_posts_serializer_data.data
            else:
                posts_serializer_data = posts_serializer(rest_query, many=True)
                serialized_data = posts_serializer_data.data

        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(
            serialized_data, request, view=self)

        posts_to_increment_views = set()
        for item in paginated_data:
            if 'id' in item:
                posts_to_increment_views.add(item['id'])
            elif 'post' in item and 'id' in item['post']:
                posts_to_increment_views.add(item['post']['id'])

        self._posts_add_view(posts_to_increment_views)

        return paginator.get_paginated_response(paginated_data)

    @extend_schema(
        request=CreatePostSerializer,
    )
    def create(self, request: Request, *args, **kwargs):
        """
        Create a new post.\n
        - `Note:` Media files are only support one type per post. I.e. video only, imgs only or gif only.\n
        ### Request:\n
        - `user` (int, required): ID of the user creating the post.\n
        - `body` (str, required): Content of the post.\n
        - `video` (file, optional): Video file attachment.\n
        - `img1`, `img2`, `img3`, `img4` (image file, optional): Image file attachments.\n
            - To have a successful attach have to be in order. e.g. `img2` must be null if `img1` is null.\n
        - `gif` (image file, optional): GIF file attachment.\n
        - `date_to_publish` (str, optional): Date and time when the post is scheduled to be published.\n
        - `quote` (int, optional): ID of the post being quoted.\n
        - `parent` (int, optional): ID of the parent post if this is a reply.\n
        - `opt1`, `opt2`, `opt3`, `opt4` (str, optional): Poll options if the post includes a poll.\n
            - If you want to have a poll `opt1` and `opt2` must not be null.\n
        - `end_time` (str, optional): Date and time when the poll ends.\n\n

        ### Response (Success):\n
        - `201 Created`:
        Post created successfully.\n\n

        ### Response (Failure):\n
        - `400 Bad Request`:
        Error on creating the post.\n
        - `401 Unauthorized`:
        If the user is not authenticated.\n
        """
        data = request.data.copy()

        data['user'] = request.user

        post_serializer = self.get_serializer_class()(data=data)

        if post_serializer.is_valid():
            try:
                quote_post = post_serializer.validated_data['quote']
                quote_post.num_repost += 1
                quote_post.save()
            except:
                quote_post = None

            validated_keys = post_serializer.validated_data.keys()
            if 'video' in validated_keys or 'img1' in validated_keys or 'gif' in validated_keys:
                post = post_serializer.save(have_media=True)
            else:
                post = post_serializer.save()
                if quote_post:
                    Notification.objects.create(
                        sender=post.user,
                        recipient=quote_post.user,
                        notification_type='quote',
                        post=post,
                        header=f'{post.user} quote your post.',
                        message=post.body,
                    )

            return Response(
                {
                    'detail': 'Post created successfully.',
                },
                status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Error on create post',
                    'errors': post_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request: Request, pk=None, *args, **kwargs):
        """
        Retrieve details of a specific post with its replies.

        ### Path Parameter:
        - `id` (int): ID of the post that want to get.

        ### Response (Success):
        - `200 OK`:
        - `post` (object):
            - `id` (int): ID of the post.
            - `body` (str): Content of the post.
            - `user` (object): User who created the post.\n
                - `user_handle` (str): User handle.\n
                - `username` (str): Username.\n
                - `profile_image` (str): URL of the user's profile image.\n
                - `biography` (str): Profile Biography.\n
                - `follower_amount` (int): Number of followers for the user.\n
                - `following_amount` (int): Number of users the user is following.\n
            - `media` (object, optional): Media attachments.\n
                - `img1`, `img2`, `img3`, `img4` (str, optional): URLs of image file attachments.\n
                - `video` (str, optional): URL of the video file attachment.\n
                - `gif` (str, optional): URL of the GIF file attachment.\n
            - `hashtags` (list, optional): List of hashtags.\n
                - `tag` (str): Hashtag.\n
                - `amount_use` (int): Number of times the hashtag is used.\n
            - `users-mention` (list, optional): \n
                - List of mentioned users, (Each have same structure as `user` object). \n
            - `date_to_publish` (str, optional): Date and time when the post is scheduled to be published.\n
            - `num_replies` (int): Number of replies to the post.\n
            - `num_repost` (int): Number of times the post has been reposted.\n
            - `num_likes` (int): Number of likes on the post.\n
            - `num_views` (int): Number of views on the post.\n
            - `quote` (object, optional): Details of the quoted post.\n
                - (Same structure as `post` object)\n

            - `replies` (list, optional): List of replies to the post.\n
                - (Same structure as `post` object)\n

        ### Response (Failure):\n
        - `401 Unauthorized`:
        Not authenticated user.\n
        - `403 FORBIDDEN`:
        If the requesting user is blocked from accessing the post.\n
        - `404 Not Found`:
        Post not found.\n

        """
        try:

            post, replies = self.get_queryset(lookup=pk)
            blocked = is_request_user_blocked(
                post=post, request_user=request.user)
            if blocked:
                return Response({'detail': 'You do not have permission to access this information.'}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = self.get_serializer_class()(
                {'post': post, 'replies': [reply.reply for reply in replies]})
            post_ids = set()
            post_ids.add(post.id)

            self._posts_add_view(post_ids)
            return Response(serializer.data)

        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(request=DummySerializer, responses={405: DummySerializer})
    def update(self, request: Request, pk=None, *args, **kwargs):
        """ 
        ### Response: \n
        -`405  Method not allowed` : This action can be execute.
        """
        return Response({'detail': 'Method not allow.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(request=DummySerializer, responses={405: DummySerializer})
    def partial_update(self, request, *args, **kwargs):
        """ 
        ### Response: \n
        -`405  Method not allowed` : This action can be execute.
        """
        return Response({'detail': 'Method not allow.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(responses={204: DummySerializer})
    def destroy(self, request: Request, pk=None, *args, **kwargs):
        """
        Delete a specific post.\n

        Only the owner of the post can delete it.\n

        ### Path Parameter:\n
        - `id` (int): ID of the post that want to get.\n

        ### Response (Success):\n
        - `204 No Content`:
        Post successfully deleted.\n\n

        ### Response (Failure):\n
        - `401 Unauthorized`:
        Not authenticated user.\n
        - `403 FORBIDDEN`: 
        If the requesting user is not the owner of the post.\n
        - `404 Not Found`: 
        If the post does not exist.\n

        """
        post, replies = self.get_queryset(lookup=pk)

        if request.user == post.user:
            parents = PostReply.objects.select_related(
                'parent').filter(reply=post)
            if parents.exists():
                parents[0].parent.num_replies -= 1
                parents[0].parent.save()

            post.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Unauthorize to perform this action'}, status=status.HTTP_403_FORBIDDEN)


class LikePostAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated,]
    serializer_class = DummySerializer

    @extend_schema(responses={200: ListSimpleUserSerializer(many=True)})
    def get(self, request: Request, pk=None, *args, **kwargs):
        '''
        Retrieve the list of users who liked a specific post.

        ### Path Parameter:
        - `id` (int): ID of the post that want to get the likes.

        ### Response (Success):
        - `200 OK` :
        List of user objects that like the post.\n
            - `user_handle` (str): User handle.\n
            - `username` (str): Username.\n
            - `profile_img` (str): URL to the user's profile image.\n
            - `biography` (str): Profile Biography.\n
            - `follower_amount` (int): Number of followers for the user.\n
            - `following_amount` (int): Number of users the user is following.\n\n

        - `200 OK` (No Likes):\n
            - An empty response is returned if no users have liked the post.\n\n

        ### Response (Failure):\n
        - `401 Unauthorized`:
        Not authenticated user.\n
        - `403 FORBIDDEN`:
        If the requesting user is blocked from accessing the post.\n
        - `404 Not Found`:
        Post not found.\n
        '''
        try:
            Post.objects.get(id=int(pk))
            blocked = is_request_user_blocked(
                post_pk=pk, request_user=request.user)
            if blocked:
                return Response({'detail': 'You do not have permission to access this information.'}, status=status.HTTP_403_FORBIDDEN)

            likes = Likes.objects.select_related(
                'user').filter(post=pk)
            if len(likes) != 0:
                posts_serializer = ListSimpleUserSerializer(
                    [like.user for like in likes], many=True)
                return Response(posts_serializer.data, status=status.HTTP_200_OK)
            return Response({}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'detail': f'Post {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'Internal Error Server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request, pk=None, *args, **kwargs):
        '''
        Like a specific post.\n

        ### Path Parameter:\n
        - `id` (int): ID of the post that want like.\n\n

        ### Response (Success):\n
        - `201 Created`:
        Post successfully liked.\n\n

        ### Response (Failure):\n
        - `400 Bad Request`:
        If the user has already liked the post.\n
        - `401 Unauthenticated`:
        Not authenticated user.\n
        - `403 Forbidden`:
        If the requesting user is blocked from accessing the post.\n
        - `404 Not Found`:
        Post not found.\n
        '''
        try:

            post = Post.objects.select_related('user').get(id=int(pk))
            blocked = is_request_user_blocked(
                post=post, request_user=request.user)
            if blocked:
                return Response({'detail': 'You do not have permission to access this information.'}, status=status.HTTP_403_FORBIDDEN)

            like, create = Likes.objects.get_or_create(
                user=request.user, post=post)

            if not create:
                return Response({"detail": "You've already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
            post.num_likes += 1
            post.save()

            if request.user != post.user:
                Notification.objects.create(
                    sender=request.user,
                    recipient=post.user,
                    notification_type='like',
                    post=post,
                    header=f'{request.user} like your post.',
                    message=post.body,
                )

            return Response({"detail": "Post liked."}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'detail': "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, pk=None, *args, **kwargs):
        '''
        Remove like from a specific post.\n

        ### Path Parameter:\n
        - `id` (int): ID of the post that want to remove your like.\n\n

        ### Response (Success):\n
        - `204 No Content`:
        Like successfully removed from the post.\n\n

        ### Response (Failure):\n
        - `401 Unauthenticated`:
        Not authenticated user.\n
        - `403 Forbidden`:
        If the requesting user is blocked from accessing the post.\n
        - `404 Not Found`:
        If the post is not found or user has not liked the post.\n

        '''
        try:
            post = Post.objects.get(id=int(pk))
            like = Likes.objects.get(user=request.user, post=post)

            like.delete()

            post.num_likes -= 1
            post.save()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Likes.DoesNotExist:
            return Response({"detail": "You have not liked this post."}, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'Internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RepostAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = DummySerializer

    @extend_schema(responses={200: ListSimpleUserSerializer(many=True)})
    def get(self, request: Request, pk=None, *args, **kwargs):
        '''
        Retrieve the list of users who repost a specific post.

        ### Path Parameter:
        - `id` (int): ID of the post that want to get the reposts.

        ### Response (Success):
        - `200 OK` :
        List of user objects that repost the post.\n
            - `user_handle` (str): User handle.\n
            - `username` (str): Username.\n
            - `profile_img` (str): URL to the user's profile image.\n
            - `biography` (str): Profile Biography.\n
            - `follower_amount` (int): Number of followers for the user.\n
            - `following_amount` (int): Number of users the user is following.\n\n

        - `200 OK` (No Reposts):\n
            - An empty response is returned if no users have reposted the post.\n\n

        ### Response (Failure):\n
        - `401 Unauthorized`:
        Not authenticated user.\n
        - `403 FORBIDDEN`:
        If the requesting user is blocked from accessing the post.\n
        - `404 Not Found`:
        Post not found.\n
        '''

        try:
            Post.objects.get(id=int(pk))
            blocked = is_request_user_blocked(
                post_pk=pk, request_user=request.user)
            if blocked:
                return Response({'detail': 'You do not have permission to access this information.'}, status=status.HTTP_403_FORBIDDEN)

            reposts = Repost.objects.select_related(
                'user').filter(post=pk)
            if len(reposts) != 0:
                posts_serializer = ListSimpleUserSerializer(
                    [repost.user for repost in reposts], many=True)
                return Response(posts_serializer.data, status=status.HTTP_200_OK)
            return Response({}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'detail': "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'Internal Error Server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request, pk=None, *args, **kwargs):
        '''
        Repost a specific post.\n

        ### Path Parameter:\n
        - `id` (int): ID of the post that want to reposts.\n\n

        ### Response (Success):\n
        - `201 Created`:
        Post successfully reposted.\n\n

        ### Response (Failure):\n
        - `400 Bad Request`:
        If the user has already repost this post.\n
        - `401 Unauthenticated`:
        Not authenticated user.\n
        - `403 Forbidden`:
        If the requesting user is blocked from accessing the post.\n
        - `404 Not Found`:
        Post not found.\n
        '''
        try:
            post = Post.objects.select_related('user').get(id=int(pk))
            blocked = is_request_user_blocked(
                post=post, request_user=request.user)
            if blocked:
                return Response({'detail': 'You do not have permission to access this information.'}, status=status.HTTP_401_UNAUTHORIZED)

            repost, create = Repost.objects.get_or_create(
                user=request.user, post=post)

            if not create:
                return Response({"detail": "You've already repost this post."}, status=status.HTTP_400_BAD_REQUEST)
            post.num_repost += 1
            post.save()
            if request.user != post.user:
                Notification.objects.create(
                    sender=request.user,
                    recipient=post.user,
                    notification_type='repost',
                    post=post,
                    header=f'{post.user} repost your post.',
                    message=post.body,
                )
            return Response({"detail": "Post reposted."}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'detail': "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, pk=None, *args, **kwargs):
        '''
        Remove repost from a specific post.\n

        ### Path Parameter:\n
        - `id` (int): ID of the post that want to your repost.\n\n

        ### Response (Success):\n
        - `204 No Content`:
        Repost successfully removed from the post.\n\n

        ### Response (Failure):\n
        - `401 Unauthenticated`:
        Not authenticated user.\n
        - `403 Forbidden`:
        If the requesting user is blocked from accessing the post.\n
        - `404 Not Found`:
        If the post is not found or user has not reposted the post.\n

        '''
        try:
            post = Post.objects.get(id=int(pk))
            repost = Repost.objects.get(user=request.user, post=post)

            repost.delete()
            post.num_repost -= 1
            post.save()

            return Response({"detail": "Post repost undid."}, status=status.HTTP_204_NO_CONTENT)

        except Repost.DoesNotExist:
            return Response({"detail": "You have not repost this post."}, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'Internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HashtagAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = DummySerializer
    pagination_class = GenericPagination
    lookup_field = 'tag'

    def get_queryset(self, lookup=None):
        if lookup == None:
            hashtags = Hashtag.objects.all().order_by('-amount_use')
        else:
            hashtags = Hashtag.objects.filter(
                tag__icontains=lookup).order_by('-amount_use')

        return hashtags

    @extend_schema(
        responses={200: ListHashtagsSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='search', description='Tag to filter.', type=str),
            OpenApiParameter(
                name='page', description='Page number.', type=int),
            OpenApiParameter(
                name='page_size', description='Amount of hashtags per page.', type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        lookup_tag = self.request.GET.get('search', None)
        queryset = self.get_queryset(lookup=lookup_tag)

        if not queryset.exists():
            return Response({'detail': 'No matching hashtags found.'}, status=status.HTTP_404_NOT_FOUND)

        hashtags_serializer = ListHashtagsSerializer(queryset, many=True)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(
            hashtags_serializer.data, request, view=self)

        return paginator.get_paginated_response(paginated_data)

    def post(self, request, *args, **kwargs):
        '''
        Create hashtags from a post's body.\n

        ### Request:\n
        - `post` (int, required): ID of the post to extract hashtags from.\n\n

        ### Response (Success):\n
        - `200 OK`:
        Body of post examined successfully, and no hashtags were found.\n
        - `201 Created`:
        Hashtags created successfully.\n\n

        ### Response (Failure):\n
        - `400 Bad Request`:
        If the required field `post` is not provided.\n
        - `401 Unauthorized`:
        Not authenticated user.\n
        - `404 Not Found`:
        Post with that ID not found.\n

        '''
        if 'post' in request.data.keys():
            post = get_object_or_404(Post, id=request.data['post'])

            hashtags = re.findall(r'#\w+', post.body)
            processed_hashtags = False

            for word in hashtags:
                try:
                    hashtag, create = Hashtag.objects.get_or_create(
                        tag=word.lower())
                    if not create:
                        hashtag.amount_use += 1
                        hashtag.save()
                    HashtagsPost.objects.create(hashtag=hashtag, post=post)
                    processed_hashtags = True
                except:
                    continue

            if processed_hashtags:
                return Response({'detail': 'Hashtag/s created successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Body of post examined successfully and not found any hashtags.'}, status=status.HTTP_200_OK)
        else:
            return Response({'post': 'This field required.'}, status=status.HTTP_400_BAD_REQUEST)


class UserMentionAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = DummySerializer

    def post(self, request, *args, **kwargs):
        '''
        Create Mentions of users from a post's body.\n

        ### Request:\n
        - `post` (int, required): ID of the post to extract mentions from.\n\n

        ### Response (Success):\n
        - `200 OK`:
        Body of post examined successfully, and no mentions were found.\n
        - `201 Created`:
        Mentions created successfully.\n\n

        ### Response (Failure):\n
        - `400 Bad Request`:
        If the required field `post` is not provided.\n
        - `401 Unauthorized`:
        Not authenticated user.\n
        - `404 Not Found`:
        Post with that ID not found.\n

        '''
        if 'post' in request.data.keys():
            post = get_object_or_404(Post, id=request.data['post'])

            users_mentions = re.findall(r'@\w+', post.body)
            processed_user_mention = False
            for word in users_mentions:
                try:
                    user = User.objects.get(
                        user_handle=word[1:], is_active=True)
                    is_block = Block.objects.filter(
                        Q(blocked_by=post.user, blocked_user=user) |
                        Q(blocked_by=user, blocked_user=post.user)).exists()
                    if not is_block:
                        UserMention.objects.create(user=user, post=post)

                        Notification.objects.create(
                            sender=post.user,
                            recipient=user,
                            notification_type='mention',
                            post=post,
                            header=f'{post.user} mention you in a post.',
                            message=post.body,
                        )
                    processed_user_mention = True

                except:
                    continue
            if processed_user_mention:
                return Response({'detail': 'Mention/s created successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Body of post examined successfully and not found any mention.'}, status=status.HTTP_200_OK)
        else:
            return Response({'post': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)


class VoteOptionPollAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated,]
    serializer_class = CreateVoteOptionPollSerializer

    @extend_schema(request=serializer_class, responses={201: DummySerializer})
    def post(self, request: Request, pk=None, *args, **kwargs):
        '''
        Vote on a poll option for a specific post.\n

        ### Path Parameter:\n
        - `id` (int): ID of the post that want to vote a option.\n\n

        ### Request:\n
        - `poll` (int): ID of the poll that have the option.\n
        - `option` (string): Option where want to apply the vote.\n\n

        ### Response (Success):\n
        - `201 Created`:
        Vote successfully applied to the poll option.\n\n

        ### Response (Failure):\n
        - `400 Bad Request`:
        If the request is invalid.\n
        - `401 Unauthorized`:
        Not authenticated user.\n
        - `403 FORBIDDEN`:
        If the user does not have permission to access the poll.\n
        - `404 Not Found`:
        If the post with the poll is not found.\n

        '''
        try:
            post = Post.objects.select_related(
                'user').get(have_poll=True, id=pk)
        except:
            return Response({'detail': 'Post with poll not found.'}, status=status.HTTP_404_NOT_FOUND)

        blocked = is_request_user_blocked(post=post, request_user=request.user)
        if blocked:
            return Response({'detail': 'You do not have permission to access this information.'}, status=status.HTTP_403_FORBIDDEN)

        option_serializer = self.serializer_class(
            data=request.data, context={'user': request.user})
        if option_serializer.is_valid():
            option = option_serializer.save()

            opt = option.option
            poll = option.poll

            opt.votes += 1
            opt.save()
            poll.total_votes += 1
            poll.save()

            return Response({'detail': 'Vote successfully apply.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(option_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationsListAPIView(ListAPIView):
    serializer_class = ListNotificationsSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(recipient_id=self.request.user)

    def get(self, request: Request, *args, **kwargs):
        notifications = self.get_queryset()
        notifications_serializer = self.serializer_class(
            notifications, many=True)

        notification_data = notifications_serializer.data.copy()
        for noti in notifications:
            noti.is_read = True
            noti.save()
        return Response(notification_data)
