from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import ListSimpleUserSerializer

from .models import (
    Post, PostReply, OptionPollPost, PollPost, Likes, Repost, Hashtag,
    HashtagsPost, UserMention, VoteOptionPoll, Notification,
)


class ListPollPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollPost
        fields = ['id', 'option1', 'option2', 'option3',
                  'option4', 'total_votes', 'end_time']


class CreatePostSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), allow_null=True, required=False)
    quote = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), allow_null=True, required=False)

    opt1 = serializers.CharField(max_length=25, required=False)
    opt2 = serializers.CharField(max_length=25, required=False)
    opt3 = serializers.CharField(
        max_length=25, allow_null=True, required=False)
    opt4 = serializers.CharField(
        max_length=25, allow_null=True, required=False)
    end_time = serializers.DateTimeField(
        default=timezone.now()+timezone.timedelta(days=1), required=False)

    class Meta:
        model = Post
        fields = [
            'user', 'body', 'video', 'img1', 'img2', 'img3', 'img4', 'gif',
            'date_to_publish', 'quote', 'parent', 'opt1', 'opt2',
            'opt3', 'opt4', 'end_time'
        ]

    def validate(self, data):
        data_keys = data.keys()
        if 'opt1' in data_keys and ('video' in data_keys or 'img1' in data_keys or 'gif' in data_keys):
            raise ValidationError(
                {'poll': "Can't make a poll and use multi media in a post."})
        elif 'video' in data_keys and ('img1' in data_keys or 'gif' in data_keys):
            raise ValidationError(
                {'video': 'Multi different media types, are not support.'})
        elif 'img1' in data_keys and 'gif' in data_keys:
            raise ValidationError(
                {'gif': 'Multi different media types, are not support.'})

        try:
            if data['opt1'] != None and data['opt2'] == None:
                raise ValidationError(
                    {'opt2': 'The poll must have at least 2 options.'})
            elif data['opt1'] != None and data['opt2'] != None and data['end_poll'] == None:
                raise ValidationError(
                    {'end_poll': 'The poll must have a limit date.'})
        except:
            pass

        return data

    def create(self, validated_data):
        try:
            parent = validated_data.pop('parent')
        except:
            parent = None

        try:
            opt1 = validated_data.pop('opt1')
            opt2 = validated_data.pop('opt2')

            if 'opt3' in validated_data.keys():
                opt3 = validated_data.pop('opt3')
            else:
                opt3 = None
            if 'opt4' in validated_data.keys():
                opt4 = validated_data.pop('opt4')
            else:
                opt4 = None

        except:
            opt1 = None
            opt2 = None
            end_time = None
        end_time = validated_data.pop('end_time')
        post = self.Meta.model(**validated_data)
        post.save()

        if parent:
            PostReply.objects.create(parent=parent, reply=post)
            parent.num_replies += 1
            parent.save()

            Notification.objects.create(
                sender=post.user,
                recipient=parent.user,
                notification_type='reply',
                post=post,
                header=f'{post.user} reply your post.',
                message=post.body,
            )

        if opt1 and opt2:
            poll = PollPost.objects.create(
                post=post,
                end_time=end_time
            )
            opt1 = OptionPollPost.objects.create(poll=poll, option=opt1)
            opt2 = OptionPollPost.objects.create(poll=poll, option=opt2)

            if opt3:
                opt3 = OptionPollPost.objects.create(poll=poll, option=opt3)
            if opt4:
                opt4 = OptionPollPost.objects.create(poll=poll, option=opt4)

            post.have_poll = True
            post.save()
        return post


class BaseListPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            'id', 'body',  'video', 'img1', 'img2', 'img3', 'img4', 'gif',
            'quote', 'date_to_publish', 'num_replies', 'num_repost', 'num_likes',
            'num_views'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id

        if instance.have_media:
            representation['media'] = {}
            if instance.video:
                representation['media']['video'] = instance.video.url

            elif instance.img1 or instance.img2 or instance.img3 or instance.img4:
                if instance.img1:
                    representation['media']['img1'] = instance.img1.url
                if instance.img2:
                    representation['media']['img2'] = instance.img2.url
                if instance.img3:
                    representation['media']['img3'] = instance.img3.url
                if instance.img4:
                    representation['media']['img4'] = instance.img4.url

            elif instance.gif:
                representation['media']['gif'] = instance.gif.url

        elif instance.have_poll:

            try:
                poll = PollPost.objects.get(post=instance)
                options = poll.options.all()
                representation['poll'] = {
                    'id': poll.id,
                    'total_votes': poll.total_votes,
                    'end_time': poll.end_time,
                }
                for i in range(len(options)):
                    representation['poll'][f'option{str(i+1)}'] = {
                        'option': options[i].option,
                        'votes': options[i].votes
                    }

            except:
                pass

        hashtags = HashtagsPost.objects.select_related(
            'hashtag').filter(post=instance.id)
        if hashtags.exists():
            representation['hashtags'] = []
            for tag in hashtags:
                representation['hashtags'].append(
                    {
                        'tag': tag.hashtag.tag,
                        'amount_use': tag.hashtag.amount_use
                    }
                )

        users_mentions = UserMention.objects.select_related(
            'user').filter(post=instance.id)
        if users_mentions.exists():
            representation['users-mention'] = []
            for mention in users_mentions:
                representation['users-mention'].append(
                    ListSimpleUserSerializer(mention.user).data)

        representation.pop('video')
        representation.pop('img1')
        representation.pop('img2')
        representation.pop('img3')
        representation.pop('img4')
        representation.pop('gif')

        return representation


class ListPostNoQuoteSerializer(BaseListPostSerializer):
    user = ListSimpleUserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = BaseListPostSerializer.Meta.fields + ['user']
        fields.remove('quote')


class ListPostSerializer(BaseListPostSerializer):
    user = ListSimpleUserSerializer(read_only=True)
    quote = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = BaseListPostSerializer.Meta.fields + ['user']

    def get_quote(self, instance):
        if instance.quote:
            return ListPostNoQuoteSerializer(instance.quote).data
        return None


class ListLikedPostSerializer(serializers.ModelSerializer):
    post = ListPostSerializer(read_only=True)
    user = ListSimpleUserSerializer(read_only=True)

    class Meta:
        model = Likes
        fields = ['user', 'post']

    def to_representation(self, instance):

        representation = super().to_representation(instance)
        representation['liked_by'] = representation.pop('user')
        representation['post'] = representation.pop('post')

        return representation


class ListRepostPostSerializer(serializers.ModelSerializer):
    post = ListPostSerializer(read_only=True)
    user = ListSimpleUserSerializer(read_only=True)

    class Meta:
        model = Repost
        fields = ['user', 'post']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['repost_by'] = representation.pop('user')
        representation['post'] = representation.pop('post')

        return representation


class ListPostNotificationSerializer(BaseListPostSerializer):

    pass


class ListPostRepliesSerializer(serializers.ModelSerializer):
    post = ListPostSerializer(read_only=True)
    replies = ListPostSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['post', 'replies']


class CreateVoteOptionPollSerializer(serializers.ModelSerializer):
    option = serializers.CharField(max_length=25)

    class Meta:
        model = VoteOptionPoll
        fields = ['poll', 'option']

    def to_internal_value(self, data):
        new_data = data.copy()
        if 'option' in data:
            option_name = new_data['option']

            try:
                poll = PollPost.objects.get(id=new_data['poll'])
                option = OptionPollPost.objects.get(
                    poll=poll, option=option_name)
                new_data['option'] = option.option

            except PollPost.DoesNotExist:
                raise serializers.ValidationError(
                    {'poll': "Poll not found."})
            except OptionPollPost.DoesNotExist:
                raise serializers.ValidationError(
                    {'option': "Option not found."})

        return super().to_internal_value(new_data)

    def validate(self, data):
        user = self.context.get('user')
        poll = data['poll']
        opt_to_vote = self.Meta.model.objects.filter(
            user=user, poll=poll)
        if opt_to_vote.exists():
            raise serializers.ValidationError(
                {"detail": "You have already voted on an option of this poll."})

        if poll.end_time < timezone.now():
            raise serializers.ValidationError(
                {"poll": "Voting for this poll has ended."})

        return super().validate(data)

    def create(self, validated_data):

        user = self.context.get('user')
        return self.Meta.model.objects.create(
            user=user,
            poll=validated_data['poll'],
            option=OptionPollPost.objects.get(
                poll=validated_data['poll'],
                option=validated_data['option'])
        )


class ListHashtagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'tag': f'{instance.tag.capitalize()}',
            'amount_used': instance.amount_use
        }


class ListNotificationsSerializer(serializers.ModelSerializer):
    sender = ListSimpleUserSerializer(read_only=True)
    post = ListPostNotificationSerializer(read_only=True)

    class Meta:
        model = Notification
        exclude = ['recipient', 'modify_at', 'id']


class DummySerializer(serializers.Serializer):
    pass
