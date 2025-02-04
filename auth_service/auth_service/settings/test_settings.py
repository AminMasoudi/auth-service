from .base import LOGGING

LOGGING["handlers"]["file_json"]["filename"] ="logs/test.log.jsonl"
LOGGING["loggers"]["django"]["handlers"] =["file_json"]