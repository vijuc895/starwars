from django.contrib import admin

from core.models import Movies, Planets, FavoriteMovies, FavoritePlanets

# Register your models here.
admin.site.register(Movies)
admin.site.register(Planets)
admin.site.register(FavoriteMovies)
admin.site.register(FavoritePlanets)