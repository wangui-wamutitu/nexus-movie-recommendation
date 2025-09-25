import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_authentication():
    print("Testing Authentication System...")
    
    # Test data
    user_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # 1. Register user
    print("Testing user registration...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        if response.status_code == 201:
            print("User registration successful!")
            register_data = response.json()
            access_token = register_data['tokens']['access']
            print(f"   Username: {register_data['user']['username']}")
            print(f"   User ID: {register_data['user']['id']}")
        else:
            print(f"Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"Registration error: {e}")
        return
    
    # 2. Test login
    print("Testing user login...")
    try:
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            print("Login successful!")
            login_response = response.json()
            access_token = login_response['tokens']['access']
        else:
            print(f"Login failed: {response.text}")
            return
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # 3. Test protected endpoint
    print("Testing protected endpoint (user profile)...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        if response.status_code == 200:
            print("Protected endpoint access successful!")
            profile = response.json()
            print(f"   Profile: {profile['username']} ({profile['email']})")
        else:
            print(f"Protected endpoint failed: {response.text}")
    except Exception as e:
        print(f"Protected endpoint error: {e}")
    
    # 4. Test user stats
    print("Testing user stats...")
    try:
        response = requests.get(f"{BASE_URL}/auth/stats/", headers=headers)
        if response.status_code == 200:
            print("User stats retrieved!")
            stats = response.json()
            print(f"Favorite movies: {stats['stats']['favorite_movies']}")
        else:
            print(f"Stats failed: {response.text}")
    except Exception as e:
        print(f"Stats error: {e}")
    
    # 5. Test favorites (if movies exist)
    print("Testing favorites...")
    try:
        # First get available movies
        movies_response = requests.get(f"{BASE_URL}/movies/")
        if movies_response.status_code == 200:
            movies = movies_response.json()
            if movies.get('results') and len(movies['results']) > 0:
                movie_id = movies['results'][0]['id']
                
                # Add to favorites
                favorite_data = {"movie_id": movie_id}
                response = requests.post(f"{BASE_URL}/movies/favorites/", 
                                       json=favorite_data, headers=headers)
                if response.status_code == 201:
                    print("Added movie to favorites!")
                    
                    # Get favorites list
                    response = requests.get(f"{BASE_URL}/movies/favorites/", headers=headers)
                    if response.status_code == 200:
                        favorites = response.json()
                        print(f"Favorites count: {len(favorites['results']) if 'results' in favorites else len(favorites)}")
                else:
                    print(f"Add to favorites failed: {response.text}")
            else:
                print("No movies available to test favorites")
        else:
            print("Could not fetch movies for favorites test")
    except Exception as e:
        print(f"Favorites test error: {e}")
    
    print("Authentication tests completed!")

if __name__ == "__main__":
    test_authentication()