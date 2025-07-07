from django.urls import path
from . import views

urlpatterns = [
    path("", views.song_list, name="song_list"),
    path("songs/", views.song_list, name="song_list"),
    path("songs/<str:song_id>/", views.song_detail, name="song_detail"),
    path("artists/", views.artist_list, name="artist_list"),
    path("artists/<str:artist_id>/", views.artist_detail, name="artist_detail"),
    path("search/", views.search, name="search"),
    path("search/results/", views.search_results, name="search_results"),
    path("comments/add/<str:song_id>/", views.add_comment, name="add_comment"),
    path(
        "comments/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"
    ),
]
