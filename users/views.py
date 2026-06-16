from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'
from .models import EmailVerification
from .serializers import (
    RegisterSerializer, TajflixTokenSerializer, UserProfileSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
)
from .utils import send_verification_email, send_password_reset_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        from django.conf import settings
        if settings.DEBUG:
            user.is_active = True
            user.is_email_verified = True
            user.save()
            return Response(
                {'detail': 'Аккаунт создан. Вы можете войти.'},
                status=status.HTTP_201_CREATED,
            )
        send_verification_email(user)
        return Response(
            {'detail': f'Аккаунт создан. Письмо с подтверждением отправлено на {user.email}.'},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = TajflixTokenSerializer
    throttle_classes = [LoginRateThrottle]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Выход выполнен успешно.'})
        except Exception:
            return Response({'detail': 'Неверный токен.'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            verification = EmailVerification.objects.get(token=token)
        except EmailVerification.DoesNotExist:
            return Response({'detail': 'Недействительная ссылка.'}, status=status.HTTP_400_BAD_REQUEST)

        if not verification.is_valid():
            return Response({'detail': 'Ссылка устарела. Запросите новую.'}, status=status.HTTP_400_BAD_REQUEST)

        user = verification.user
        user.is_active = True
        user.is_email_verified = True
        user.save()
        verification.is_used = True
        verification.save()

        return Response({'detail': 'Email подтверждён. Теперь вы можете войти.'})


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_email_verified=False)
            send_verification_email(user)
            return Response({'detail': 'Письмо отправлено повторно.'})
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден или уже подтверждён.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Пароль успешно изменён.'})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = getattr(serializer, 'user', None)
        if user:
            send_password_reset_email(user)
        # Always return success to not reveal whether email exists
        return Response({'detail': 'Если аккаунт существует, письмо со сбросом пароля отправлено.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Пароль успешно сброшен.'})


# ── Favorites ─────────────────────────────────────────────────────────────────

from rest_framework import mixins, viewsets
from .models import UserFavorite, WatchHistory
from .serializers import FavoriteSerializer, WatchHistorySerializer


class FavoriteViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).select_related('video')

    def destroy(self, request, *args, **kwargs):
        video_id = kwargs.get('pk')
        deleted, _ = UserFavorite.objects.filter(user=request.user, video_id=video_id).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)


class FavoriteIdsView(APIView):
    """Returns just the list of video IDs the user has favorited — fast for UI checks."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ids = list(UserFavorite.objects.filter(user=request.user).values_list('video_id', flat=True))
        return Response(ids)


# ── Watch History ─────────────────────────────────────────────────────────────

class WatchHistoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = WatchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WatchHistory.objects.filter(user=self.request.user, is_finished=False).select_related('video')[:20]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(WatchHistorySerializer(obj, context={'request': request}).data,
                        status=status.HTTP_200_OK)
