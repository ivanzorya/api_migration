from time import sleep

from django.db import models
from rest_framework.generics import get_object_or_404


class Credentials(models.Model):
    username = models.TextField(
        max_length=50,
        blank=False,
        null=False
    )
    password = models.TextField(
        max_length=50,
        blank=False,
        null=False
    )
    domain = models.TextField(
        max_length=100,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f'{self.pk} {self.domain}'


class MountPoint(models.Model):
    mount_point_name = models.TextField(
        max_length=100,
        blank=False,
        null=False
    )
    total_size_of_the_volume = models.PositiveIntegerField(
        db_index=True,
        blank=False,
        null=False
    )


class WorkLoad(models.Model):
    ip = models.TextField(
        max_length=50,
        blank=False,
        null=False
    )
    credentials = models.ForeignKey(
        Credentials,
        related_name="workloads",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    storage = models.ManyToManyField(
        MountPoint,
        related_name="workloads"
    )

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f'{self.pk} {self.ip}'


class CloudType(models.TextChoices):
    AWS = 'aws'
    AZURE = 'azure'
    VSPHERE = 'vsphere'
    VCLOUD = 'vcloud'


class MigrationTarget(models.Model):
    cloud_type = models.CharField(
        max_length=7,
        choices=CloudType.choices,
        default=CloudType.AWS
    )
    cloud_credentials = models.ForeignKey(
        Credentials,
        related_name="migration_targets",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    target_vm = models.ForeignKey(
        WorkLoad,
        related_name="migration_targets",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f'{self.pk} {self.cloud_type}'


class MigrationState(models.TextChoices):
    NOT_STARTED = 'not_started'
    RUNNING = 'running'
    ERROR = 'error'
    SUCCESS = 'success'


class Migration(models.Model):
    selected_mount_points = models.ManyToManyField(
        MountPoint,
        related_name="migrations"
    )
    source_of_type = models.ForeignKey(
        WorkLoad,
        related_name="migrations",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    migration_target = models.ForeignKey(
        MigrationTarget,
        related_name="migrations",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    migration_state = models.CharField(
        max_length=11,
        choices=MigrationState.choices,
        default=MigrationState.NOT_STARTED
    )

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f'{self.pk} {self.migration_target} {self.migration_state}'

    def run_migration(self):
        migration = get_object_or_404(Migration, pk=self.pk)
        migration.migration_state = MigrationState.RUNNING
        migration.save()
        sleep(10)
        migration_target = migration.migration_target
        source = migration.source_of_type
        if source.storage.all() == migration.selected_mount_points.all():
            try:
                migration_target.target_vm = source
                migration_target.save()
            except Exception as e:
                migration.migration_state = MigrationState.ERROR
                migration.save()
                return e
        else:
            destination_storages = migration.check_mount_point(
                source.storage.all(),
                migration.selected_mount_points.all()
            )
            if not destination_storages:
                migration.migration_state = MigrationState.ERROR
                migration.save()
                return 'selected_mount_points not in source'
            else:
                try:
                    destination_source = WorkLoad.objects.create(
                        ip=source.ip,
                        credentials=source.credentials
                    )
                    destination_source.storage.set(destination_storages)
                    migration_target.target_vm = destination_source
                    migration_target.save()
                    migration.migration_state = MigrationState.SUCCESS
                    migration.save()
                except Exception as e:
                    migration.migration_state = MigrationState.ERROR
                    migration.save()
                    return e

    def check_mount_point(self, source_mount_points, selected_mount_points):
        destination_mount_points = set(
            source_mount_points
        ).intersection(set(selected_mount_points))
        return list(destination_mount_points)
