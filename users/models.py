import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    email = models.EmailField('Email', unique=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    bio = models.TextField('О себе', blank=True, max_length=500)
    is_premium = models.BooleanField('Премиум подписка', default=False)
    is_email_verified = models.BooleanField('Email подтверждён', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications', verbose_name='Пользователь')
    token = models.UUIDField('Токен', default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    expires_at = models.DateTimeField('Истекает')
    is_used = models.BooleanField('Использован', default=False)

    class Meta:
        verbose_name = 'Верификация email'
        verbose_name_plural = 'Верификации email'

    def __str__(self):
        return f'{self.user.email} — {self.token}'

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def create_for_user(cls, user):
        cls.objects.filter(user=user, is_used=False).delete()
        return cls.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='Пользователь')
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Видео')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'video']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.video.title}'


class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history', verbose_name='Пользователь')
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='watched_by', verbose_name='Видео')
    progress = models.PositiveIntegerField('Прогресс (сек)', default=0)
    total_duration = models.PositiveIntegerField('Длительность (сек)', default=0)
    last_watched = models.DateTimeField('Последний просмотр', auto_now=True)
    is_finished = models.BooleanField('Досмотрено', default=False)

    class Meta:
        verbose_name = 'История просмотров'
        verbose_name_plural = 'История просмотров'
        unique_together = ['user', 'video']
        ordering = ['-last_watched']

    def __str__(self):
        return f'{self.user.email} → {self.video.title} ({self.progress}с)'

    @property
    def progress_percent(self):
        if self.total_duration:
            return round(self.progress / self.total_duration * 100)
        return 0

    @property
    def remaining_seconds(self):
        return max(0, self.total_duration - self.progress)
