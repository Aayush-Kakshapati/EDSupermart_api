from django.urls import path
from .views import (
    NotificationListAPIView,
    NotificationMarkReadAPIView,
    NotificationMarkAllReadAPIView,
    UnreadCountAPIView
)

urlpatterns = [
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/unread-count/', UnreadCountAPIView.as_view(), name='unread-count'),
    path('notifications/<int:pk>/read/', NotificationMarkReadAPIView.as_view(), name='notification-mark-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadAPIView.as_view(), name='mark-all-read'),
]
