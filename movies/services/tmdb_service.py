import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TMDbService:
    """Service class for interacting with The Movie Database (TMDb) API"""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = getattr(settings, 'TMDB_BASE_URL', 'https://api.themoviedb.org/3')
        self.image_base_url = 'https://image.tmdb.org/t/p/'
        
        if not self.api_key:
            raise ValueError("TMDb API key not found in settings")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to TMDb API with error handling"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """Get popular movies from TMDb"""
        return self._make_request('movie/popular', {'page': page})
    
    def get_trending_movies(self, time_window: str = 'week', page: int = 1) -> Optional[Dict]:
        """Get trending movies (day or week)"""
        return self._make_request(f'trending/movie/{time_window}', {'page': page})
    
    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """Get top rated movies"""
        return self._make_request('movie/top_rated', {'page': page})
    
    def get_now_playing_movies(self, page: int = 1) -> Optional[Dict]:
        """Get movies now playing in theaters"""
        return self._make_request('movie/now_playing', {'page': page})
    
    def get_upcoming_movies(self, page: int = 1) -> Optional[Dict]:
        """Get upcoming movies"""
        return self._make_request('movie/upcoming', {'page': page})
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information about a specific movie"""
        return self._make_request(f'movie/{movie_id}')
    
    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """Search for movies by title"""
        return self._make_request('search/movie', {
            'query': query,
            'page': page,
            'include_adult': False
        })
    
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """Get movie recommendations based on a specific movie"""
        return self._make_request(f'movie/{movie_id}/recommendations', {'page': page})
    
    def get_similar_movies(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """Get movies similar to a specific movie"""
        return self._make_request(f'movie/{movie_id}/similar', {'page': page})
    
    def get_genres(self) -> Optional[Dict]:
        """Get list of official genres for movies"""
        return self._make_request('genre/movie/list')
    
    def discover_movies(self, **kwargs) -> Optional[Dict]:
        """
        Discover movies with various filters
        
        Available filters:
        - with_genres: Genre IDs separated by comma
        - primary_release_year: Year
        - vote_average.gte: Minimum rating
        - vote_count.gte: Minimum vote count
        - sort_by: popularity.desc, release_date.desc, etc.
        """
        params = {k: v for k, v in kwargs.items() if v is not None}
        return self._make_request('discover/movie', params)
    
    def get_poster_url(self, poster_path: str, size: str = 'w500') -> str:
        """Generate full poster URL"""
        if not poster_path:
            return None
        return f"{self.image_base_url}{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: str, size: str = 'w1280') -> str:
        """Generate full backdrop URL"""
        if not backdrop_path:
            return None
        return f"{self.image_base_url}{size}{backdrop_path}"


tmdb_service = TMDbService()