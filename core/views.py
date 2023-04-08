from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, When
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Movies, Planets, FavoriteMovies, FavoritePlanets
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from django.db import models

from starwars.logger import Logger


logger = Logger()


@api_view(['POST'])
def add_favorite_movie(request):
    """
        Add a movie as a favorite for a user.

        Required request parameters:
        - title: the title of the movie to add as a favorite
        - user_id: the ID of the user adding the movie as a favorite

        Optional request parameters:
        - custom_title: a custom title for the favorite movie

        Returns a JSON response with either an error message or a success message, along with the ID of the created
        FavoriteMovies object.

        HTTP status codes:
        - 201 Created: the movie was successfully added as a favorite
        - 400 Bad Request: required data is missing from the request
        - 404 Not Found: the movie with the given title could not be found
        - 200 OK: the movie was already added as a favorite
    """
    movie_title = request.data.get('title')
    user_id = request.data.get('user_id')
    custom_title = request.data.get('custom_title')

    logger.info(msg='adding {} movie as fav movie for user: {}'.format(movie_title, user_id))

    # Check if required data is present in request
    if not movie_title or not user_id:
        logger.error(msg='Missing required data: {} and {}'.format(movie_title, user_id))
        return Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if movie with given title exists
    try:
        movie = Movies.objects.get(title__iexact=movie_title)
    except ObjectDoesNotExist:
        logger.error(msg='Movie not found, movie title: {}'.format(movie_title))
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create favorite movie object
    favorite_movie, is_created = FavoriteMovies.objects.get_or_create(
        user_id=user_id,
        movie=movie,
        defaults={'custom_title': custom_title},
    )

    if not is_created:
        logger.warn(msg='Movie already added as favorite, movie title: {}'.format(movie_title))
        return Response({'success': 'Movie already added as favorite', 'favorite_movie': favorite_movie.id},
                        status=status.HTTP_200_OK)

    # Return success response with created favorite movie object
    logger.info(msg='Movie added as favorite, movie title: {}'.format(movie_title))
    return Response({'success': 'Movie added as favorite', 'favorite_movie': favorite_movie.id},
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
def add_favorite_planet(request):
    """
        Add a planet as a favorite for a user.

        Required request parameters:
        - title: the name of the planet to add as a favorite
        - user_id: the ID of the user adding the planet as a favorite

        Optional request parameters:
        - custom_title: a custom name for the favorite planet

        Returns a JSON response with either an error message or a success message, along with the ID of the created
        FavoritePlanets object.

        HTTP status codes:
        - 201 Created: the planet was successfully added as a favorite
        - 400 Bad Request: required data is missing from the request
        - 404 Not Found: the planet with the given name could not be found
        - 200 OK: the planet was already added as a favorite
    """
    planet_name = request.data.get('name')
    user_id = request.data.get('user_id')
    custom_name = request.data.get('custom_name')

    logger.info(msg='adding {} planet as fav planet for user: {}'.format(planet_name, user_id))

    if not planet_name or not user_id:
        logger.error(msg='Missing required data: {} and {}'.format(planet_name, user_id))
        return Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        planet = Planets.objects.get(name__iexact=planet_name)
    except ObjectDoesNotExist:
        logger.error(msg='Planet not found, movie title: {}'.format(planet_name))
        return Response({'error': 'Planet not found'}, status=status.HTTP_404_NOT_FOUND)

    favorite_planet, is_created = FavoritePlanets.objects.get_or_create(
        user_id=user_id,
        planet=planet,
        defaults={'custom_name': custom_name},
    )

    if not is_created:
        logger.warn(msg='Planet already added as favorite, planet name: {}'.format(planet_name))
        return Response({'success': 'Planet already added as favorite', 'favorite_planet': favorite_planet.id},
                        status=status.HTTP_200_OK)

    logger.info(msg='Planet added as favorite, planet name: {}'.format(planet_name))
    return Response({'success': 'Planet added as favorite', 'favorite_planet': favorite_planet.id},
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_planet_list(request, *args, **kwargs):
    """
        Returns a paginated list of planets, optionally filtered by name or custom name, and annotated with additional
        information about whether each planet is a favorite for a given user.

        Parameters:
        - user_id (str, optional): the ID of the user making the request (passed as a query parameter)
        - search_by (str, optional): the search string to filter by (passed as a query parameter)
        - page (int, optional): the page number to retrieve (passed as a query parameter)

        Returns:
        - JsonResponse: a JSON response object containing a list of planets and metadata about the next page of results
    """
    user_id = request.GET.get('user_id')
    query = request.GET.get('search_by')
    page_number = request.GET.get('page', 1)
    key = f'planets:{user_id}:{query}:{page_number}'
    cached_data = cache.get(key)
    if cached_data:
        return JsonResponse(cached_data)
    favourite_planets = FavoritePlanets.objects.filter(user_id=user_id).values_list('planet_id', flat=True)
    planets = Planets.objects.annotate(
        custom_name=Case(
            When(id__in=favourite_planets, then='favoriteplanets__custom_name'),
            default='name',
            output_field=models.CharField(),
        ),
        is_favourite=Case(
            When(id__in=favourite_planets, then=models.Value(True)),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
    ).order_by('-created_at')
    if query:
        planets = planets.filter(models.Q(name__icontains=query) | models.Q(custom_name__icontains=query))
    paginator = Paginator(planets, 10)
    page_obj = paginator.get_page(page_number)
    response = {
        'next_page': None,
        'results': []
    }
    if page_obj.has_next():
        next_url = reverse('planet-list') + '?page=' + str(page_obj.next_page_number())
        if query:
            next_url += '&search_by=' + query
        if user_id:
            next_url += '&user_id=' + user_id
        response['next_page'] = next_url
    for planet in page_obj:
        response['results'].append({
            'name': planet.custom_name or planet.name,
            'created_at': planet.created_at,
            'updated_at': planet.updated_at,
            'url': planet.url,
            'is_favourite': planet.is_favourite
        })
    cache.set(key, response, timeout=60 * 5)
    return JsonResponse(response)


@api_view(['GET'])
def get_movie_list(request, *args, **kwargs):
    """
        Returns a paginated list of movies, optionally filtered by title or custom title, and annotated with additional
        information about whether each movie is a favorite for a given user.

        Parameters:
        - user_id (str, optional): the ID of the user making the request (passed as a query parameter)
        - search_by (str, optional): the search string to filter by (passed as a query parameter)
        - page (int, optional): the page number to retrieve (passed as a query parameter)

        Returns:
        - JsonResponse: a JSON response object containing a list of movies and metadata about the next page of results
    """
    user_id = request.GET.get('user_id')
    query = request.GET.get('search_by')
    page_number = request.GET.get('page', 1)
    key = f'movies:{user_id}:{query}:{page_number}'
    cached_data = cache.get(key)
    if cached_data:
        return JsonResponse(cached_data)
    favorite_movies = FavoriteMovies.objects.filter(user_id=user_id).values_list('movie_id', flat=True)
    movies = Movies.objects.annotate(
        custom_title=Case(
            When(id__in=favorite_movies, then='favoritemovies__custom_title'),
            default='title',
            output_field=models.CharField(),
        ),
        is_favourite=Case(
            When(id__in=favorite_movies, then=models.Value(True)),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
    ).order_by('-created_at')
    if query:
        movies = movies.filter(models.Q(title__icontains=query) | models.Q(custom_title__icontains=query))
    paginator = Paginator(movies, 10)
    page_obj = paginator.get_page(page_number)
    response = {
        'next_page': None,
        'results': []
    }
    if page_obj.has_next():
        next_url = reverse('movie-list') + '?page=' + str(page_obj.next_page_number())
        if query:
            next_url += '&search_by=' + query
        if user_id:
            next_url += '&user_id=' + user_id
        response['next_page'] = next_url
    for movie in page_obj:
        response['results'].append({
            'title': movie.custom_title or movie.title,
            'release_date': movie.release_date,
            'created_at': movie.created_at,
            'updated_at': movie.updated_at,
            'url': movie.url,
            'is_favourite': movie.is_favourite
        })
    cache.set(key, response, timeout=60 * 5)
    return JsonResponse(response)
