import json
import hashlib
from typing import Any, Optional
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Service for managing cache operations"""
    
    def __init__(self):
        self.cache_ttl = getattr(settings, 'CACHE_TTL', {})
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a unique cache key based on prefix and parameters"""
        # Create a hash of the parameters for a consistent key
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{params_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            cache.set(key, value, timeout)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def get_or_set(self, key: str, func, timeout: Optional[int] = None, *args, **kwargs) -> Any:
        """Get from cache or execute function and cache the result"""
        try:
            # Try to get from cache first
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.info(f"Cache hit for key: {key}")
                return cached_value
            
            # Cache miss - execute function
            logger.info(f"Cache miss for key: {key}")
            value = func(*args, **kwargs)
            
            # Cache the result
            if value is not None:
                cache.set(key, value, timeout)
                logger.info(f"Cached result for key: {key}")
            
            return value
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            # If cache fails, just execute the function
            return func(*args, **kwargs)
    
    # Movie-specific cache methods
    def get_trending_movies_key(self, page: int = 1) -> str:
        """Generate cache key for trending movies"""
        return self._generate_cache_key('trending_movies', page=page)
    
    def get_popular_movies_key(self, page: int = 1) -> str:
        """Generate cache key for popular movies"""
        return self._generate_cache_key('popular_movies', page=page)
    
    def get_top_rated_movies_key(self, page: int = 1) -> str:
        """Generate cache key for top rated movies"""
        return self._generate_cache_key('top_rated_movies', page=page)
    
    def get_movie_details_key(self, movie_id: int) -> str:
        """Generate cache key for movie details"""
        return self._generate_cache_key('movie_details', movie_id=movie_id)
    
    def get_genres_key(self) -> str:
        """Generate cache key for genres"""
        return 'genres:all'
    
    def get_search_key(self, query: str, page: int = 1) -> str:
        """Generate cache key for search results"""
        return self._generate_cache_key('search', query=query.lower(), page=page)
    
    def get_user_favorites_key(self, user_id: int) -> str:
        """Generate cache key for user favorites"""
        return f"user_favorites:{user_id}"
    
    def get_movie_recommendations_key(self, **filters) -> str:
        """Generate cache key for movie recommendations"""
        return self._generate_cache_key('recommendations', **filters)
    
    # Cache invalidation methods
    def invalidate_movie_cache(self, movie_id: Optional[int] = None):
        """Invalidate movie-related cache"""
        patterns_to_delete = [
            'trending_movies:*',
            'popular_movies:*',
            'top_rated_movies:*',
            'search:*',
            'recommendations:*'
        ]
        
        if movie_id:
            patterns_to_delete.append(f'movie_details:{movie_id}:*')
        
        for pattern in patterns_to_delete:
            try:
                cache.delete_pattern(pattern)
            except Exception as e:
                logger.error(f"Error deleting cache pattern {pattern}: {e}")
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate user-specific cache"""
        try:
            cache.delete_pattern(f'user_favorites:{user_id}')
        except Exception as e:
            logger.error(f"Error deleting user cache for {user_id}: {e}")
    
    # Cache warming methods
    def warm_popular_caches(self):
        """Pre-warm popular caches"""
        from .tmdb_service import tmdb_service
        
        try:
            # Warm trending movies cache
            trending_key = self.get_trending_movies_key(1)
            trending_timeout = self.cache_ttl.get('TRENDING_MOVIES', 900) 
            
            self.get_or_set(
                trending_key,
                tmdb_service.get_trending_movies,
                trending_timeout,
                'week', 1
            )
            
            # Warm popular movies cache
            popular_key = self.get_popular_movies_key(1)
            popular_timeout = self.cache_ttl.get('POPULAR_MOVIES', 1800) 
            
            self.get_or_set(
                popular_key,
                tmdb_service.get_popular_movies,
                popular_timeout,
                1
            )
            
            logger.info("Cache warming completed successfully")
            
        except Exception as e:
            logger.error(f"Cache warming error: {e}")

cache_service = CacheService()