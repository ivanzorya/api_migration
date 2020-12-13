from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (Credentials, MountPoint, WorkLoad, MigrationTarget,
                     Migration)
from .serializers import (UserSerializer, CredentialsSerializer,
                          MountPointSerializer, WorkLoadSerializer,
                          MigrationTargetSerializer, MigrationSerializer,
                          check_mount_point, check_object)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', ]

    def perform_create(self, serializer):
        serializer.save(is_active=True)


class CredentialsViewSet(viewsets.ModelViewSet):
    queryset = Credentials.objects.all()
    serializer_class = CredentialsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']


class MountPointViewSet(viewsets.ModelViewSet):
    queryset = MountPoint.objects.all()
    serializer_class = MountPointSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']


class WorkLoadViewSet(viewsets.ModelViewSet):
    queryset = WorkLoad.objects.all()
    serializer_class = WorkLoadSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.check_ip(self.request.data.get('ip'))
        credentials = check_object(
            self.request.data.get('credentials'),
            Credentials,
            'credentials'
        )
        storage = check_mount_point(self.request.data.getlist('storage'))
        serializer.save(credentials=credentials, storage=storage)

    def perform_update(self, serializer):
        serializer.stop_change_ip(self.request.data.get('ip'))
        if self.request.data.get('credentials'):
            credentials = check_object(
                self.request.data.get('credentials'),
                Credentials,
                'credentials'
            )
            serializer.save(credentials=credentials)
        if self.request.data.getlist('storage'):
            storage = check_mount_point(self.request.data.getlist('storage'))
            serializer.save(storage=storage)


class MigrationTargetViewSet(viewsets.ModelViewSet):
    queryset = MigrationTarget.objects.all()
    serializer_class = MigrationTargetSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        cloud_credentials = check_object(
            self.request.data.get('cloud_credentials'),
            Credentials,
            'cloud_credentials'
        )
        if self.request.data.get('target_vm'):
            target_vm = check_object(
                self.request.data.get('target_vm'),
                WorkLoad,
                'target_vm'
            )
            serializer.save(target_vm=target_vm)
        serializer.save(
            cloud_credentials=cloud_credentials
        )

    def perform_update(self, serializer):
        if self.request.data.get('cloud_credentials'):
            cloud_credentials = check_object(
                self.request.data.get('cloud_credentials'),
                Credentials,
                'credentials'
            )
            serializer.save(cloud_credentials=cloud_credentials)
        if self.request.data.get('target_vm'):
            target_vm = check_object(
                self.request.data.get('target_vm'),
                WorkLoad,
                'work load'
            )
            serializer.save(target_vm=target_vm)
        serializer.save()


class MigrationViewSet(viewsets.ModelViewSet):
    queryset = Migration.objects.all()
    serializer_class = MigrationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        selected_mount_points = check_mount_point(
            self.request.data.getlist('selected_mount_points')
        )
        source_of_type = check_object(
            self.request.data.get('source_of_type'),
            WorkLoad,
            'work load'
        )
        migration_target = check_object(
            self.request.data.get('migration_target'),
            MigrationTarget,
            'migration target'
        )
        serializer.save(
            selected_mount_points=selected_mount_points,
            source_of_type=source_of_type,
            migration_target=migration_target
        )

    def perform_update(self, serializer):
        if self.request.data.getlist('selected_mount_points'):
            selected_mount_points = check_mount_point(
                self.request.data.getlist('selected_mount_points')
            )
            serializer.save(selected_mount_points=selected_mount_points)
        if self.request.data.get('source_of_type'):
            source_of_type = check_object(
                self.request.data.get('source_of_type'),
                WorkLoad,
                'work load'
            )
            serializer.save(source_of_type=source_of_type)
        if self.request.data.get('migration_target'):
            migration_target = check_object(
                self.request.data.get('migration_target'),
                MigrationTarget,
                'migration target'
            )
            serializer.save(migration_target=migration_target)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def run_migration(request, migration_id):
    migration = get_object_or_404(Migration, pk=migration_id)
    if migration.migration_state not in ('not_started', 'error'):
        return Response({'''migration can't run'''}, status=400)
    error = migration.run_migration()
    if error:
        return Response(error, status=400)
    return Response('migration successfully', status=200)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_migration_state(request, migration_id):
    migration = get_object_or_404(Migration, pk=migration_id)
    data = {
        'migration state': migration.migration_state
    }
    return Response(data, status=200)
