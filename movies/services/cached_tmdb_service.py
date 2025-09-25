from typing import Dict, Optional
from django.conf import settings
from .tmdb_service import TMDbService
from .cache_service import cache_service
import logging

logger = logging.getLogger(__name__)


class CachedTMDbService(TMDbService):
    """TMDb service with caching layer"""
    
    def __init__(self):
        super().__init__()
        self.cache_ttl = getattr(settings, 'CACHE_TTL', {})
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """Get popular movies with caching"""
        cache_key = cache_service.get_popular_movies_key(page)
        timeout = self.cache_ttl.get('POPULAR_MOVIES', 1800)
        
        return cache_service.get_or_set(
            cache_key,
            super().get_popular_movies,
            timeout,
            page
        )
    
    def get_trending_movies(self, time_window: str = 'week', page: int = 1) -> Optional[Dict]:
        """Get trending movies with caching"""
        cache_key = cache_service.get_trending_movies_key(page)
        timeout = self.cache_ttl.get('TRENDING_MOVIES', 900) 
        
        return cache_service.get_or_set(
            cache_key,
            super().get_trending_movies,
            timeout,
            time_window,
            page
        )
    
    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """Get top rated movies with caching"""
        cache_key = cache_service.get_top_rated_movies_key(page)
        timeout = self.cache_ttl.get('TOP_RATED_MOVIES', 3600) 
        
        return cache_service.get_or_set(
            cache_key,
            super().get_top_rated_movies,
            timeout,
            page
        )
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get movie details with caching"""
        cache_key = cache_service.get_movie_details_key(movie_id)
        timeout = self.cache_ttl.get('MOVIE_DETAILS', 7200) 
        
        return cache_service.get_or_set(
            cache_key,
            super().get_movie_details,
            timeout,
            movie_id
        )
    
    def get_genres(self) -> Optional[Dict]:
        """Get genres with caching (genres rarely change)"""
        cache_key = cache_service.get_genres_key()
        timeout = self.cache_ttl.get('GENRES', 86400) 
        
        return cache_service.get_or_set(
            cache_key,
            super().get_genres,
            timeout
        )
    
    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """Search movies with caching"""
        cache_key = cache_service.get_search_key(query, page)
        timeout = self.cache_ttl.get('SEARCH_RESULTS', 600) 
        
        return cache_service.get_or_set(
            cache_key,
            super().search_movies,
            timeout,
            query,
            page
        )
    
    def get_now_playing_movies(self, page: int = 1) -> Optional[Dict]:
        """Get now playing movies with short cache (changes frequently)"""
        cache_key = cache_service._generate_cache_key('now_playing', page=page)
        timeout = 600  # 10 minutes (shorter because it changes frequently)
        
        return cache_service.get_or_set(
            cache_key,
            super().get_now_playing_movies,
            timeout,
            page
        )
    
    def get_upcoming_movies(self, page: int = 1) -> Optional[Dict]:
        """Get upcoming movies with medium cache"""
        cache_key = cache_service._generate_cache_key('upcoming', page=page)
        timeout = 1800  # 30 minutes
        
        return cache_service.get_or_set(
            cache_key,
            super().get_upcoming_movies,
            timeout,
            page
        )
    
    def discover_movies(self, **kwargs) -> Optional[Dict]:
        """Discover movies with caching"""
        cache_key = cache_service._generate_cache_key('discover', **kwargs)
        timeout = 3600  
        
        return cache_service.get_or_set(
            cache_key,
            super().discover_movies,
            timeout,
            **kwargs
        )
    
    def invalidate_cache(self, movie_id: Optional[int] = None):
        """Invalidate relevant caches"""
        cache_service.invalidate_movie_cache(movie_id)


cached_tmdb_service = CachedTMDbService()