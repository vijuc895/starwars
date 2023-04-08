import requests
from django.db import models

# Create your models here.
from django.db import models


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Movies(BaseModel):
    title = models.CharField(max_length=255, db_index=True)
    release_date = models.DateField()
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Planets(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FavoriteMovies(BaseModel):
    user_id = models.BigIntegerField()
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    custom_title = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'movie'], name='favorite_movie_pk'),
        ]


class FavoritePlanets(BaseModel):
    user_id = models.BigIntegerField()
    planet = models.ForeignKey(Planets, on_delete=models.CASCADE)
    custom_name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'planet'], name='favorite_planet_pk'),
        ]
