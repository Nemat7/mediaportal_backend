from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from .models import Category, Tag, Video
from .serializers import CategorySerializer, TagSerializer, VideoListSerializer, VideoDetailSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def videos(self, request, slug=None):
        category = self.get_object()
        videos = category.videos.all()
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.select_related('category').prefetch_related('tags')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'quality', 'year', 'is_new', 'is_popular', 'is_hero']
    search_fields = ['title', 'description', 'studio', 'tags__name']
    ordering_fields = ['rating', 'views', 'year', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VideoDetailSerializer
        return VideoListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Video.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hero(self, request):
        videos = self.queryset.filter(is_hero=True)[:8]
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        videos = self.queryset.filter(is_popular=True)[:20]
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new(self, request):
        videos = self.queryset.filter(is_new=True)[:20]
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)
