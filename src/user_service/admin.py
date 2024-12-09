from django.contrib import admin

from user_service.models import (
    Organisation,
    Permission,
    Role,
    RolePermission,
    User,
    UserProfile,
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "firstname",
        "middlename",
        "lastname",
        "role",
        "organisation",
        "user_station",
        "is_active",
        "is_superuser",
        "created_at",
        "updated_at"
    ]

    list_filter = [
        "username",
        "role",
        "user_station",
        "is_active",
        "created_at"
    ]

    search_fields = [
        "username",
        "email",
        "role"
    ]

    date_hierarchy = "created_at"

    ordering = [
        "username",
        "email",
        "firstname",
        "role",
        "user_station",
        "created_at",
        "is_active"
    ]

    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Organisation)
class OrgAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "logo",
        "address",
        "contact",
        "email",
        "owner",
        "created_at"
    ]

    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]

    list_filter = ["name", "created_at"]
    search_fields = ["name"]
    date_hierarchy = "created_at"

    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Permission)
class PermAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]
    list_filter = ["name", "created_at"]
    search_fields = ["name"]
    date_hierarchy = "created_at"

    show_facets = admin.ShowFacets.ALWAYS


admin.site.register(RolePermission)
admin.site.register(UserProfile)


