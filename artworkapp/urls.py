from django.contrib import admin
from django.urls import path, include
from .views import ArtworkView,SaveArt,TagView, BlockchainView,LikeArt,FeedView,GetArtworkView
urlpatterns = [
    path('upload',ArtworkView.as_view()),
    path('gallery',ArtworkView.as_view()),
    path('uploads/presign',BlockchainView.as_view()),
    path('art/status/<int:pk>',BlockchainView.as_view()),
    path('art/<int:pk>',GetArtworkView.as_view(),name='artworks_art_read'),
    path('art/<int:pk>/likes',LikeArt.as_view()),
    path('art/<int:pk>/saves',SaveArt.as_view()),
    path('tags',TagView.as_view()),
    path('feed',FeedView.as_view())
]
