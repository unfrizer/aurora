"""Public gateway for application-owned user preferences."""

from src.preferences.models import PreferencesError, UserPreferences
from src.preferences.store import PreferencesStore, default_preferences_path

__all__ = ["PreferencesError", "PreferencesStore", "UserPreferences", "default_preferences_path"]
