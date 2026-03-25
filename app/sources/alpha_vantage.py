import httpx
import logging
from datetime import datetime
from app.config import Settings
from app.sources import (
    BaseDataSource, SourceName, QuoteData, OHLCVBar, NewsArticle
)
logger = logging.getLogger(__name__)

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

    async def _get(self, params: dict) -> dict | None:
        """Base HTTP GET with error handling."""
        params['apikey'] = self.api_key
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(self.base_url, params=params)
                res.raise_for_status();
                data = res.json()

                 # Alpha Vantage returns error messages in the body, not HTTP status
                if "Error Message" in data:
                    logger.error(f"[AlphaVantage] API error: {data['Error Message']}")
                    return None
                if "Note" in data:
                    logger.warning(f"[AlphaVantage] Rate limit hit: {data['Note']}")
                    return None
                if "Information" in data:
                    logger.warning(f"[AlphaVantage] API notice: {data['Information']}")
                    return None
            return data
        except httpx.TimeoutException:
            logger.error(f"[AlphaVantage] Timeout fetching params={params}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"[AlphaVantage] HTTP {e.response.status_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"[AlphaVantage] Unexpected error: {e}")
            return None
