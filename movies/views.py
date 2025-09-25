from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.cache import cache
from .models import Movie, Genre, UserFavorite
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    UserFavoriteSerializer,
    GenreSerializer,
)
from .services.cache_service import cache_service


class MovieListView(generics.ListAPIView):
    """List all movies with pagination"""

    queryset = Movie.objects.all()
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Movie.objects.all()

        # Filter by genre
        genre = self.request.query_params.get("genre")
        if genre:
            queryset = queryset.filter(genres__name__icontains=genre)

        # Filter by year
        year = self.request.query_params.get("year")
        if year:
            queryset = queryset.filter(release_date__year=year)

        # Search by title
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(original_title__icontains=search)
                | Q(overview__icontains=search)
            )

        return queryset


class MovieDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific movie"""

    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "tmdb_id"


class TrendingMoviesView(generics.ListAPIView):
    """Get trending movies (ordered by popularity)"""

    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Movie.objects.filter(status="released").order_by("-popularity")[:20]


class RecommendedMoviesView(generics.ListAPIView):
    """Get recommended movies (highly rated recent movies)"""

    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        from datetime import date, timedelta

        # Movies from last 2 years with high ratings
        two_years_ago = date.today() - timedelta(days=730)

        return Movie.objects.filter(
            status="released",
            release_date__gte=two_years_ago,
            vote_average__gte=7.0,
            vote_count__gte=100,
        ).order_by("-vote_average", "-popularity")[:20]


class UserFavoriteListCreateView(generics.ListCreateAPIView):
    """List user's favorite movies and add new favorites"""

    serializer_class = UserFavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).select_related(
            "movie"
        )

    def perform_create(self, serializer):
        # Check if movie exists
        movie_id = serializer.validated_data.get("movie_id")
        try:
            movie = Movie.objects.get(id=movie_id)
            serializer.save(user=self.request.user, movie=movie)
        except Movie.DoesNotExist:
            raise ValidationError({"movie_id": "Movie not found"})

    def create(self, request, *args, **kwargs):
        # Check if user already has this movie as favorite
        movie_id = request.data.get("movie_id")
        if UserFavorite.objects.filter(user=request.user, movie_id=movie_id).exists():
            return Response(
                {"error": "Movie is already in favorites"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class UserFavoriteDeleteView(generics.DestroyAPIView):
    """Remove a movie from user's favorites"""

    permission_classes = [IsAuthenticated]

    def get_object(self):
        movie_id = self.kwargs.get("movie_id")
        return get_object_or_404(
            UserFavorite, user=self.request.user, movie_id=movie_id
        )


class GenreListView(generics.ListAPIView):
    """List all available genres"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


@api_view(["GET"])
@permission_classes([AllowAny])
def movie_search(request):
    """Search movies by title, genre, or year"""
    query = request.GET.get("q", "")
    genre = request.GET.get("genre", "")
    year = request.GET.get("year", "")

    if not any([query, genre, year]):
        return Response(
            {
                "error": "Please provide at least one search parameter (q, genre, or year)"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    movies = Movie.objects.all()

    if query:
        movies = movies.filter(
            Q(title__icontains=query)
            | Q(original_title__icontains=query)
            | Q(overview__icontains=query)
        )

    if genre:
        movies = movies.filter(genres__name__icontains=genre)

    if year:
        movies = movies.filter(release_date__year=year)

    movies = movies.distinct()[:50]  # Limit results
    serializer = MovieListSerializer(movies, many=True)

    return Response({"count": movies.count(), "results": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def cache_stats(request):
    """Get cache statistics (admin only)"""
    try:
        from django_redis import get_redis_connection

        redis_conn = get_redis_connection("default")
        info = redis_conn.info()

        stats = {
            "redis_version": info.get("redis_version"),
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_connections_received": info.get("total_connections_received"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "uptime_in_seconds": info.get("uptime_in_seconds"),
        }

        # Calculate hit rate
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0

        stats["hit_rate_percentage"] = round(hit_rate, 2)

        return Response({"cache_enabled": True, "stats": stats})

    except Exception as e:
        return Response(
            {"cache_enabled": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def clear_cache(request):
    """Clear cache (admin only)"""
    pattern = request.data.get("pattern")

    try:
        if pattern:
            cache.delete_pattern(pattern)
            message = f"Cleared cache pattern: {pattern}"
        else:
            cache.clear()
            message = "Cleared all cache"

        return Response({"message": message})

    except Exception as e:
        return Response(
            {"error": f"Failed to clear cache: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
