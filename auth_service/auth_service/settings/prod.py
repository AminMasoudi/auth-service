from .base import *

SECRET_KEY = os.environ.get("SECRET_KEY")
if SECRET_KEY is None:
    raise Exception("Provide SECRET_KEY in env")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split()