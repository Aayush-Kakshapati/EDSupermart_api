from django.urls import path
from .views import (
    OrderListAPIView,
    OrderDetailAPIView,
    OrderCreateAPIView,
    OrderUpdateAPIView,
    OrderDeleteAPIView,
    OrderStatusUpdateAPIView,
    OrderConfirmDeliveryAPIView
)

urlpatterns = [
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/update/', OrderUpdateAPIView.as_view(), name='order-update'),
    path('orders/<int:pk>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('orders/<int:pk>/confirm-delivery/', OrderConfirmDeliveryAPIView.as_view(), name='order-confirm-delivery'),
    path('orders/<int:pk>/delete/', OrderDeleteAPIView.as_view(), name='order-delete'),
]
