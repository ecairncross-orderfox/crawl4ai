from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field
from utils import FilterType


class CrawlRequest(BaseModel):
    urls: List[str] = Field(min_length=1, max_length=100)
    browser_config: Optional[Dict] = Field(default_factory=dict)
    crawler_config: Optional[Dict] = Field(default_factory=dict)

class MarkdownRequest(BaseModel):
    """Request body for the /md endpoint."""
    url: str                    = Field(...,  description="Absolute http/https URL to fetch")
    f:   FilterType             = Field(FilterType.FIT, description="Content‑filter strategy: fit, raw, bm25, or llm")
    q:   Optional[str] = Field(None,  description="Query string used by BM25/LLM filters")
    c:   Optional[str] = Field("0",   description="Cache‑bust / revision counter")
    provider: Optional[str] = Field(None, description="LLM provider override (e.g., 'anthropic/claude-3-opus')")


class RawCode(BaseModel):
    code: str

class HTMLRequest(BaseModel):
    url: str
    
class ScreenshotRequest(BaseModel):
    url: str
    screenshot_wait_for: Optional[float] = 2
    output_path: Optional[str] = None

class PDFRequest(BaseModel):
    url: str
    output_path: Optional[str] = None


class JSEndpointRequest(BaseModel):
    url: str
    scripts: List[str] = Field(
        ...,
        description="List of separated JavaScript snippets to execute"
    )


class MapRequest(BaseModel):
    root: str = Field(..., description="Root domain or URL to discover from")
    limit: int = Field(1000, ge=1, le=10000)
    source: str = Field("sitemap+cc", description="'sitemap', 'cc', or 'sitemap+cc'")
    pattern: Optional[str] = Field("*", description="Glob-like URL include pattern")
    extract_head: bool = False
    live_check: bool = False
    concurrency: int = Field(200, ge=1, le=5000)
    hits_per_sec: int = Field(5, ge=0, le=1000)
    query: Optional[str] = None
    score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    filter_nonsense_urls: bool = True