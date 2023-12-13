import os
import random
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from faker import Faker
from faker.providers import BaseProvider
from users.test.factories import UserFactory
from posts.models import Post


class PostFieldsProvider(BaseProvider):

    def image(self, width=640, height=480):

        image = Image.new('RGB', (width, height), 'rgb(255, 255, 255)')
        stream = BytesIO()
        image.save(stream, format='JPEG')

        filename = f"{faker.word() + str(random.randint(0, 1000))}.jpg"

        image_file = InMemoryUploadedFile(
            stream,
            None,
            filename,
            'image/jpeg',
            stream.getbuffer().nbytes,
            None
        )
        return image_file

    def gif(self, width=640, height=480, frames=10):
        # Generate a fake GIF using Pillow
        gif = Image.new('RGB', (width, height), 'rgb(255, 255, 255)')
        frames_list = []

        for _ in range(frames):
            frame = Image.new('RGB', (width, height), 'rgb(255, 255, 255)')
            frames_list.append(frame)

        stream = BytesIO()
        frames_list[0].save(stream, format='GIF', save_all=True,
                            append_images=frames_list[1:], duration=200, loop=0)

        # Generate a unique filename for the GIF
        filename = f"{faker.word() + str(random.randint(0, 1000))}.gif"

        # Save the GIF data to an InMemoryUploadedFile
        gif_file = InMemoryUploadedFile(
            stream,
            None,
            filename,
            'image/gif',
            stream.getbuffer().nbytes,
            None
        )
        return gif_file

    def video(self, duration_seconds=10):
        # Generate random binary data to simulate a video file
        # 5 MB for example, adjust as needed
        video_data = os.urandom(1024 * 1024 * 5)

        # Generate a unique filename for the video
        filename = f"{faker.word() + str(random.randint(0, 1000))}.mp4"

        # Save the video data to an InMemoryUploadedFile
        video_file = InMemoryUploadedFile(
            BytesIO(video_data),
            None,
            filename,
            'video/mp4',  # Adjust the mime type based on your needs
            len(video_data),
            None
        )
        return video_file


faker = Faker()
faker.add_provider(PostFieldsProvider)


class PostFactory:
    def body(self):
        return faker.text(max_nb_chars=250)

    def body_with_hashtag(self):
        return faker.text(max_nb_chars=200) + f'#{faker.word()}'

    def body_with_mention(self):
        fac = UserFactory()
        user = fac.create_active_user()
        return faker.text(max_nb_chars=200) + f'@{user.user_handle}'

    def image(self):
        return faker.image()

    def gif(self):
        return faker.gif()

    def video(self):
        return faker.video()

    def option(self):
        return faker.text(max_nb_chars=25)

    def create_post(self):
        fac = UserFactory()
        return Post.objects.create(
            body=self.body(),
            user=fac.create_active_user(),
        )

    def create_post_kwargs(self, **kwargs):
        return Post.objects.create(**kwargs)

    def create_post_and_user(self):
        fac = UserFactory()

        user = fac.create_active_user()
        post = Post.objects.create(
            body=self.body,
            user=user,
        )

        return post, user


class HashtagFactory:

    def hashtag(self):
        word1 = faker.word().capitalize()
        word2 = faker.word()

        return f'{word1}{word2}'
