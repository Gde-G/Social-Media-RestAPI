from django.contrib.auth.backends import BaseBackend
from .models import User
from django.db.models import Q


class MyUserBackend(BaseBackend):

    def authenticate(self, request, email=None, password=None):
        try:
            # Username, Email or user_handle Accepts
            user = User.objects.get(Q(is_active=True) &
                                    (Q(username__iexact=email) | Q(email__iexact=email) | Q(user_handle__iexact=email)))

            if user.check_password(password) or user.password == password:
                return user

        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
