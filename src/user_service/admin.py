from django.contrib import admin

from user_service.models import (
    Organisation,
    Permission,
    Role,
    RolePermission,
    User,
    UserProfile,
)

admin.site.register(User)
admin.site.register(Organisation)
admin.site.register(Role)
admin.site.register(RolePermission)
admin.site.register(Permission)
admin.site.register(UserProfile)
