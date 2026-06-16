from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        # simplejwt passes the field as `email=...` (USERNAME_FIELD), not `username=`
        # so we check kwargs for email too
        login = username or kwargs.get('email')
        if not login or not password:
            return None
        try:
            if '@' in login:
                user = User.objects.get(email=login)
            else:
                user = User.objects.get(username=login)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
