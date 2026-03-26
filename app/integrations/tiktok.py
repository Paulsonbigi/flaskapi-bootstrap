from app.config import get_settings

settings = get_settings()

class TiktokIntegration:
    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key

