from rest_framework.routers import SimpleRouter
from .views import UserViewSet, PasswordRecoveryViewSet, FollowViewSet, BlockViewSet

router = SimpleRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'password-recovery', PasswordRecoveryViewSet,
                basename='password-recovery')
router.register(r'follows', FollowViewSet, basename='follows')
router.register(r'block', BlockViewSet, basename='block')

urlpatterns = router.urls
