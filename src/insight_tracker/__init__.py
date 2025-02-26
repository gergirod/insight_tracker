# Import auth module to make it available at package level
from . import auth
from . import db
from . import ui
from . import utils
from . import api

# You can also expose specific functions if needed
from .auth import (
    handle_callback,
    logout,
    validate_token_and_get_user,
    silent_sign_in,
    login,
    signup,
    process_callback
)

__all__ = [
    'auth',
    'db',
    'ui',
    'utils',
    'api',
    'handle_callback',
    'logout',
    'validate_token_and_get_user',
    'silent_sign_in',
    'login',
    'signup',
    'process_callback'
]

