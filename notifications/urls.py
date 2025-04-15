from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NoteViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    path('', include(router.urls)),
]
