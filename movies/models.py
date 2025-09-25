from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """Model for movie genres"""

    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    """Model for movies from TMDb API"""

    tmdb_id = models.IntegerField(unique=True, db_index=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True)

    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    overview = models.TextField(blank=True)
    tagline = models.CharField(max_length=255, blank=True)

    release_date = models.DateField(null=True, blank=True)

    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)

    vote_average = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0.0
    )
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0.0)

    runtime = models.IntegerField(null=True, blank=True)  # in minutes
    budget = models.BigIntegerField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)

    STATUS_CHOICES = [
        ("rumored", "Rumored"),
        ("planned", "Planned"),
        ("in_production", "In Production"),
        ("post_production", "Post Production"),
        ("released", "Released"),
        ("canceled", "Canceled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="released")

    original_language = models.CharField(max_length=10, default="en")

    genres = models.ManyToManyField(Genre, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-popularity", "-release_date"]
        indexes = [
            models.Index(fields=["tmdb_id"]),
            models.Index(fields=["release_date"]),
            models.Index(fields=["popularity"]),
            models.Index(fields=["vote_average"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'Unknown'})"

    @property
    def poster_url(self):
        """Return full poster URL"""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def backdrop_url(self):
        """Return full backdrop URL"""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return None

    @property
    def year(self):
        """Return release year"""
        return self.release_date.year if self.release_date else None


class UserFavorite(models.Model):
    """Model for user's favorite movies"""

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
