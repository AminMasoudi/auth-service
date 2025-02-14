import pickle
import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


redis_client = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    )


def get_user_from_redis(request):
    user_id = request.session.get('_auth_user_id')
    if not user_id:
        return AnonymousUser()

    cache_key = f"user:{user_id}"
    user = None

    cached_user = redis_client.get(cache_key)
    if cached_user:
        try:
            user = pickle.loads(cached_user)
        except Exception:
            user = None

    if user is None:
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return AnonymousUser()
        try:
            redis_client.set(cache_key, pickle.dumps(user), ex=3600)
        except Exception:
            # log ? nahhh comon
            pass

    return user
