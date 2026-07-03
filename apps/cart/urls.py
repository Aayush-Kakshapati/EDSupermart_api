from django.urls import path
from .views import CartAPIView, CartItemAddAPIView, CartItemDeleteAPIView

urlpatterns = [
    path("cart/", CartAPIView.as_view(), name='cart-list'),
    path("cart/items/", CartItemAddAPIView.as_view(), name='cart-items'),
    path("cart/items/<int:pk>/", CartItemDeleteAPIView.as_view(), name='cart-item-detail')
]