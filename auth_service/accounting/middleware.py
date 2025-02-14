from django.utils.functional import SimpleLazyObject
from django.utils.deprecation import MiddlewareMixin
from auth_service.utils import get_user_from_redis

class RedisAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user_from_redis(request))
        request.user = get_user_from_redis(request)