from .base import *

SECRET_KEY = os.environ.get("SECRET_KEY")
if SECRET_KEY is None:
    raise Exception("Provide SECRET_KEY in env")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.environ.get("MYSQL_HOST", "mysql"),
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "PORT": int(os.environ.get("MYSQL_PORT", 3306)),
    }
}

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
