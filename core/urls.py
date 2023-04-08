from django.urls import path
from .views import  add_favorite_planet, add_favorite_movie, get_planet_list, get_movie_list

urlpatterns = [
    path('favourite/movie', add_favorite_movie, name='add_favorite_movie'),
    path('favourite/planet', add_favorite_planet, name='add_favorite_planet'),
    path('movies/', get_movie_list, name='movie-list'),
    path('planets/', get_planet_list, name='planet-list'),
]