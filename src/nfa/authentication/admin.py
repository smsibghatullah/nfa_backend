from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User

    list_display = ("email", "cnic", "first_name", "last_name", "is_active", "is_staff", "last_login")
    
    search_fields = ("email", "cnic", "first_name", "last_name")
    
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "cnic", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "cnic", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )
