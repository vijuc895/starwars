import requests
from django.core.management.base import BaseCommand

from core.models import Movies, Planets

from decouple import config


class Command(BaseCommand):
    help = 'Loads movies and planets from the Star Wars API'

    def handle(self, *args, **options):
        # Make API request to get movies data
        url = config('PLANET_DATA_URL')
        while url:
            response = requests.get(url)
            print("Planet data: ", response)
            if response.status_code == 200:
                data = response.json()
                for planet_data in data['results']:
                    Planets.objects.update_or_create(
                        name=planet_data['name'],
                        defaults={
                            'url': planet_data['url'],
                        }
                    )
                url = data['next']
            else:
                url = None

        url = config('MOVIE_DATA_URL')
        while url:
            print("Movies data: ", response)
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for movie_data in data['results']:
                    Movies.objects.update_or_create(
                        title=movie_data['title'],
                        defaults={
                            'release_date': movie_data['release_date'],
                            'url': movie_data['url'],
                        }
                    )
                url = data['next']
            else:
                url = None
