from django.contrib import admin
from django.urls import path, include
from .views import RegisterView,UserView, MeView, UpdateDataView, FollowView, UnfollowView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/login',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/register', RegisterView.as_view()),
    path('auth/me',UserView.as_view()),
    path('profile/me',MeView.as_view()),
    path('profile/<int:pk>/follow',FollowView.as_view(),name="profile_follow"),
    path('profile/me',UpdateDataView.as_view(),name="update_profile"),
    path('profile/<int:pk>/unfollow',UnfollowView.as_view(),name="profile_unfollow")
]
