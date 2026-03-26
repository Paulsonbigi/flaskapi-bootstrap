import http
import json
from urllib.parse import urlencode

import httpx
import logging
from datetime import datetime
from app.config import get_settings
from app.sources import (
    BaseDataSource, SourceName, QuoteData, OHLCVBar, NewsArticle
)
logger = logging.getLogger(__name__)

# settings = get_settings()

SENTIMENT_MAP = {
    "Bullish": "Bullish",
    "Somewhat-Bullish": "Bullish",
    "Neutral": "Neutral",
    "Bearish": "Bearish",
    "Somewhat-Bearish": "Bearish",
}

class AlphaVantageSource(BaseDataSource):
    def __init__(self):
        settings = get_settings()
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
            # conn = http.client.HTTPSConnection("alpha-vantage.p.rapidapi.com")
            # headers = {
            #     "X-RapidAPI-Key": self.api_key,
            #     "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com",
            # }

            # query_string = urlencode(params)
            # logger.info(f">>>>> {query_string} {self.api_key}")
            # conn.request(
            #     "GET",
            #     f"/query?{query_string}",
            #     headers=headers
            # )
            # res = conn.getresponse()
            # data = res.read()

            # data = json.loads(data.decode("utf-8"))
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(
                    "https://alpha-vantage.p.rapidapi.com/query",
                    params=params,
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com",
                    }
                )
                data = res.json()
            print(data)
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

    async def get_quote(self, symbol: str) -> QuoteData | None:
        data = await self._get({
            "function": "GLOBAL_QUOTE",
            "symbol":   symbol,
        })
        if not data:
            return None
 
        q = data.get("Global Quote", {})
        if not q or not q.get("05. price"):
            logger.warning(f"[AlphaVantage] Empty quote for {symbol}")
            return None
 
        try:
            return QuoteData(
                symbol         = symbol,
                price          = float(q["05. price"]),
                open           = float(q["02. open"]),
                high           = float(q["03. high"]),
                low            = float(q["04. low"]),
                volume         = float(q["06. volume"]),
                change         = float(q.get("09. change", 0)),
                change_percent = q.get("10. change percent", "0%"),
                source         = self.name.value,
            )
        except (ValueError, KeyError) as e:
            logger.error(f"[AlphaVantage] Failed to parse quote for {symbol}: {e}")
            return None
 
    async def get_ohlcv(self, symbol: str, days: int = 100) -> list[OHLCVBar]:
        outputsize = "full" if days > 100 else "compact"
        data = await self._get({
            "function":   "TIME_SERIES_DAILY_ADJUSTED",
            "symbol":     symbol,
            "outputsize": outputsize,
        })
        if not data:
            return []
 
        series = data.get("Time Series (Daily)", {})
        bars   = []
 
        for date_str, values in list(series.items())[:days]:
            try:
                bars.append(OHLCVBar(
                    symbol    = symbol,
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d"),
                    open      = float(values["1. open"]),
                    high      = float(values["2. high"]),
                    low       = float(values["3. low"]),
                    close     = float(values["5. adjusted close"]),  # use adjusted
                    volume    = float(values["6. volume"]),
                    source    = self.name.value,
                ))
            except (ValueError, KeyError) as e:
                logger.warning(f"[AlphaVantage] Skipping malformed bar {date_str}: {e}")
                continue
 
        # Return oldest → newest
        return sorted(bars, key=lambda b: b.timestamp)
 
    async def get_news(self, symbol: str, limit: int = 10) -> list[NewsArticle]:
        data = await self._get({
            "function": "NEWS_SENTIMENT",
            "tickers":  symbol,
            # "datatype":    "json",
            "limit":     50,
            "sort":     "LATEST",
        })
        print('%%%%%%', data)
        if not data:
            return []
 
        articles = []
        for item in data.get("feed", [])[:limit]:
            try:
                published_at = None
                raw_time = item.get("time_published")
                if raw_time:
                    # Format: 20240315T143000
                    published_at = datetime.strptime(raw_time, "%Y%m%dT%H%M%S")
 
                # Find sentiment specific to this ticker
                sentiment = item.get("overall_sentiment_label")
                for ts in item.get("ticker_sentiment", []):
                    if ts.get("ticker") == symbol:
                        sentiment = ts.get("ticker_sentiment_label", sentiment)
                        break
 
                articles.append(NewsArticle(
                    title        = item.get("title", ""),
                    symbol       = symbol,
                    summary      = item.get("summary"),
                    url          = item.get("url"),
                    sentiment    = SENTIMENT_MAP.get(sentiment, "Neutral"),
                    source       = item.get("source"),
                    published_at = published_at,
                ))
            except Exception as e:
                logger.warning(f"[AlphaVantage] Skipping malformed news item: {e}")
                continue
 
        return articles