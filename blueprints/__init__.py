from .api_events import api_events
from .api_users import api_users

app.register_blueprint(api_events)
app.register_blueprint(api_users)
