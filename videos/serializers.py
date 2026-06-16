from rest_framework import serializers
from .models import Category, Tag, Video, Season, Episode


class CategorySerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(source='videos.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'video_count']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ['id', 'number', 'title', 'description', 'duration', 'thumbnail_url', 'video_url']


class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ['id', 'number', 'title', 'episodes']


class VideoListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    thumbnail = serializers.SerializerMethodField()
    backdrop = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'year', 'rating', 'duration', 'quality',
            'category', 'tags', 'thumbnail', 'backdrop',
            'views', 'studio', 'is_new', 'is_popular', 'is_hero',
        ]

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return obj.thumbnail_url

    def get_backdrop(self, obj):
        request = self.context.get('request')
        if obj.backdrop:
            url = obj.backdrop.url
            return request.build_absolute_uri(url) if request else url
        return obj.backdrop_url


class VideoDetailSerializer(VideoListSerializer):
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta(VideoListSerializer.Meta):
        fields = VideoListSerializer.Meta.fields + ['seasons', 'video_url', 'created_at']
