from django.contrib import admin
from .models import Movie, Genre, UserFavorite


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'tmdb_id']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'release_date', 
        'vote_average', 
        'popularity', 
        'status'
    ]
    list_filter = [
        'status', 
        'release_date', 
        'genres',
        'original_language'
    ]
    search_fields = ['title', 'original_title', 'overview']
    readonly_fields = ['created_at', 'updated_at', 'poster_url', 'backdrop_url']
    filter_horizontal = ['genres']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'original_title', 'overview', 'tagline')
        }),
        ('TMDb Data', {
            'fields': ('tmdb_id', 'imdb_id')
        }),
        ('Release Information', {
            'fields': ('release_date', 'status', 'original_language')
        }),
        ('Media', {
            'fields': ('poster_path', 'poster_url', 'backdrop_path', 'backdrop_url')
        }),
        ('Ratings & Popularity', {
            'fields': ('vote_average', 'vote_count', 'popularity')
        }),
        ('Movie Details', {
            'fields': ('runtime', 'budget', 'revenue', 'genres')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'movie__title']
    raw_id_fields = ['user', 'movie']