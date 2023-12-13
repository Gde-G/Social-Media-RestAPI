from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PasswordRecoveryViewSet, FollowViewSet, BlockViewSet

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'password-recovery', PasswordRecoveryViewSet,
                basename='password-recovery')
router.register(r'follows', FollowViewSet, basename='follows')
router.register(r'block', BlockViewSet, basename='block')

urlpatterns = router.urls
