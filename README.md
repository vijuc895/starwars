# Starwars
This is a Django web application that allows users to add movies and planets to their favorites list, and also retrieve a paginated list of planets and movies.

# Getting started

To run this Django application, you can follow these steps:
1. Clone the repository to your local machine using the command git clone https://github.com/vijuc895/starwars.git.
2. Make sure you have Docker
3. Once docker is installed, please build Docker using 
```docker build -t starwars-app .```
4. Then to run the application using ```docker run -p 8000:8000 starwars-app```

This will start the development server at http://127.0.0.1:8000/

# Api Endpoints

### GET _`/core/planets`_

This endpoint returns a paginated list of planets, optionally filtered by name or custom name, and annotated with additional information about whether each planet is a favorite for a given user.

The request should include the following parameters:

`user_id (str, optional)`: the ID of the user making the request (passed as a query parameter)

`search_by (str, optional)`: the search string to filter by (passed as a query parameter)

`page (int, optional)`: the page number to retrieve (passed as a query parameter)

```commandline
curl --location 'localhost:8000/core/planets?search_by=umbara&user_id=1'
```

### GET _`/core/movies`_

This endpoint returns a paginated list of movies, optionally filtered by title or custom title, and annotated with additional information about whether each movie is a favorite for a given user.

The request should include the following parameters:

`user_id (str, optional)`: the ID of the user making the request (passed as a query parameter)

`search_by (str, optional)`: the search string to filter by (passed as a query parameter)

`page (int, optional)`: the page number to retrieve (passed as a query parameter)

```commandline
curl --location 'localhost:8000/core/movies?search_by=Revenge%20of%20the%20Sith&user_id=2'
```

#### Features:

* It gets the list of planets or movies for the given user, if user_id is specified else it list all.
* It also annotates it with additional information about whether each planet is a favorite for the given user.
* If search_by is specified, it filters the list of planets by name or custom name.
* It paginates the list of planets with 10 planets per page.
* It caches the response data for 5 minutes.


### POST _`/core/favourite/movie`_
This endpoint is used to add a movie to the favorites list for a user. 

The request should include the following parameters:

`title`: The title of the movie to add as a favorite.

`user_id`: The ID of the user adding the movie as a favorite.
Optional parameters:

`custom_title`: A custom title for the favorite movie.
Returns a JSON response with either an error message or a success message, along with the ID of the created FavoriteMovies object.

**HTTP status codes:**

* 201 Created: The movie was successfully added as a favorite.
* 400 Bad Request: Required data is missing from the request.
* 404 Not Found: The movie with the given title could not be found.
* 200 OK: The movie was already added as a favorite.

Curl:
```
curl --location 'localhost:8000/core/favourite/movie' \
--header 'user_id: 1' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": 2,
    "title": "Attack of the Clones",
    "custom_title": "attack_movie"
}'
```

### POST _`/core/favourite/planet`_
This endpoint is used to add a planet to the favorites list for a user. The request should include the following parameters:

`name`: The name of the planet to add as a favorite.

`user_id`: The ID of the user adding the planet as a favorite.

Optional parameters:

`custom_name`: A custom name for the favorite planet.

Returns a JSON response with either an error message or a success message, along with the ID of the created FavoritePlanet object.

**HTTP status codes:**

* 201 Created: The planet was successfully added as a favorite.
* 400 Bad Request: Required data is missing from the request.
* 404 Not Found: The planet with the given name could not be found.
* 200 OK: The planet was already added as a favorite.

Curl:
```
curl --location 'localhost:8000/core/favourite/planet' \
--header 'user_id: 1' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": 1,
    "name": "Umbara",
    "custom_name": "best planet"
}'
```



