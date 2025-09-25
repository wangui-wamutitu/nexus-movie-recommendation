from movies.services.tmdb_service import tmdb_service

print("Testing TMDb API connection...")

# Test API key
try:
    popular_movies = tmdb_service.get_popular_movies(page=1)
    if popular_movies:
        print("✅ API connection successful!")
        print(f"Found {len(popular_movies.get('results', []))} popular movies")
        
        # Show first movie as example
        first_movie = popular_movies['results'][0]
        print(f"First movie: {first_movie['title']} ({first_movie['release_date']})")
        print(f"Rating: {first_movie['vote_average']}/10")
        
    else:
        print("❌ API connection failed")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test genres
try:
    genres = tmdb_service.get_genres()
    if genres:
        print(f"✅ Found {len(genres.get('genres', []))} genres")
    else:
        print("❌ Failed to fetch genres")
except Exception as e:
    print(f"❌ Error fetching genres: {e}")

print("Test complete!")