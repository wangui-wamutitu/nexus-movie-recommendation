# Movie Recommendation Backend API

A high-performance Django REST API for movie recommendations, featuring TMDb integration, user authentication, favorites management, and Redis caching.

## Features

- **TMDb Integration**: Real movie data from The Movie Database API
- **User Authentication**: JWT-based authentication system
- **Movie Management**: Browse, search, and discover movies
- **User Favorites**: Save and manage favorite movies
- **High Performance**: Redis caching for lightning-fast responses
- **Admin Interface**: Django admin for data management
- **RESTful API**: Clean, well-documented API endpoints

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Caching](#caching)
- [Management Commands](#management-commands)
- [Performance](#performance)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- TMDb API Key ([Get it here](https://www.themoviedb.org/settings/api))

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/wangui-wamutitu/nexus-movie-recommendation.git
cd nexus-movie-recommendation
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  
# On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

#### PostgreSQL (macOS)
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Redis (macOS)
```bash
brew install redis
brew services start redis
```

## ⚙️ Configuration

### 1. Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-django-secret-key-here

# Database Configuration
DATABASE_NAME=movie_recommendation
DATABASE_USER=movie_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# TMDb API
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_BASE_URL=https://api.themoviedb.org/3

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1
```

### 2. Generate Django Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Database Setup

### 1. Create PostgreSQL Database
```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE movie_recommendation;
CREATE USER movie_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE movie_recommendation TO movie_user;
GRANT USAGE ON SCHEMA public TO movie_user;
GRANT CREATE ON SCHEMA public TO movie_user;
ALTER USER movie_user CREATEDB;

# Exit PostgreSQL
\q
```

### 2. Run Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Create Superuser
```bash
python3 manage.py createsuperuser
```

### 4. Populate Movie Data
```bash
# Populate database with movies from TMDb
python3 manage.py populate_movies --pages 5 --categories popular top_rated trending

# Fetch detailed information for movies
python3 manage.py fetch_movie_details --limit 100
```

## API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | User login | No |
| POST | `/api/auth/logout/` | User logout | Yes |
| POST | `/api/auth/token/refresh/` | Refresh JWT token | No |
| GET | `/api/auth/profile/` | Get user profile | Yes |
| PUT | `/api/auth/profile/` | Update user profile | Yes |
| POST | `/api/auth/change-password/` | Change password | Yes |
| GET | `/api/auth/stats/` | User statistics | Yes |

### Movie Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/movies/` | List all movies | No |
| GET | `/api/movies/<tmdb_id>/` | Movie details | No |
| GET | `/api/movies/trending/` | Trending movies | No |
| GET | `/api/movies/recommended/` | Recommended movies | No |
| GET | `/api/movies/search/` | Search movies | No |
| GET | `/api/movies/genres/` | List genres | No |
| GET | `/api/movies/favorites/` | User's favorite movies | Yes |
| POST | `/api/movies/favorites/` | Add movie to favorites | Yes |
| DELETE | `/api/movies/favorites/<id>/delete/` | Remove from favorites | Yes |

### Admin Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/movies/cache/stats/` | Cache statistics | Admin |
| POST | `/api/movies/cache/clear/` | Clear cache | Admin |

## Authentication

The API uses JWT (JSON Web Token) authentication. Here's how to use it:

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "strongpassword123",
    "password_confirm": "strongpassword123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "strongpassword123"
  }'
```

### 3. Use Protected Endpoints
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Add Movie to Favorites
```bash
curl -X POST http://localhost:8000/api/movies/favorites/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 1}'
```

## ⚡ Caching

The application uses Redis for high-performance caching with intelligent cache strategies:

### Cache Configuration
| Data Type | Cache Duration | Reason |
|-----------|---------------|--------|
| Trending Movies | 15 minutes | Changes frequently |
| Popular Movies | 30 minutes | Moderate change rate |
| Top Rated Movies | 1 hour | Stable data |
| Movie Details | 2 hours | Rarely changes |
| Genres | 24 hours | Very stable |
| Search Results | 10 minutes | User-specific, moderate caching |
| User Favorites | 5 minutes | Personal data, changes often |

### Cache Management
```bash
# Warm up cache with popular data
python3 manage.py cache_warm

# Clear all cache
python3 manage.py cache_clear

# Clear specific cache pattern
python3 manage.py cache_clear --pattern "movies:*"
```

### Performance Benefits
- **90%+ faster response times** for cached data
- **Reduced TMDb API calls** (stays within rate limits)
- **Better user experience** with instant responses
- **Scalable architecture** supporting high concurrent users

## Management Commands

### Data Population
```bash
# Populate movies from TMDb
python3 manage.py populate_movies --pages 5 --categories popular top_rated trending

# Fetch detailed movie information
python3 manage.py fetch_movie_details --limit 50
```

### Cache Management
```bash
# Warm up cache
python3 manage.py cache_warm

# Clear cache
python3 manage.py cache_clear

# Clear specific pattern
python3 manage.py cache_clear --pattern "trending_*"
```

## Performance

### API Response Times
- **Without Cache**: ~500ms (database + TMDb API)
- **With Cache**: ~50ms (Redis lookup)
- **Performance Improvement**: 90% faster

### Database Optimizations
- **Select Related**: Reduces database queries for foreign keys
- **Prefetch Related**: Optimizes many-to-many relationships
- **Database Indexing**: Optimized for common queries

### Caching Strategy
- **Multi-level caching**: Database queries + TMDb API responses
- **Smart invalidation**: Automatic cache clearing when data changes
- **User-specific caching**: Separate cache for user favorites

## Project Structure

```
nexus-movie-recommendation/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── movie_backend/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py               # Main configuration
│   ├── urls.py                   # Main URL routing
│   └── wsgi.py
├── movies/                       # Movies app
│   ├── models.py                 # Movie, Genre, UserFavorite models
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API views
│   ├── urls.py                   # Movie URL routing
│   ├── admin.py                  # Django admin configuration
│   ├── services/                 # Business logic
│   │   ├── tmdb_service.py       # TMDb API integration
│   │   ├── cached_tmdb_service.py # Cached TMDb service
│   │   └── cache_service.py      # Cache management
│   └── management/commands/       # Custom management commands
│       ├── populate_movies.py
│       ├── fetch_movie_details.py
│       ├── cache_warm.py
│       └── cache_clear.py
└── users/                        # Users app
    ├── models.py                 # User profile (optional)
    ├── serializers.py            # User serializers
    ├── views.py                  # Authentication views
    └── urls.py                   # Auth URL routing
```

## Testing

### 1. Test Authentication
```bash
python3 test_auth.py
```

### 2. Test Cache Performance
```bash
python3 test_cache.py
```

### 3. Test API Endpoints
```bash
# Test movie endpoints
curl http://localhost:8000/api/movies/
curl http://localhost:8000/api/movies/trending/
curl http://localhost:8000/api/movies/search/?q=batman

# Test authentication
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "testpass123", "password_confirm": "testpass123"}'
```

## Deployment

### Environment Setup
1. Set `DEBUG=False` in production
2. Configure production database
3. Set up Redis server
4. Configure web server (gunicorn)
5. Set up SSL certificates

### Production Settings
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://redis-server:6379/0
```
Currently hosted at: https://nexus-movie-recommendation.onrender.com/swagger/

## Key Features Implemented

### Database & Models
- PostgreSQL database with optimized models
- Movie, Genre, and UserFavorite relationships
- Database migrations and admin interface

### TMDb Integration
- Complete TMDb API integration
- Automatic data population from TMDb
- Error handling and rate limiting

### Authentication System
- JWT-based authentication
- User registration and login
- Password management and user profiles
- Protected endpoints for user-specific data

### Caching System
- Redis integration for high performance
- Intelligent cache strategies by data type
- Cache warming and invalidation
- Performance monitoring and management

### API Endpoints
- RESTful API design
- Movie browsing, searching, and filtering
- User favorites management
- Admin cache management endpoints

### Performance Optimizations
- Database query optimization
- Multi-level caching strategy
- Efficient serialization
- 90%+ performance improvement

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License

## Acknowledgments

- [The Movie Database (TMDb)](https://www.themoviedb.org/) for providing the movie data API
- [Django](https://www.djangoproject.com/) for the web framework
- [Django REST Framework](https://www.django-rest-framework.org/) for API functionality
- [Redis](https://redis.io/) for caching infrastructure

## Support

If you have any questions or need help with setup, please open an issue in the repository.

---

**Built with ❤️ using Django, PostgreSQL, Redis, and TMDb API**