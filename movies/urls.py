from django.urls import path
from . import views

urlpatterns = [
    # Movie endpoints
    path('', views.MovieListView.as_view(), name='movie-list'),
    path('<int:tmdb_id>/', views.MovieDetailView.as_view(), name='movie-detail'),
    
    # Special movie lists
    path('trending/', views.TrendingMoviesView.as_view(), name='trending-movies'),
    path('recommended/', views.RecommendedMoviesView.as_view(), name='recommended-movies'),
    
    # Search
    path('search/', views.movie_search, name='movie-search'),
    
    # User favorites
    path('favorites/', views.UserFavoriteListCreateView.as_view(), name='user-favorites'),
    path('favorites/<int:movie_id>/delete/', views.UserFavoriteDeleteView.as_view(), name='delete-favorite'),
    
    # Genres
    path('genres/', views.GenreListView.as_view(), name='genre-list'),

    # Cache management
    path('cache/stats/', views.cache_stats, name='cache-stats'),
    path('cache/clear/', views.clear_cache, name='clear-cache'),
]