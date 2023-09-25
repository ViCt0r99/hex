from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TierListView, TierDetailView, ImageCreateView, ThumbnailListView, ThumbnailDetailView

# Create a router for any viewsets
router = DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/tiers/', TierListView.as_view(), name='tier-list'),
    path('api/tiers/<int:pk>/', TierDetailView.as_view(), name='tier-detail'),
    path('api/images/', ImageCreateView.as_view(), name='image-create'),
    path('api/thumbnails/', ThumbnailListView.as_view(), name='thumbnail-list'),
    path('api/thumbnails/<int:pk>/', ThumbnailDetailView.as_view(), name='thumbnail-detail'),

]
