from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(['GET'])
def health_check():
    data = {'status': 'ok'}
    return JsonResponse(data)
