from django.core.management.base import BaseCommand
from movies.services.cache_service import cache_service


class Command(BaseCommand):
    help = "Warm up the cache with popular movie data"

    def handle(self, *args, **options):
        self.stdout.write("Warming up cache...")

        try:
            cache_service.warm_popular_caches()
            self.stdout.write(
                self.style.SUCCESS("Cache warming completed successfully!")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Cache warming failed: {e}"))
