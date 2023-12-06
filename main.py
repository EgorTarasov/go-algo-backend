from app.app import create_app
from app.servicies.settings import Settings

settings = Settings()  # type: ignore
app = create_app(settings)
