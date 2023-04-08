from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.utils import json

from .models import Movies, FavoriteMovies, Planets, FavoritePlanets


class FavoriteMoviesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_id = 1
        self.movie_title = 'The Main'
        self.custom_title = 'My Custom Title'

        # Create a test movie
        self.movie = Movies.objects.create(
            title=self.movie_title,
            release_date='2001-01-05',
            created_at='2023-01-01',
            updated_at='2023-01-01',
            url='https://swapi.dev/api/films/1/',
        )
        self.url = reverse('add_favorite_movie')

    def test_add_favorite_movie_success(self):
        data = {'title': self.movie_title, 'user_id': self.user_id, 'custom_title': self.custom_title}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'Movie added as favorite')

        # Check if favorite movie is created in the database
        favorite_movie = FavoriteMovies.objects.get(user_id=self.user_id, movie=self.movie)
        self.assertEqual(favorite_movie.custom_title, self.custom_title)

    def test_add_favorite_movie_missing_data(self):
        data = {'user_id': self.user_id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Missing required data')

    def test_add_favorite_movie_movie_not_found(self):
        data = {'title': 'Not Found', 'user_id': self.user_id, 'custom_title': self.custom_title}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Movie not found')

    def test_add_favorite_movie_already_added(self):
        # Create a favorite movie for the user
        FavoriteMovies.objects.create(user_id=self.user_id, movie=self.movie, custom_title=self.custom_title)

        data = {'title': self.movie_title, 'user_id': self.user_id, 'custom_title': self.custom_title}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Movie already added as favorite')


class AddFavoritePlanetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_id = 1
        self.planet_name = 'Earth'
        self.custom_name = 'Home'

        # Create a test planet
        self.planet = Planets.objects.create(
            name=self.planet_name,
            created_at='2023-01-01',
            updated_at='2023-01-01',
            url='https://swapi.dev/api/planets/1/',
        )
        self.url = reverse('add_favorite_planet')

    def test_add_favorite_planet(self):
        data = {'name': self.planet_name, 'user_id': self.user_id, 'custom_name': self.custom_name}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'Planet added as favorite')

        # Check if favorite planet is created in the database
        favorite_planet = FavoritePlanets.objects.get(user_id=self.user_id, planet=self.planet)
        self.assertEqual(favorite_planet.custom_name, self.custom_name)

    def test_add_favorite_planet_with_missing_data(self):
        data = {'name': 'Test Planet'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Missing required data')

    def test_add_favorite_planet_not_found(self):
        data = {'name': 'Non-existent Planet', 'user_id': 1}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Planet not found')

    def test_add_favorite_planet_already_added(self):
        # Create a favorite movie for the user
        FavoritePlanets.objects.create(user_id=self.user_id, planet=self.planet, custom_name=self.custom_name)

        data = {'name': self.planet_name, 'user_id': self.user_id, 'custom_name': self.custom_name}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Planet already added as favorite')


class GetPlanetListTestCase(TestCase):
    def setUp(self):
        self.user_id = 1
        self.planet1 = Planets.objects.create(name='Earth', created_at='2022-01-01', updated_at='2022-01-02', url='http://localhost:8000/planets/1')
        self.planet2 = Planets.objects.create(name='Mars', created_at='2022-01-03', updated_at='2022-01-04', url='http://localhost:8000/planets/2')
        self.fav_planet = FavoritePlanets.objects.create(user_id=self.user_id, planet_id=self.planet1.id, custom_name='My Earth')

    def test_get_planet_list(self):
        url = reverse('planet-list')
        response = self.client.get(url, {'user_id': self.user_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), 2)

    def test_get_planet_list_with_query(self):
        url = reverse('planet-list')
        response = self.client.get(url, {'user_id': self.user_id, 'search_by': 'Mars'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), 1)
        self.assertEqual(content['results'][0]['name'], 'Mars')
        self.assertEqual(content['results'][0]['url'], 'http://localhost:8000/planets/2')
        self.assertEqual(content['results'][0]['is_favourite'], False)


class GetMovieListTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.movie1 = Movies.objects.create(title='Inception', release_date='2010-07-16', url='http://localhost:8000/movies/1')
        self.movie2 = Movies.objects.create(title='The Dark Knight', release_date='2008-07-18', url='http://localhost:8000/movies/2')
        self.fav_movie = FavoriteMovies.objects.create(user_id=1, movie_id=self.movie1.id, custom_title='My Inception')

    def test_get_movie_list(self):
        url = reverse('movie-list')
        response = self.client.get(url, {'user_id': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), 2)

    def test_get_movie_list_with_search_query(self):
        url = reverse('movie-list')
        response = self.client.get(url, {'user_id': 1, 'search_by': 'Inception'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), 1)
        self.assertEqual(content['results'][0]['title'], 'My Inception')
        self.assertEqual(content['results'][0]['release_date'], '2010-07-16')
        self.assertEqual(content['results'][0]['is_favourite'], True)
