import random

from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .tokens import account_activation_token
from .models import User


def activate_with_email(request, user, to_email):

    try:
        mail_subject = "Bienvenido/a a Carbono Smart - Confirmación de Registro"

        context = {
            'user': user.username,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http',
        }

        temp = get_template('email_confirmation_message.html')

        content = temp.render(context)

        corr = EmailMultiAlternatives(
            subject=mail_subject,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
        )

        corr.attach_alternative(content, 'text/html')
        corr.send(fail_silently=False)

    except:
        print('ERROR')


def generate_available_username_suggestions(base_user_handle, max_suggestions=3):
    existing_user_handles = User.objects.all().values('user_handle')

    suggestions = []
    for i in range(1, max_suggestions + 1):
        suggestion = f"{base_user_handle}{random.randint(10, 1000)}"
        if suggestion not in existing_user_handles:
            suggestions.append(suggestion)
    return suggestions


def recover_account_email(request, user, to_email, token):
    # try:
    mail_subject = "Recovery your account - Social Media API"

    context = {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token,
        'protocol': 'https' if request.is_secure() else 'http',
    }

    temp = get_template('password_reset_key_message.html')

    content = temp.render(context)

    corr = EmailMultiAlternatives(
        subject=mail_subject,
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email],
    )

    corr.attach_alternative(content, 'text/html')
    corr.send(fail_silently=False)

    # except:
    #     print('ERROR')
