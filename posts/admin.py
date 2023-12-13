from django.contrib import admin

from .models import (
    Post, PostReply, UserMention, Hashtag, HashtagsPost,
    OptionPollPost, PollPost, VoteOptionPoll, Notification
)
# Register your models here.
admin.site.register(Post)
admin.site.register(PostReply)
admin.site.register(UserMention)
admin.site.register(Hashtag)
admin.site.register(HashtagsPost)
admin.site.register(PollPost)
admin.site.register(VoteOptionPoll)
admin.site.register(OptionPollPost)
admin.site.register(Notification)
