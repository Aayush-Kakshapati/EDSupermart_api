from django.urls import path

from .views import UserCreateAPIView

urlpatterns = [
    path("users/create", UserCreateAPIView.as_view(), name="user-create")
] 