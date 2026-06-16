from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView,
    VerifyEmailView, ResendVerificationView,
    UserProfileView, ChangePasswordView,
    PasswordResetRequestView, PasswordResetConfirmView,
    FavoriteViewSet, FavoriteIdsView, WatchHistoryViewSet,
)

router = DefaultRouter()
router.register('favorites', FavoriteViewSet, basename='favorites')
router.register('history', WatchHistoryViewSet, basename='history')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify-email/resend/', ResendVerificationView.as_view(), name='resend-verification'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/favorite-ids/', FavoriteIdsView.as_view(), name='favorite-ids'),
    path('password/change/', ChangePasswordView.as_view(), name='change-password'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('', include(router.urls)),
]
