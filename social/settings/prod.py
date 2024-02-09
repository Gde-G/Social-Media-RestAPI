from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG')))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE'),
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'POST': os.environ.get('DATABASE_PORT'),
    }
}

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_USE_TLS = bool(int(os.environ.get('EMAIL_USE_TLS')))
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
PASSWORD_RESET_TIMEOUT = os.environ.get('PASSWORD_RESET_TIMEOUT')

CORS_ALLOWED_ORIGINS = list(os.environ.get('CORS_ALLOWED_ORIGINS').split(','))
CORS_ORIGIN_WHITELIST = list(os.environ.get('CORS_ORIGIN_WHITELIST').split(','))
