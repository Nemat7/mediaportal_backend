from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .models import EmailVerification


def send_verification_email(user):
    verification = EmailVerification.create_for_user(user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email/{verification.token}"
    send_mail(
        subject='Подтвердите ваш email — Tajflix',
        message=(
            f'Привет, {user.username}!\n\n'
            f'Для подтверждения вашего email перейдите по ссылке:\n{verify_url}\n\n'
            f'Ссылка действительна 24 часа.\n\nС уважением, команда Tajflix'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
    send_mail(
        subject='Сброс пароля — Tajflix',
        message=(
            f'Вы запросили сброс пароля.\n\n'
            f'Перейдите по ссылке:\n{reset_url}\n\n'
            f'Если вы не запрашивали сброс, проигнорируйте это письмо.\n\nС уважением, команда Tajflix'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
