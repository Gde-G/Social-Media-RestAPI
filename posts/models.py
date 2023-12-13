from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from core.models import DatesRecordsBaseModel
from users.models import User


def get_post_file_upload_path(self, filename):
    # Generate a unique path for the user's profile image
    return f'{self.user}/media/{filename}'


class Post(DatesRecordsBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_handle',
                             related_name=_("post_by"), verbose_name=_("Post by"))

    body = models.CharField(max_length=280, verbose_name=_("Post Content"))

    have_media = models.BooleanField(default=False)
    have_poll = models.BooleanField(default=False)
    video = models.FileField(upload_to=get_post_file_upload_path, null=True, blank=True,
                             validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    img1 = models.ImageField(upload_to=get_post_file_upload_path,
                             null=True, blank=True, verbose_name=_("Post image 1"))
    img2 = models.ImageField(upload_to=get_post_file_upload_path,
                             null=True, blank=True, verbose_name=_("Post image 2"))
    img3 = models.ImageField(upload_to=get_post_file_upload_path,
                             null=True, blank=True, verbose_name=_("Post image 3"))
    img4 = models.ImageField(upload_to=get_post_file_upload_path,
                             null=True, blank=True, verbose_name=_("Post image 4"))
    gif = models.ImageField(upload_to=get_post_file_upload_path,
                            null=True, blank=True, verbose_name=_("Post gif"))

    quote = models.ForeignKey('self', on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name=_('Quote from post'))

    num_replies = models.PositiveIntegerField(
        default=0, verbose_name=_("Replies amount"))
    num_repost = models.PositiveIntegerField(
        default=0, verbose_name=_("Repost amount"))
    num_likes = models.PositiveIntegerField(
        default=0, verbose_name=_("Likes amount"))
    num_views = models.PositiveIntegerField(
        default=0, verbose_name=_("Views amount"))

    date_to_publish = models.DateTimeField(
        default=timezone.now, verbose_name=_("Date to be publish"))

    def clean(self):
        if self.video and self.gif:
            raise ValidationError(
                "Can't parse video AND gif on the some post.")
        elif (self.video or self.gif) and (self.img1 or self.img2 or self.img3 or self.img4):
            raise ValidationError(
                "If video or gif is not null, do not use img fields.")

    def __str__(self):
        return f'{self.body}, Post by {self.user}'


class PostReply(models.Model):
    parent = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="parent_post", verbose_name=_('Parent post'))
    reply = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="reply_post", verbose_name=_('Reply post'))

    class Meta:
        verbose_name = _('Post reply')
        verbose_name_plural = _('Posts replies')

    def __str__(self):
        return f"Post with ID {self.parent.id} was reply with '{self.reply}'."


class UserMention(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_handle', related_name=_(
        "mentioned_user"), verbose_name=_("Mentioned User"))

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name=_("Post where was mentioned"))

    class Meta:
        verbose_name = _("User mention")
        verbose_name_plural = _("Users mentions")

    def __str__(self):
        return f'@{self.user} in post {self.post.id}'


class Hashtag(models.Model):
    tag = models.CharField(max_length=100, unique=True,
                           verbose_name=_('Hashtag'))
    amount_use = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("Hashtag")
        verbose_name_plural = _("Hashtags")

    def __str__(self):
        return self.tag


class HashtagsPost(models.Model):
    hashtag = models.ForeignKey(
        Hashtag, to_field="tag", on_delete=models.CASCADE, verbose_name=_('Hashtag'))
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name=_('Post'))

    class Meta:
        verbose_name = _("Hashtag use in post")
        verbose_name_plural = _("Hashtags use in posts")

    def __str__(self):
        return f'{self.hashtag} use on post {self.post.id}'


class Likes(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Like by"))
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name=_("post_liked"), verbose_name=_("Liked post"))

    class Meta:
        unique_together = ['user', 'post']

        verbose_name = _('Like')
        verbose_name_plural = _("Likes")


class Repost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name=_(
        "repost_by"), verbose_name=_("Like by"))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name=_(
        "post_reposted"), verbose_name=_("Liked post"))

    class Meta:
        unique_together = ['user', 'post']

        verbose_name = _('Repost')
        verbose_name_plural = _("Reposts")

    def __str__(self):
        return f"Post with ID {self.post.id} be repost by {self.user}."


class PollPost(models.Model):
    def _calc_end_time():
        return timezone.now() + timezone.timedelta(days=1)
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    total_votes = models.PositiveBigIntegerField(default=0)

    end_time = models.DateTimeField(
        default=_calc_end_time)

    class Meta:
        verbose_name = _('Poll')
        verbose_name_plural = _('Polls')

    def clean(self):
        if self.end_time > timezone.now() + timezone.timedelta(days=7):
            raise ValidationError(
                "The end time of the poll must be within 7 days from now.")

    def __str__(self):
        return f"Poll on post {self.post.id}."


class OptionPollPost(models.Model):
    poll = models.ForeignKey(
        PollPost, on_delete=models.CASCADE, related_name='options')
    option = models.CharField(max_length=25, verbose_name=_('Option'))
    votes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['poll', 'option']
        verbose_name = _('Poll option')
        verbose_name_plural = _('Polls options')

    def clean(self):

        if self.poll.options.count() > 4:
            raise ValidationError("A poll cannot have more than 4 options.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.poll} {self.option}, have {self.votes} votes."


class VoteOptionPoll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(PollPost, on_delete=models.CASCADE)
    option = models.ForeignKey(
        OptionPollPost, on_delete=models.CASCADE)

    vote_date = models.DateTimeField(
        auto_now=True, verbose_name=_('Date of vote'))

    class Meta:
        unique_together = ('user', 'poll')
        verbose_name = _('Vote in Poll')
        verbose_name_plural = _('Votes in Polls')

    def __str__(self):
        return f'Option {self.option.option} that corresponds to the poll {self.poll} received a vote.'


class Notification(DatesRecordsBaseModel):
    NOTIFICATION_TYPES = (
        ('mention', 'Mention'),
        ('like', 'Like'),
        ('repost', 'Repost'),
        ('quote', 'Quote'),
        ('follow', 'Follow'),

    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="notification_sender", verbose_name=_("Sender user"))
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_recipient", verbose_name=_("Recipient user"))
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, verbose_name='Notification Type')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             null=True, blank=True, verbose_name='Related Post')
    header = models.CharField(max_length=150)
    message = models.TextField(null=True, blank=True, verbose_name='Message')

    is_read = models.BooleanField(default=False, verbose_name='Read')

    class Meta:
        ordering = ('-create_at',)
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return self.header
