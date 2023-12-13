from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from .models import User, Follower, Block


class ListProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'user_handle', 'email',
            'first_name', 'last_name', 'birth_date',
            'biography', 'profile_img', 'header_photo',
            'website', 'location', 'create_at',
            'follower_amount', 'following_amount'
        ]

    def to_representation(self, instance):
        try:
            return {
                'username': instance['username'],
                'user_handle': instance['user_handle'],
                'email': instance['email'],
                'first_name': instance['first_name'],
                'last_name': instance['last_name'],
                'birth_date': instance['birth_date'],
                'biography': instance['biography'],
                'profile_img': instance.profile_img.url if instance['profile_img'] else '',
                'header_photo': instance.header_photo.url if instance['header_photo'] else '',
                'website': instance['website'],
                'location': instance['location'],
                'create_at': _(instance['create_at'].strftime("%B of %Y")),
                'follower_amount': instance['follower_amount'],
                'following_amount': instance['following_amount'],
            }
        except:
            return {
                'username': instance.username,
                'user_handle': instance.user_handle,
                'email': instance.email,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'birth_date': instance.birth_date,
                'biography': instance.biography,
                'profile_img': instance.profile_img.url if instance.profile_img else '',
                'header_photo': instance.header_photo.url if instance.header_photo else '',
                'website': instance.website,
                'location': instance.location,
                'create_at': _(instance.create_at.strftime("%B of %Y")),
                'follower_amount': instance.follower_amount,
                'following_amount': instance.following_amount,
            }


class ListSimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'user_handle', 'biography',
            'profile_img', 'follower_amount', 'following_amount'
        ]

    def to_representation(self, instance):

        try:
            return {
                'username': instance['username'],
                'user_handle': instance['user_handle'],
                'biography': instance['biography'],
                'profile_img': instance.profile_img.url if instance['profile_img'] else '',
                'follower_amount': instance['follower_amount'],
                'following_amount': instance['following_amount'],
            }
        except:
            return {
                'username': instance.username,
                'user_handle': instance.user_handle,

                'biography': instance.biography,
                'profile_img': instance.profile_img.url if instance.profile_img else '',
                'follower_amount': instance.follower_amount,
                'following_amount': instance.following_amount,
            }


class CreateUserSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(required=True)

    class Meta:
        model = User

        exclude = [
            'groups', 'user_permissions', 'follower_amount', 'following_amount',
            'is_active', 'is_staff', 'is_superuser', 'last_login'
        ]

    def validate_user_handle(self, user_handle):
        """
        Custom validation to ensure case-insensitive user_handle uniqueness.
        """
        User = self.Meta.model
        if User.objects.filter(user_handle__iexact=user_handle).exists():
            raise serializers.ValidationError(
                "This user_handle is already in use.")
        return user_handle

    def validate(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})

        data.pop('password2')

        return data

    def create(self, validated_data):
        validated_data['user_handle'] = validated_data['user_handle'].lower()
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])

        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        exclude = [
            'gender', 'password', 'create_at', 'groups',
            'following_amount', 'follower_amount', 'user_permissions',
            'is_active', 'is_staff', 'is_superuser', 'last_login'
        ]

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=252, min_length=8, write_only=True)
    password2 = serializers.CharField(
        max_length=252, min_length=8, write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password2': "Passwords do not match"})

        return data['password']


class PasswordCheckMatchSerializer(serializers.Serializer):
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        keys = data.keys()
        if 'password' not in keys:
            raise ValidationError({'password': 'This field is required.'})
        elif 'password2' not in keys:
            raise ValidationError({'password2': 'This field is required.'})
        else:
            return data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(
        required=True, write_only=True)


class PasswordRecoveryRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordRecoveryConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(
        required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError(
                {'confirm_new_password': "Passwords do not match"})

        return data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follower
        fields = ['following']


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['blocked_user', 'reason']


class ListBlockSerializer(serializers.ModelSerializer):
    blocked_user = ListSimpleUserSerializer(read_only=True)

    class Meta:
        model = Block
        fields = ['blocked_user', 'reason']


class DummySerializer(serializers.Serializer):
    pass
