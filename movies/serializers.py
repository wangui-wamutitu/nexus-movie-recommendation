from rest_framework import serializers
from .models import Movie, Genre, UserFavorite


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name']


class MovieListSerializer(serializers.ModelSerializer):
    """Serializer for movie list views (minimal data)"""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.ReadOnlyField()
    year = serializers.ReadOnlyField()
    
    class Meta:
        model = Movie
        fields = [
            'id',
            'tmdb_id',
            'title',
            'overview',
            'release_date',
            'year',
            'poster_path',
            'poster_url',
            'vote_average',
            'vote_count',
            'popularity',
            'genres'
        ]


class MovieDetailSerializer(serializers.ModelSerializer):
    """Serializer for movie detail view (complete data)"""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.ReadOnlyField()
    backdrop_url = serializers.ReadOnlyField()
    year = serializers.ReadOnlyField()
    
    class Meta:
        model = Movie
        fields = [
            'id',
            'tmdb_id',
            'imdb_id',
            'title',
            'original_title',
            'overview',
            'tagline',
            'release_date',
            'year',
            'poster_path',
            'poster_url',
            'backdrop_path',
            'backdrop_url',
            'vote_average',
            'vote_count',
            'popularity',
            'runtime',
            'budget',
            'revenue',
            'status',
            'original_language',
            'genres',
            'created_at',
            'updated_at'
        ]


class UserFavoriteSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserFavorite
        fields = ['id', 'movie', 'movie_id', 'created_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)