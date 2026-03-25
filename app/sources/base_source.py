from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from datetime import datetime, timezone

class SourceName(str, Enum):
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    RAPIDAPI      = "rapidapi"

@dataclass
class QuoteData:
    symbol: str
    price: float
    open: float
    high: float
    low: float
    volume: float
    change: float | None = None
    change_percent: str  | None = None
    market_cap: float| None = None
    pe_ratio: float| None = None
    source: str = ""
    fetched_at: datetime   = None

    def __post_init__(self):
        if self.fetched_at is None:
            self.fetched_at = datetime.now(timezone.utc)
 
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "change": self.change,
            "change_percent": self.change_percent,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "source": self.source,
            "fetched_at": self.fetched_at.isoformat(),
        }

@dataclass
class OHLCVBar:
    symbol:    str
    timestamp: datetime
    open:      float
    high:      float
    low:       float
    close:     float
    volume:    float
    source:    str = ""
 
    def to_dict(self) -> dict:
        return {
            "symbol":    self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open":      self.open,
            "high":      self.high,
            "low":       self.low,
            "close":     self.close,
            "volume":    self.volume,
            "source":    self.source,
        }

@dataclass
class NewsArticle:
    title:        str
    symbol:       str | None = None
    summary:      str | None = None
    url:          str | None = None
    sentiment:    str | None = None   # "Bullish" | "Bearish" | "Neutral"
    source:       str | None = None
    published_at: datetime | None = None
 
    def to_dict(self) -> dict:
        return {
            "title":        self.title,
            "symbol":       self.symbol,
            "summary":      self.summary,
            "url":          self.url,
            "sentiment":    self.sentiment,
            "source":       self.source,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }
 
class BaseDataSource(ABC):
    """
    All market data sources implement this interface.
    Ingestion job calls these methods — never the HTTP clients directly.
    """
 
    @property
    @abstractmethod
    def name(self) -> SourceName:
        """Unique identifier for this source."""
        ...
 
    @abstractmethod
    async def get_quote(self, symbol: str) -> QuoteData | None:
        """Fetch latest quote for a symbol."""
        ...
 
    @abstractmethod
    async def get_ohlcv(self, symbol: str, days: int = 100) -> list[OHLCVBar]:
        """Fetch historical OHLCV bars."""
        ...
 
    @abstractmethod
    async def get_news(self, symbol: str, limit: int = 10) -> list[NewsArticle]:
        """Fetch latest news articles."""
        ...
 
    async def health_check(self) -> bool:
        """Return True if the source is reachable. Override if needed."""
        try:
            result = await self.get_quote("AAPL")
            return result is not None
        except Exception:
            return False