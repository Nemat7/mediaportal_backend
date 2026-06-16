from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TagViewSet, VideoViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('tags', TagViewSet)
router.register('videos', VideoViewSet)

urlpatterns = router.urls
