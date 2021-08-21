from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import FollowUserViewSet, FollowViewSet
from djoser import views

app_name = 'users'

router = DefaultRouter()
router.register("users/subscriptions", FollowViewSet)
router.register("users", FollowUserViewSet)
# router.register('subscriptions', FollowViewSet, basename='follow') 


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
] + router.urls

