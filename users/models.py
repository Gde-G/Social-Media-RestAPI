from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError

from core.models import DatesRecordsBaseModel


def get_profile_file_upload_path(self, filename):
    return f'{self.username}/profile/{filename}'


def get_header_file_upload_path(self, filename):
    return f'{self.username}/header/{filename}'


class CustomAccountManager(BaseUserManager):

    def create_user(self, first_name, last_name, username, user_handle, email, password, **other_fields):
        if not email:
            raise ValueError(_("You must provide a email address!"))

        if not username:
            raise ValueError(_("You must provide a username!"))

        if not user_handle:
            raise ValidationError(_("You must provide a user_handle."))

        if not first_name:
            raise ValueError(_("You must provide a first_name!"))

        if not last_name:
            raise ValueError(_("You must provide a last_name!"))

        if not password:
            raise ValueError(_("You must provide a password!"))

        email = self.normalize_email(email)

        if other_fields.get('email_substitute') is True:
            other_fields['email_substitute'] = self.normalize_email(
                other_fields['email_substitute'])

        user = self.model(email=email, first_name=first_name,
                          last_name=last_name, username=username,
                          **other_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, first_name, last_name, username, user_handle, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Restricted Access')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Restricted Access')

        return self.create_user(first_name, last_name, username, user_handle, email, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin, DatesRecordsBaseModel):
    GENDER = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Other', 'Other')
    ]
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    username = models.CharField(max_length=100)
    user_handle = models.CharField(max_length=70, unique=True)
    biography = models.CharField(max_length=160, null=True, blank=True)

    profile_img = models.ImageField(
        upload_to=get_profile_file_upload_path, null=True, blank=True)
    header_photo = models.ImageField(
        upload_to=get_header_file_upload_path, null=True, blank=True)
    email = models.EmailField(unique=True)
    email_substitute = models.EmailField(
        _('Email substitute'), null=True, blank=True)
    gender = models.CharField(max_length=15, choices=GENDER)
    website = models.URLField(null=True, blank=True)
    location = models.CharField(max_length=160, null=True, blank=True)

    following_amount = models.PositiveIntegerField(default=0)
    follower_amount = models.PositiveIntegerField(default=0)

    birth_date = models.DateField(null=True, blank=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.user_handle


class ResetLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    expiration_time = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        """
        Check if the reset link is valid (not used and not expired).
        """
        now = timezone.now()
        return not self.used and self.expiration_time > now

    def mark_as_used(self):
        """
        Mark the reset link as used.
        """
        self.used = True
        self.save()


class Follower(DatesRecordsBaseModel):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_handle',
                                 related_name="follower", verbose_name=_('Follower'))
    following = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_handle',
                                  related_name="following", verbose_name=_('Following'))

    class Meta:
        unique_together = ['follower', 'following']

        verbose_name = _('Follower')
        verbose_name_plural = _("Followers")

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("A user cannot follow themselves.")

    def __str__(self):
        return f'{self.follower} is following to {self.following}'


class Block(models.Model):
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   to_field='user_handle', related_name='blocks', verbose_name='Blocked by')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE,  to_field='user_handle',
                                     related_name='blocked_users', verbose_name='Blocked User')
    reason = models.TextField(blank=True, null=True)
    block_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('blocked_by', 'blocked_user')
        verbose_name = _("User block")
        verbose_name_plural = _("Users Block")

    def __str__(self):
        return f'{self.blocked_by} blocked the user {self.blocked_user}.'
