from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)


from .views import (CredentialsViewSet, MountPointViewSet, WorkLoadViewSet,
                    MigrationTargetViewSet, MigrationViewSet, UserViewSet,
                    run_migration, get_migration_state)


router = DefaultRouter()
router.register(r'credentials', CredentialsViewSet)
router.register(r'mount_points', MountPointViewSet)
router.register(r'work_loads', WorkLoadViewSet)
router.register(r'migration_targets', MigrationTargetViewSet)
router.register(r'migrations', MigrationViewSet)


urlpatterns = [
    path('v1/migrations/<int:migration_id>/run/', run_migration),
    path('v1/migrations/<int:migration_id>/state/', get_migration_state),
    path('v1/', include(router.urls)),
    path('v1/auth/', UserViewSet.as_view({'post': 'create'})),
    path(
        'v1/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    path(
        'v1/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    )
]
