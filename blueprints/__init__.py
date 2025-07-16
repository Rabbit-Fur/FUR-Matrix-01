# blueprints/__init__.py

from .admin import admin
from .api_events import api_events
from .api_users import api_users
from .public import public
from .monitoring import monitoring

__all__ = ["admin", "api_events", "api_users", "public", "monitoring"]

# ... weitere Blueprints, z. B.:
# from .leaderboard import leaderboard
# from .reminder import reminder
