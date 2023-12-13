from django.urls import path
from .views import (LikePostAPIView, RepostAPIView,
                    VoteOptionPollAPIView, HashtagAPIView,
                    UserMentionAPIView, NotificationsListAPIView)

urlpatterns = [
    path('posts/<str:pk>/likes/', LikePostAPIView.as_view(), name='likes-post'),
    path('posts/<str:pk>/reposts/', RepostAPIView.as_view(), name='reposts-post'),
    path('posts/<str:pk>/votepoll/',
         VoteOptionPollAPIView.as_view(), name='vote-poll-post'),
    path('hashtags/', HashtagAPIView.as_view(), name='hashtags'),
    path('user-mention/', UserMentionAPIView.as_view(), name='user-mention'),
    path('notifications/', NotificationsListAPIView.as_view(), name='notifications')
]
