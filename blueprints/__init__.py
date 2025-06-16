from .api_users import api_users
from .api_events import api_events


app.register_blueprint(api_events)
app.register_blueprint(api_users)

