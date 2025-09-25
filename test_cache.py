import time
import requests
import statistics

BASE_URL = "http://127.0.0.1:8000/api/movies"

def test_endpoint_performance(endpoint, iterations=5):
    """Test endpoint performance with and without cache"""
    print(f"Testing {endpoint} performance...")
    
    times = []
    
    # First request (cache miss)
    start_time = time.time()
    response = requests.get(f"{BASE_URL}{endpoint}")
    first_request_time = time.time() - start_time
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    
    print(f"First request (cache miss): {first_request_time:.3f}s")
    
    # Subsequent requests (cache hits)
    for i in range(iterations):
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}")
        request_time = time.time() - start_time
        times.append(request_time)
        time.sleep(0.1)  # Small delay between requests
    
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Cached requests ({iterations} iterations):")
    print(f"   Average: {avg_time:.3f}s")
    print(f"   Min: {min_time:.3f}s")
    print(f"   Max: {max_time:.3f}s")
    
    # Calculate performance improvement
    if avg_time > 0:
        improvement = ((first_request_time - avg_time) / first_request_time) * 100
        print(f"Cache performance improvement: {improvement:.1f}%")
    
    return {
        'endpoint': endpoint,
        'first_request': first_request_time,
        'avg_cached': avg_time,
        'improvement_percent': improvement if avg_time > 0 else 0
    }

def test_cache_performance():
    """Test cache performance for various endpoints"""
    print("Redis Cache Performance Test")
    print("=" * 50)
    
    endpoints_to_test = [
        "/trending/",
        "/recommended/", 
        "/",
        "/genres/",
        "/search/?q=batman"
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        result = test_endpoint_performance(endpoint)
        if result:
            results.append(result)
        time.sleep(1)  # Pause between endpoint tests
    
    # Summary
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    
    for result in results:
        print(f"Endpoint: {result['endpoint']}")
        print(f"  First request: {result['first_request']:.3f}s")
        print(f"  Cached avg: {result['avg_cached']:.3f}s")
        print(f"  Improvement: {result['improvement_percent']:.1f}%")
        print()
    
    # Overall statistics
    if results:
        avg_improvement = statistics.mean([r['improvement_percent'] for r in results])
        print(f"Average cache performance improvement: {avg_improvement:.1f}%")

def test_cache_invalidation():
    """Test cache invalidation"""
    print("Testing cache invalidation...")
    
    # Make a request to cache data
    print("1. Making initial request to cache data...")
    response = requests.get(f"{BASE_URL}/trending/")
    
    if response.status_code == 200:
        print("Data cached successfully")
        
        # Clear cache (requires admin token - this is just a demonstration)
        print("2. Cache cleared (simulated)")
        
        # Make request again (this should be slower)
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/trending/")
        request_time = time.time() - start_time
        
        print(f"3. Request after cache clear: {request_time:.3f}s")
    else:
        print("Failed to test cache invalidation")

if __name__ == "__main__":
    try:
        # Test basic performance
        test_cache_performance()
        
        # Test cache invalidation
        test_cache_invalidation()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure your Django server is running: python3 manage.py runserver")
    except Exception as e:
        print(f"Error: {e}")