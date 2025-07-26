"""
This module provides internationalization (i18n) support for the mwareeth project
using the standard gettext library.
"""

import contextlib
import gettext as _gettext
import os
from typing import Dict, List
import warnings

# Set up the gettext translation system
PROJECT_NAME = 'mwareeth'
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOCALE_DIR = os.path.join(ROOT_DIR, 'locales')
SUPPORTED_LANGUAGES = ['en', 'ar']
# Default to English if no translation is found
FALLBACK_LANGUAGE = "en"

# Store translations for different languages
_translations: Dict[str, _gettext.NullTranslations] = {}
_current_language = 'en'


def _get_translation(language: str) -> _gettext.NullTranslations:
    """
    Get the translation object for the specified language.
    
    Args:
        language: The language code to get the translation for
        
    Returns:
        A gettext translation object
    """
    if language not in _translations:
        try:
            _translations[language] = _gettext.translation(
                PROJECT_NAME, 
                localedir=LOCALE_DIR, 
                languages=[language],
                fallback=True,
            )
        except FileNotFoundError:
            warnings.warn(f"Translation file for language '{language}' not found. Using fallback language '{FALLBACK_LANGUAGE}'.")
            # If the translation file is not found, use a NullTranslations object
            _translations[language] = _gettext.NullTranslations()
    
    _translations[language].install()
    return _translations[language]


def set_language(language: str) -> None:
    """
    Set the current language for translations.
    
    Args:
        language: The language code to use for translations
    """
    global _current_language
    
    if language not in SUPPORTED_LANGUAGES:
        language = FALLBACK_LANGUAGE
    
    _current_language = language


def get_available_languages() -> List[str]:
    """
    Get the list of available languages.
    
    Returns:
        A list of language codes
    """
    return SUPPORTED_LANGUAGES


@contextlib.contextmanager
def force_language(language: str):
    """
    Context manager for setting the current language.
    
    Args:
        language: The language code to use for translations
    """
    global _current_language
    old_language = _current_language
    set_language(language)
    try:
        yield
    finally:
        set_language(old_language)


def gettext(msgid: str, **kwargs) -> str:
    """
    Translate a message to the current language.
    
    Args:
        msgid: The message ID to translate (the original English text)
        **kwargs: Format arguments to apply to the translated string
        
    Returns:
        The translated string, or the msgid itself if no translation is found
    """
    # Get the translation for the current language
    translation = _get_translation(_current_language)
    
    # Translate the message
    translated = translation.gettext(msgid)
    
    # Apply format arguments if provided
    if kwargs:
        try:
            return translated.format(**kwargs)
        except KeyError:
            # If formatting fails, return the unformatted translation
            return translated
    
    return translated


def pgettext(context: str, msgid: str, **kwargs) -> str:
    """
    Translate a message to the current language with context.
    
    Args:
        context: The context of the message
        msgid: The message ID to translate (the original English text)
        **kwargs: Format arguments to apply to the translated string
        
    Returns:
        The translated string, or the msgid itself if no translation is found
    """
    # Get the translation for the current language
    translation = _get_translation(_current_language)

    # Translate the message
    translated = translation.pgettext(context, msgid)
    
    # Apply format arguments if provided
    if kwargs:
        try:
            return translated.format(**kwargs)
        except KeyError:
            # If formatting fails, return the unformatted translation
            return translated
    
    return translated


# Alias for translate for backward compatibility and convenience
_ = gettext
_p = pgettext

# Initialize with English as the default language
set_language('en')
