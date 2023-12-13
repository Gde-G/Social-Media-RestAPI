from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'some-key-jeje'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASES_ENGINE'),
        'NAME': os.environ.get('DATABASES_NAME'),
        'USER': os.environ.get('DATABASES_USER'),
        'PASSWORD': os.environ.get('DATABASES_PASSWORD'),
        'HOST': os.environ.get('DATABASES_HOST'),
        'POST': os.environ.get('DATABASES_POST'),
    }
}

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000"
]
CORS_ORIGIN_WHITELIST = [  # No es necesario creo
    "http://localhost:3000"
]
