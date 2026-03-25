import httpx
import logging
from datetime import datetime
from app.config import Settings
from app.sources import (
    BaseDataSource, SourceName, QuoteData, OHLCVBar, NewsArticle
)

settings = Settings()

SENTIMENT_MAP = {
    "Bullish": "Bullish",
    "Somewhat-Bullish": "Bullish",
    "Neutral": "Neutral",
    "Bearish": "Bearish",
    "Somewhat-Bearish": "Bearish",
}

class AlphaVantageSource(BaseDataSource):
    def __init__(self):
        self.base_url = settings.alpha_vantage_base_url
        self.api_key  = settings.alpha_vantage_api_key
        self.timeout  = 15

    @property
    def name(self):
        return SourceName.ALPHA_VANTAGE

    def _get(self, params: dict) -> dict | None:
        """Base HTTP GET with error handling."""
        params['apikey'] = self.api_key
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await 
        except:
            pass
