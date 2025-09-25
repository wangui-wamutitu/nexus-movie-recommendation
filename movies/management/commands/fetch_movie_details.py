from django.core.management.base import BaseCommand
from movies.models import Movie
from movies.services.tmdb_service import tmdb_service
import time


class Command(BaseCommand):
    help = 'Fetch detailed information for existing movies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit number of movies to update'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        
        # Get movies that don't have detailed info (missing runtime, budget, etc.)
        movies = Movie.objects.filter(runtime__isnull=True)[:limit]
        
        self.stdout.write(f'Updating details for {len(movies)} movies...')
        
        updated_count = 0
        
        for movie in movies:
            try:
                # Fetch detailed movie data
                details = tmdb_service.get_movie_details(movie.tmdb_id)
                
                if details:
                    # Update movie with detailed information
                    movie.runtime = details.get('runtime')
                    movie.budget = details.get('budget', 0) or None
                    movie.revenue = details.get('revenue', 0) or None
                    movie.imdb_id = details.get('imdb_id', '')
                    movie.tagline = details.get('tagline', '')
                    movie.status = self.map_status(details.get('status', ''))
                    
                    movie.save()
                    updated_count += 1
                    
                    self.stdout.write(f'Updated: {movie.title}')
                
                # Be nice to the API - small delay
                time.sleep(0.25)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating {movie.title}: {e}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated_count} movies with detailed info')
        )
    
    def map_status(self, tmdb_status: str) -> str:
        """Map TMDb status to our model choices"""
        status_mapping = {
            'Released': 'released',
            'Post Production': 'post_production',
            'In Production': 'in_production',
            'Planned': 'planned',
            'Rumored': 'rumored',
            'Canceled': 'canceled',
        }
        return status_mapping.get(tmdb_status, 'released')