import logging
from app.sources import BaseDataSource, QuoteData, OHLCVBar, NewsArticle, AlphaVantageSource

logger = logging.getLogger(__name__)

class SourceRegistry:
 
    def __init__(self):
        # first source is primary, rest are fallbacks
        self._sources: list[BaseDataSource] = [
            AlphaVantageSource(),
        ]

    @property
    def sources(self) -> list[BaseDataSource]:
        return self._sources
    
    async def get_quote(self, symbol: str) -> QuoteData | None:
        primary_quote = None
        secondary_quote = None

        for i, source in enumerate(self._sources):
            quote = await source.get_quote(symbol)
            if quote and i == 0:
                primary_quote = quote
            elif quote and i == 1:
                secondary_quote = quote
 
        if not primary_quote and not secondary_quote:
            logger.error(f"[Registry] All sources failed for quote: {symbol}")
            return None
 
        # Use primary, enrich with secondary fundamentals if missing
        result = primary_quote or secondary_quote
        if primary_quote and secondary_quote:
            result.pe_ratio    = result.pe_ratio    or secondary_quote.pe_ratio
            result.market_cap  = result.market_cap  or secondary_quote.market_cap
 
        print('result////', result)
        return result
    
    async def get_ohlcv(self, symbol: str, days: int = 100) -> list[OHLCVBar]:
        """
        Try sources in order. Return the first non-empty result.
        """
        for source in self._sources:
            bars = await source.get_ohlcv(symbol, days)
            if bars:
                logger.info(f"[Registry] {symbol} OHLCV: {len(bars)} bars from {source.name.value}")
                return bars
            logger.warning(f"[Registry] {source.name.value} returned no OHLCV for {symbol}")
 
        logger.error(f"[Registry] All sources failed for OHLCV: {symbol}")
        return []
    
    async def get_news(self, symbol: str, limit: int = 10) -> list[NewsArticle]:
        """
        Merge news from all sources, deduplicate by title, return top N.
        Alpha Vantage has sentiment — prefer those articles.
        """
        all_articles: list[NewsArticle] = []
        seen_titles: set[str] = set()
 
        # Alpha Vantage first — has sentiment scores
        for source in reversed(self._sources):
            articles = await source.get_news(symbol, limit)
            for article in articles:
                title_key = article.title.lower().strip()[:80]
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    all_articles.append(article)
 
        # Sort: sentiment-enriched articles first, then by recency
        all_articles.sort(
            key=lambda a: (
                a.sentiment is not None,          # articles with sentiment first
                a.published_at is not None,        # then articles with timestamps
                a.published_at or "",
            ),
            reverse=True,
        )
 
        logger.info(f"[Registry] {symbol} news: {len(all_articles)} articles from all sources")
        return all_articles[:limit]
    
    async def health_check_all(self) -> dict[str, bool]:
        """Check all sources and return their status."""
        results = {}
        for source in self._sources:
            ok = await source.health_check()
            results[source.name.value] = ok
            status = "OK" if ok else "FAILED"
            logger.info(f"[Registry] Health check {source.name.value}: {status}")
        return results
 
 
# Singleton — reused across ingestion job calls
source_registry = SourceRegistry()
