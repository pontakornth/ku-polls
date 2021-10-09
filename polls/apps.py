"""Configuration for poll app."""
from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Class for configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
