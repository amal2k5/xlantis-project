"""Configuration package for Xlantis RP Streamer & Content Directory."""
from .celery import app as celery_app

__all__ = ("celery_app",)
