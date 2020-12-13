from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import (Credentials, MountPoint, WorkLoad, MigrationTarget,
                     Migration)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'password')
        model = User

    def validate_password(self, value: str) -> str:
        return make_password(value)


class MountPointSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = MountPoint


class CredentialsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Credentials


def check_object(pk, model, name):
    if pk:
        real_object = model.objects.filter(pk=pk)
        if not real_object:
            raise serializers.ValidationError(
                f'{pk} {name} does not exist'
            )
    else:
        raise serializers.ValidationError(
            {f'{name}': ['This field is required.']}
        )
    return real_object[0]


def check_mount_point(mount_point):
    mount_points = []
    mount_point_list = mount_point
    for pk in mount_point_list:
        real_mount_point = MountPoint.objects.filter(pk=pk)
        if real_mount_point:
            mount_points.append(get_object_or_404(MountPoint, pk=pk))
        else:
            raise serializers.ValidationError(
                f'{pk} storage does not exist')
    if not mount_points:
        raise serializers.ValidationError(
            {'storage': ['This field is required.']}
        )
    return mount_points


class WorkLoadSerializer(serializers.ModelSerializer):
    credentials = CredentialsSerializer(many=False, read_only=True)
    storage = MountPointSerializer(many=True, read_only=True)

    class Meta:
        fields = '__all__'
        model = WorkLoad

    def stop_change_ip(self, ip):
        if ip:
            raise serializers.ValidationError(
                {'ip': ['''Can't change for the specific source.''']}
            )

    def check_ip(self, ip):
        work_loads = WorkLoad.objects.filter(ip=ip)
        if work_loads:
            raise serializers.ValidationError(
                {'ip': ['This field is unique.']}
            )


class MigrationTargetSerializer(serializers.ModelSerializer):
    cloud_credentials = CredentialsSerializer(many=False, read_only=True)
    target_vm = WorkLoadSerializer(many=False, read_only=True)

    class Meta:
        fields = '__all__'
        model = MigrationTarget


class MigrationSerializer(serializers.ModelSerializer):
    selected_mount_points = MountPointSerializer(many=True, read_only=True)
    source_of_type = WorkLoadSerializer(many=False, read_only=True)
    migration_target = MigrationTargetSerializer(many=False, read_only=True)

    class Meta:
        fields = '__all__'
        model = Migration
