from rest_framework import status
from rest_framework.response import Response

from users.models import Block
from .models import Post


def is_request_user_blocked(post_pk=None, post=None, owner=None, request_user=None):
    try:
        if post_pk:
            post = Post.objects.select_related('user').get(id=post_pk)
            blocked = Block.objects.filter(
                blocked_by=post.user, blocked_user=request_user).exists()
        elif post:
            blocked = Block.objects.filter(
                blocked_by=post.user, blocked_user=request_user).exists()
        else:
            blocked = Block.objects.filter(
                blocked_by=owner, blocked_user=request_user).exists()
        return blocked
    except:
        return False
