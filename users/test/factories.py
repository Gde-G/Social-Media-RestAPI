import random
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from faker import Faker
from faker.providers import BaseProvider
from users.models import User


class UserFieldsProvider(BaseProvider):
    def website(self):
        return f"http://{faker.word()}.{self.random_element(['com', 'net', 'org', 'gov'])}"

    def image(self, width=640, height=480):
        # Generate a fake image using Pillow
        image = Image.new('RGB', (width, height), 'rgb(255, 255, 255)')
        stream = BytesIO()
        image.save(stream, format='JPEG')

        # Generate a unique filename for the image
        filename = f"{faker.word() + str(random.randint(0, 1000))}.jpg"

        # Save the image data to an InMemoryUploadedFile
        image_file = InMemoryUploadedFile(
            stream,
            None,
            filename,
            'image/jpeg',
            stream.getbuffer().nbytes,
            None
        )
        return image_file


faker = Faker()
faker.add_provider(UserFieldsProvider)


class UserFactory:

    def first_name(self):
        first_name = faker.first_name()
        if len(first_name) >= 100:
            first_name = first_name[:98]

        return first_name

    def last_name(self):
        last_name = faker.last_name()
        if len(last_name) >= 100:
            last_name = last_name[:98]

        return last_name

    def username(self):
        username = faker.user_name()
        if len(username) >= 100:
            username = username[:98]

        return username

    def user_handle(self):
        user_handle = faker.user_name().lower()
        if len(user_handle) >= 70:
            user_handle = user_handle[:69]

        return user_handle

    def email(self):
        return faker.email()

    def email_substitute(self):
        return faker.email()

    def gender(self):
        return random.choice(User.GENDER)[0]

    def birth_date(self):
        return faker.date_of_birth(minimum_age=18, maximum_age=65)

    def biography(self):
        return faker.text(max_nb_chars=159)

    def location(self):
        location = f'{faker.city}, {faker.country}'
        return location[:158]

    def website(self):
        return faker.website()

    def profile_img(self):
        return faker.image()

    def header_img(self):
        return faker.image()

    def create_active_user(self):

        return User.objects.create(
            username=self.username(),
            user_handle=self.user_handle(),
            email=self.email(),
            first_name=self.first_name(),
            last_name=self.last_name(),
            gender=self.gender(),
            password='Belgrano1905',
            is_active=True
        )
