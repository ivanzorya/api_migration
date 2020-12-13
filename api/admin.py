from django.contrib import admin

from .models import (Credentials, MountPoint, WorkLoad, MigrationTarget,
                     Migration)


class CredentialsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'password', 'domain')
    search_fields = ('pk', 'username', 'password', 'domain')


class MountPointAdmin(admin.ModelAdmin):
    list_display = ('pk', 'mount_point_name', 'total_size_of_the_volume')
    search_fields = ('pk', 'mount_point_name', 'total_size_of_the_volume')


class WorkLoadAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ip', 'credentials')
    search_fields = ('pk', 'ip', 'credentials', 'storage')


class MigrationTargetAdmin(admin.ModelAdmin):
    list_display = ('pk', 'cloud_type', 'cloud_credentials', 'target_vm')
    search_fields = ('pk', 'cloud_type', 'cloud_credentials', 'target_vm')


class MigrationAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'source_of_type',
        'migration_target',
        'migration_state'
    )
    search_fields = (
        'pk',
        'selected_mount_points',
        'source_of_type',
        'migration_target',
        'migration_state'
    )


admin.site.register(Credentials, CredentialsAdmin)
admin.site.register(MountPoint, MountPointAdmin)
admin.site.register(WorkLoad, WorkLoadAdmin)
admin.site.register(MigrationTarget, MigrationTargetAdmin)
admin.site.register(Migration, MigrationAdmin)
