from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label='Подтверждение пароля')

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Это имя пользователя уже занято.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Пароли не совпадают.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        return user


class TajflixTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_email_verified:
            raise serializers.ValidationError(
                {'detail': 'Подтвердите ваш email перед входом. Проверьте почту.'}
            )
        data['user'] = UserProfileSerializer(self.user).data
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'bio', 'avatar', 'avatar_url', 'is_premium', 'is_email_verified',
            'date_joined',
        ]
        read_only_fields = ['email', 'is_premium', 'is_email_verified', 'date_joined']
        extra_kwargs = {'avatar': {'write_only': True}}

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password2 = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Пароли не совпадают.'})
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password2 = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Пароли не совпадают.'})
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            self.user = User.objects.get(pk=uid)
        except (ValueError, User.DoesNotExist):
            raise serializers.ValidationError({'uid': 'Недействительная ссылка.'})
        if not default_token_generator.check_token(self.user, data['token']):
            raise serializers.ValidationError({'token': 'Ссылка недействительна или устарела.'})
        return data


# ── Favorites & Watch History ─────────────────────────────────────────────────

from .models import UserFavorite, WatchHistory
from videos.serializers import VideoListSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    video = VideoListSerializer(read_only=True)
    video_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserFavorite
        fields = ['id', 'video', 'video_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return UserFavorite.objects.get_or_create(**validated_data)[0]


class WatchHistorySerializer(serializers.ModelSerializer):
    video = VideoListSerializer(read_only=True)
    video_id = serializers.IntegerField(write_only=True)
    progress_percent = serializers.IntegerField(read_only=True)
    remaining_seconds = serializers.IntegerField(read_only=True)

    class Meta:
        model = WatchHistory
        fields = [
            'id', 'video', 'video_id', 'progress', 'total_duration',
            'progress_percent', 'remaining_seconds', 'last_watched', 'is_finished',
        ]
        read_only_fields = ['id', 'last_watched']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        obj, _ = WatchHistory.objects.get_or_create(
            user=validated_data['user'],
            video_id=validated_data['video_id'],
            defaults=validated_data,
        )
        if not _:
            for key in ['progress', 'total_duration', 'is_finished']:
                if key in validated_data:
                    setattr(obj, key, validated_data[key])
            obj.save()
        return obj
