import json
import uuid

from django.contrib.auth.models import User
from django.http import QueryDict
from django.test import Client
from django.test import TestCase
from rest_framework.test import RequestsClient, APITestCase

from .models import (Credentials, MountPoint, WorkLoad, MigrationTarget,
                     Migration)


class SetUpTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = uuid.uuid4().hex
        self.password = uuid.uuid4().hex
        self.user = User.objects.create_user(
            username=self.username,
            email=f"{self.username}@gmail.com",
            password=self.password
        )
        self.username_1 = uuid.uuid4().hex
        self.password_1 = uuid.uuid4().hex
        self.domain_1 = uuid.uuid4().hex
        self.credentials_1 = Credentials.objects.create(
            username=self.username_1,
            password=self.password_1,
            domain=self.domain_1
        )
        self.username_2 = uuid.uuid4().hex
        self.password_2 = uuid.uuid4().hex
        self.domain_2 = uuid.uuid4().hex
        self.credentials_2 = Credentials.objects.create(
            username=self.username_2,
            password=self.password_2,
            domain=self.domain_2
        )
        self.mount_point_name_1 = uuid.uuid4().hex
        self.total_size_of_the_volume_1 = uuid.getnode()
        self.mount_point_1 = MountPoint.objects.create(
            mount_point_name=self.mount_point_name_1,
            total_size_of_the_volume=self.total_size_of_the_volume_1
        )
        self.mount_point_name_2 = uuid.uuid4().hex
        self.total_size_of_the_volume_2 = uuid.getnode()
        self.mount_point_2 = MountPoint.objects.create(
            mount_point_name=self.mount_point_name_2,
            total_size_of_the_volume=self.total_size_of_the_volume_2
        )
        token_response = self.client.post('/api/v1/token/', data={
            'username': self.username,
            'password': self.password
        }
                                          )
        self.token = json.loads(token_response.content).get('access')
        self.ip = uuid.uuid4().hex
        self.work_load = WorkLoad.objects.create(
            ip=self.ip,
            credentials=self.credentials_1
        )
        self.work_load.storage.set([self.mount_point_1, self.mount_point_2])
        self.migration_target = MigrationTarget.objects.create(
            cloud_credentials=self.credentials_2
        )
        self.mount_point_name_3 = uuid.uuid4().hex
        self.total_size_of_the_volume_3 = uuid.getnode()
        self.mount_point_3 = MountPoint.objects.create(
            mount_point_name=self.mount_point_name_3,
            total_size_of_the_volume=self.total_size_of_the_volume_3
        )
        self.migration = Migration.objects.create(
            source_of_type=self.work_load,
            migration_target=self.migration_target
        )
        self.migration.selected_mount_points.set([self.mount_point_2])


class CredentialsTest(SetUpTestCase, TestCase):

    def test_credentials(self):
        response_list_credentials_without_token = self.client.get(
            '/api/v1/credentials/',
        )
        self.assertEqual(
            response_list_credentials_without_token.status_code,
            401
        )
        response_list_credentials = self.client.get(
            '/api/v1/credentials/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_list_credentials.status_code, 200)
        self.assertIn(
            bytes(self.domain_1, encoding='UTF-8'),
            response_list_credentials.content
        )
        self.assertIn(
            bytes(self.domain_2, encoding='UTF-8'),
            response_list_credentials.content
        )
        response_credentials = self.client.get(
            '/api/v1/credentials/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(self.domain_1, encoding='UTF-8'),
            response_credentials.content
        )

    def test_create_credentials(self):
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        domain = uuid.uuid4().hex
        response_create_credentials = self.client.post(
            '/api/v1/credentials/',
            data={
                'username': username,
                'password': password,
                'domain': domain
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_create_credentials.status_code, 201)
        response_credentials = self.client.get(
            '/api/v1/credentials/3/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(domain, encoding='UTF-8'),
            response_credentials.content
        )

    def test_update_credentials(self):
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        domain = uuid.uuid4().hex
        response_update_credentials = self.client.patch(
            '/api/v1/credentials/1/',
            data={
                'username': username,
                'password': password,
                'domain': domain
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_update_credentials.status_code, 200)
        response_credentials = self.client.get(
            '/api/v1/credentials/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(domain, encoding='UTF-8'),
            response_credentials.content
        )


class MountPointTest(SetUpTestCase, TestCase):

    def test_mount_point(self):
        response_list_mount_points_without_token = self.client.get(
            '/api/v1/mount_points/',
        )
        self.assertEqual(
            response_list_mount_points_without_token.status_code,
            401
        )
        response_list_mount_points = self.client.get(
            '/api/v1/mount_points/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_list_mount_points.status_code, 200)
        self.assertIn(
            bytes(self.mount_point_name_1, encoding='UTF-8'),
            response_list_mount_points.content
        )
        self.assertIn(
            bytes(self.mount_point_name_2, encoding='UTF-8'),
            response_list_mount_points.content
        )
        response_mount_point = self.client.get(
            '/api/v1/mount_points/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(self.mount_point_name_1, encoding='UTF-8'),
            response_mount_point.content
        )

    def test_create_mount_point(self):
        mount_point_name = uuid.uuid4().hex
        total_size_of_the_volume = uuid.getnode()
        response_create_mount_point = self.client.post(
            '/api/v1/mount_points/',
            data={
                'mount_point_name': mount_point_name,
                'total_size_of_the_volume': total_size_of_the_volume
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_create_mount_point.status_code, 201)
        response_mount_point = self.client.get(
            '/api/v1/mount_points/4/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(mount_point_name, encoding='UTF-8'),
            response_mount_point.content
        )

    def test_update_mount_point(self):
        mount_point_name = uuid.uuid4().hex
        total_size_of_the_volume = uuid.getnode()
        response_update_mount_point = self.client.patch(
            '/api/v1/mount_points/1/',
            data={
                'mount_point_name': mount_point_name,
                'total_size_of_the_volume': total_size_of_the_volume
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_update_mount_point.status_code, 200)
        response_mount_point = self.client.get(
            '/api/v1/mount_points/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(mount_point_name, encoding='UTF-8'),
            response_mount_point.content
        )


class WorkLoadTest(SetUpTestCase, TestCase):

    def test_work_load(self):
        response_list_work_loads_without_token = self.client.get(
            '/api/v1/work_loads/',
        )
        self.assertEqual(
            response_list_work_loads_without_token.status_code,
            401
        )
        response_list_work_loads = self.client.get(
            '/api/v1/work_loads/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_list_work_loads.status_code, 200)
        self.assertIn(
            bytes(self.ip, encoding='UTF-8'),
            response_list_work_loads.content
        )
        response_work_load = self.client.get(
            '/api/v1/work_loads/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(self.ip, encoding='UTF-8'),
            response_work_load.content
        )

    def test_create_work_load(self):
        ip = uuid.uuid4().hex
        response_create_work_load_error_1 = self.client.post(
            '/api/v1/work_loads/',
            data={
                'ip': ip,
                'credentials': 2
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_create_work_load_error_1.status_code, 400)
        self.assertIn(
            bytes('{"storage":["This field is required."]}', encoding='UTF-8'),
            response_create_work_load_error_1.content
        )
        ip = uuid.uuid4().hex
        response_create_work_load_error_2 = self.client.post(
            '/api/v1/work_loads/',
            data={
                'ip': self.ip,
                'credentials': 2,
                'storage': 2
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_create_work_load_error_2.status_code, 400)
        self.assertIn(
            bytes('This field is unique.', encoding='UTF-8'),
            response_create_work_load_error_2.content
        )
        response_create_work_load = self.client.post(
            '/api/v1/work_loads/',
            data={
                'ip': ip,
                'credentials': 2,
                'storage': 2
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_create_work_load.status_code, 201)
        response_work_load = self.client.get(
            '/api/v1/work_loads/2/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(ip, encoding='UTF-8'),
            response_work_load.content
        )


class MigrationTargetTestCase(SetUpTestCase, TestCase):

    def test_migration_target(self):
        response_list_migration_targets_without_token = self.client.get(
            '/api/v1/migration_targets/',
        )
        self.assertEqual(
            response_list_migration_targets_without_token.status_code,
            401
        )
        response_list_migration_targets = self.client.get(
            '/api/v1/migration_targets/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_list_migration_targets.status_code, 200)
        self.assertIn(
            bytes(self.domain_2, encoding='UTF-8'),
            response_list_migration_targets.content
        )
        response_migration_target = self.client.get(
            '/api/v1/migration_targets/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(self.domain_2, encoding='UTF-8'),
            response_migration_target.content
        )

    def test_create_migration_target(self):
        response_create_migration_target = self.client.post(
            '/api/v1/migration_targets/',
            data={
                'cloud_credentials': 1
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_create_migration_target.status_code, 201)
        response_migration_target = self.client.get(
            '/api/v1/migration_targets/2/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(self.domain_1, encoding='UTF-8'),
            response_migration_target.content
        )

    def test_update_migration_target(self):
        response_update_migration_target = self.client.patch(
            '/api/v1/migration_targets/1/',
            data={'cloud_type': 'vcloud'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_update_migration_target.status_code, 200)
        self.assertIn(
            bytes('vcloud', encoding='UTF-8'),
            response_update_migration_target.content
        )
        response_migration_target = self.client.get(
            '/api/v1/migration_targets/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes('vcloud', encoding='UTF-8'),
            response_migration_target.content
        )


class MigrationTestCase(SetUpTestCase, TestCase):

    def test_migration(self):
        response_list_migration_without_token = self.client.get(
            '/api/v1/migrations/',
        )
        self.assertEqual(
            response_list_migration_without_token.status_code,
            401
        )
        response_list_migration = self.client.get(
            '/api/v1/migrations/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_list_migration.status_code, 200)
        self.assertIn(
            bytes('aws', encoding='UTF-8'),
            response_list_migration.content
        )
        response_migration = self.client.get(
            '/api/v1/migrations/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(self.ip, encoding='UTF-8'),
            response_migration.content
        )

    def test_create_migration(self):
        response_create_migration = self.client.post(
            '/api/v1/migrations/',
            data={
                'selected_mount_points': 1,
                'source_of_type': 1,
                'migration_target': 1
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response_create_migration.status_code, 201)
        response_migration = self.client.get(
            '/api/v1/migrations/2/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes('not_started', encoding='UTF-8'),
            response_migration.content
        )


class UpdateMigrationWorkLoadTestCase(SetUpTestCase, APITestCase):

    def setUp(self):
        super().setUp()
        self.client = RequestsClient()

    def test_update_migration(self):
        response_migration = self.client.get(
            'http://testserver/api/v1/migrations/1/',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response_migration.status_code, 200)
        data = {'selected_mount_points': 1}
        query = QueryDict('', mutable=True)
        query.update(data)
        response_update_migration = self.client.patch(
            'http://testserver/api/v1/migrations/1/',
            query,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response_update_migration.status_code, 200)
        self.assertIn(
            bytes(self.mount_point_name_2, encoding='UTF-8'),
            response_update_migration.content
        )

    def test_update_work_load(self):
        ip = uuid.uuid4().hex
        data = {'ip': ip}
        query = QueryDict('', mutable=True)
        query.update(data)
        response_update_work_load_error = self.client.patch(
            'http://testserver/api/v1/work_loads/1/',
            query,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response_update_work_load_error.status_code, 400)
        self.assertIn(
            bytes('''Can't change''', encoding='UTF-8'),
            response_update_work_load_error.content
        )
        data = {'credentials': 2}
        query = QueryDict('', mutable=True)
        query.update(data)
        response_update_work_load = self.client.patch(
            'http://testserver/api/v1/work_loads/1/',
            query,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response_update_work_load.status_code, 200)
        self.assertIn(
            bytes(self.domain_2, encoding='UTF-8'),
            response_update_work_load.content
        )
        response_work_load = self.client.get(
            'http://testserver/api/v1/work_loads/1/',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertIn(
            bytes(self.ip, encoding='UTF-8'),
            response_work_load.content
        )


class RunMigrationTestCase(SetUpTestCase, TestCase):

    def test_run_migration(self):
        response_status_migration_without_token = self.client.get(
            '/api/v1/migrations/1/state/',
        )
        self.assertEqual(
            response_status_migration_without_token.status_code,
            401
        )
        response_run_migration_without_token = self.client.get(
            '/api/v1/migrations/1/run/',
        )
        self.assertEqual(
            response_run_migration_without_token.status_code,
            401
        )
        response_status_migration = self.client.get(
            '/api/v1/migrations/1/state/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(
            response_status_migration.status_code,
            200
        )
        self.assertIn(
            bytes('not_started', encoding='UTF-8'),
            response_status_migration.content
        )
        response_run_migration = self.client.get(
            '/api/v1/migrations/1/run/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(
            response_run_migration.status_code,
            200
        )
        self.assertIn(
            bytes('migration successfully', encoding='UTF-8'),
            response_run_migration.content
        )
        response_status_migration = self.client.get(
            '/api/v1/migrations/1/state/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(
            response_status_migration.status_code,
            200
        )
        self.assertIn(
            bytes('success', encoding='UTF-8'),
            response_status_migration.content
        )
        response_migration_target = self.client.get(
            '/api/v1/migration_targets/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertIn(
            bytes(self.mount_point_name_2, encoding='UTF-8'),
            response_migration_target.content
        )
        self.assertNotIn(
            bytes(self.mount_point_name_1, encoding='UTF-8'),
            response_migration_target.content
        )
        response_run_completed_migration = self.client.get(
            '/api/v1/migrations/1/run/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(
            response_run_completed_migration.status_code,
            400
        )
        self.assertIn(
            bytes('''migration can't run''', encoding='UTF-8'),
            response_run_completed_migration.content
        )

    def test_run_migration_errors(self):
        error_migration = Migration.objects.create(
            source_of_type=self.work_load,
            migration_target=self.migration_target
        )
        error_migration.selected_mount_points.set([self.mount_point_3])
        response_status_error_migration = self.client.get(
            '/api/v1/migrations/2/state/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(
            response_status_error_migration.status_code,
            200
        )
        self.assertIn(
            bytes('not_started', encoding='UTF-8'),
            response_status_error_migration.content
        )
        response_run_migration = self.client.get(
            '/api/v1/migrations/2/run/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(
            response_run_migration.status_code,
            400
        )
        self.assertIn(
            bytes('selected_mount_points not in source', encoding='UTF-8'),
            response_run_migration.content
        )
        response_status_migration = self.client.get(
            '/api/v1/migrations/2/state/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(
            response_status_migration.status_code,
            200
        )
        self.assertIn(
            bytes('error', encoding='UTF-8'),
            response_status_migration.content
        )
        response_migration_target = self.client.get(
            '/api/v1/migration_targets/2/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertNotIn(
            bytes(self.mount_point_name_3, encoding='UTF-8'),
            response_migration_target.content
        )
