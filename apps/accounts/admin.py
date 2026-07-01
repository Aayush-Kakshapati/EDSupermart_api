from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Extra Information",
            {
                "fields": ("phone", "address", "role"),
            },
        ),
    )
