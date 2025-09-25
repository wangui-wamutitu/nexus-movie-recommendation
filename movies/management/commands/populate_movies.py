from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Movie, Genre
from movies.services.tmdb_service import tmdb_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate database with movies from TMDb API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=5,
            help='Number of pages to fetch from each category'
        )
        parser.add_argument(
            '--categories',
            nargs='+',
            default=['popular', 'top_rated', 'trending'],
            help='Categories to fetch: popular, top_rated, trending, now_playing, upcoming'
        )

    def handle(self, *args, **options):
        pages = options['pages']
        categories = options['categories']
        
        self.stdout.write(self.style.SUCCESS('Starting movie data population...'))
        
        # First, populate genres
        self.populate_genres()
        
        # Then populate movies from different categories
        total_movies = 0
        
        for category in categories:
            self.stdout.write(f'Fetching {category} movies...')
            movies_added = self.populate_movies_by_category(category, pages)
            total_movies += movies_added
            self.stdout.write(
                self.style.SUCCESS(f'Added {movies_added} movies from {category}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated {total_movies} movies!')
        )

    def populate_genres(self):
        """Populate genres from TMDb"""
        self.stdout.write('Fetching genres...')
        
        genres_data = tmdb_service.get_genres()
        if not genres_data:
            self.stdout.write(self.style.ERROR('Failed to fetch genres'))
            return
        
        genres_created = 0
        for genre_data in genres_data.get('genres', []):
            genre, created = Genre.objects.get_or_create(
                tmdb_id=genre_data['id'],
                defaults={'name': genre_data['name']}
            )
            if created:
                genres_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {genres_created} new genres')
        )

    def populate_movies_by_category(self, category: str, pages: int) -> int:
        """Populate movies from a specific category"""
        movies_added = 0
        
        for page in range(1, pages + 1):
            # Fetch data based on category
            if category == 'popular':
                data = tmdb_service.get_popular_movies(page)
            elif category == 'top_rated':
                data = tmdb_service.get_top_rated_movies(page)
            elif category == 'trending':
                data = tmdb_service.get_trending_movies('week', page)
            elif category == 'now_playing':
                data = tmdb_service.get_now_playing_movies(page)
            elif category == 'upcoming':
                data = tmdb_service.get_upcoming_movies(page)
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unknown category: {category}')
                )
                continue
            
            if not data:
                self.stdout.write(
                    self.style.ERROR(f'Failed to fetch {category} page {page}')
                )
                continue
            
            # Process each movie in the results
            for movie_data in data.get('results', []):
                try:
                    movie_created = self.create_or_update_movie(movie_data)
                    if movie_created:
                        movies_added += 1
                except Exception as e:
                    logger.error(f'Error processing movie {movie_data.get("id")}: {e}')
                    continue
        
        return movies_added

    @transaction.atomic
    def create_or_update_movie(self, movie_data: dict) -> bool:
        """Create or update a movie from TMDb data"""
        tmdb_id = movie_data.get('id')
        if not tmdb_id:
            return False
        
        # Parse release date
        release_date = None
        if movie_data.get('release_date'):
            try:
                release_date = datetime.strptime(
                    movie_data['release_date'], '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # Create or update movie
        movie, created = Movie.objects.get_or_create(
            tmdb_id=tmdb_id,
            defaults={
                'title': movie_data.get('title', ''),
                'original_title': movie_data.get('original_title', ''),
                'overview': movie_data.get('overview', ''),
                'release_date': release_date,
                'poster_path': movie_data.get('poster_path', ''),
                'backdrop_path': movie_data.get('backdrop_path', ''),
                'vote_average': movie_data.get('vote_average', 0.0),
                'vote_count': movie_data.get('vote_count', 0),
                'popularity': movie_data.get('popularity', 0.0),
                'original_language': movie_data.get('original_language', 'en'),
            }
        )
        
        # Update existing movie if not created
        if not created:
            movie.title = movie_data.get('title', movie.title)
            movie.original_title = movie_data.get('original_title', movie.original_title)
            movie.overview = movie_data.get('overview', movie.overview)
            movie.release_date = release_date or movie.release_date
            movie.poster_path = movie_data.get('poster_path', movie.poster_path)
            movie.backdrop_path = movie_data.get('backdrop_path', movie.backdrop_path)
            movie.vote_average = movie_data.get('vote_average', movie.vote_average)
            movie.vote_count = movie_data.get('vote_count', movie.vote_count)
            movie.popularity = movie_data.get('popularity', movie.popularity)
            movie.original_language = movie_data.get('original_language', movie.original_language)
            movie.save()
        
        # Add genres
        genre_ids = movie_data.get('genre_ids', [])
        if genre_ids:
            genres = Genre.objects.filter(tmdb_id__in=genre_ids)
            movie.genres.set(genres)
        
        return created