
# Crawl4AI Production API

## Production Instances

**Instance 1**: `https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io`
**Instance 2**: `https://crawl4ai-prod-2.victoriousbay-83f81c44.northeurope.azurecontainerapps.io`
**Instance 3**: `https://crawl4ai-prod-3.victoriousbay-83f81c44.northeurope.azurecontainerapps.io`
**Instance 4**: `https://crawl4ai-prod-4.victoriousbay-83f81c44.northeurope.azurecontainerapps.io`

All instances are identical with the same configuration and capabilities, running v1.4 with the stateless URL mapping solution.

## Available Endpoints

### Core Crawling
- **`POST /crawl`** - Main crawling endpoint (batch processing)
- **`POST /crawl/stream`** - Streaming crawl results
- **`GET /health`** - Health check
- **`GET /schema`** - Full API schema/documentation

### Content Extraction
- **`POST /md`** - Extract markdown from URL
- **`POST /html`** - Get preprocessed HTML
- **`POST /screenshot`** - Capture webpage screenshot (PNG)
- **`POST /pdf`** - Generate PDF from webpage
- **`POST /execute_js`** - Execute JavaScript on page

### URL Discovery
- **`POST /map`** - Discover URLs from a root (sitemaps + Common Crawl)

### Utility
- **`GET /metrics`** - Prometheus metrics
- **`GET /playground`** - Interactive API testing interface

## Quick Examples

### Basic Crawl
```bash
curl -X POST https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/crawl \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}'
```

### Multiple URLs
```bash
curl -X POST https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/crawl \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://httpbin.org/html"]}'
```

### Markdown Extraction
```bash
curl -X POST https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/md \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### URL Discovery (Map)
```bash
curl -X POST https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/map \
  -H "Content-Type: application/json" \
  -d '{
    "root": "example.com",
    "limit": 1000,
    "source": "sitemap+cc"
  }'
```

### Screenshot
```bash
curl -X POST https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/screenshot \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Response Format

### Successful Crawl Response
```json
{
  "success": true,
  "results": [
    {
      "url": "https://example.com",
      "html": "<!DOCTYPE html>...",
      "success": true,
      "cleaned_html": "<html>...",
      "markdown": {
        "raw_markdown": "# Page Title\nContent...",
        "markdown_with_citations": "...",
        "references_markdown": "..."
      },
      "media": {"images": [], "videos": [], "audios": []},
      "links": {"internal": [], "external": []},
      "metadata": {"title": "...", "description": "..."},
      "status_code": 200,
      "response_headers": {...}
    }
  ],
  "server_processing_time_s": 2.5,
  "server_memory_delta_mb": 1.2
}
```

## Infrastructure Details

- **Location**: North Europe (Azure Container Apps)
- **Scaling**: 1-20 replicas (auto-scaling based on load)
- **Resources**: 4 CPU, 8GB RAM per replica
- **Trigger**: Scales up after 50 concurrent requests
- **Dependencies**: Self-contained (built-in Redis, Playwright)

## Performance

- **Single URL**: ~2-3 seconds
- **Multiple URLs**: ~8-10 seconds per URL (parallel processing)
- **Concurrent capacity**: Up to 1,000 requests (20 replicas × 50 each)
- **Memory usage**: ~140-150MB per request

## Firecrawl Migration

This can replace Firecrawl `/extract` and `/map` endpoints:

### Extract Equivalent
- **Firecrawl**: `POST /extract` 
- **Crawl4AI**: `POST /crawl` or `POST /md`

### Map Equivalent  
- **Firecrawl**: `POST /map`
- **Crawl4AI**: `POST /map` (sitemaps + optional Common Crawl). Deep in-site navigation still available via `POST /crawl` with deep crawling config.

## Docker Quick Start (Local)

### Build
```bash
docker build -t crawl4ai-api:local --build-arg USE_LOCAL=true .
```

### Run
```bash
docker run --rm -p 11235:11235 \
  -e LLM_PROVIDER="openai/gpt-4o-mini" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  crawl4ai-api:local
```

Or with Compose:
```bash
IMAGE=local-test docker compose up --build
```

### Test locally
```bash
curl -s http://localhost:11235/health
curl -s -X POST http://localhost:11235/map -H "Content-Type: application/json" -d '{"root":"example.com","limit":50,"source":"sitemap+cc"}'
```

## Azure Container Apps – PowerShell Deploy

Use the provided PowerShell script to build, push to ACR, and update the Container App image:

```powershell
# Parameters
$sub = "7e42706e-13f6-442f-9a21-c8bb27ac924d"
$rg  = "odx-grp-crawl4ai-prod"
$app = "crawl4ai-prod"
$acr = "<your-acr-name>"  # e.g., odxregistry

powershell -ExecutionPolicy Bypass -File scripts/aca_deploy.ps1 `
  -SubscriptionId $sub `
  -ResourceGroup $rg `
  -ContainerAppName $app `
  -AcrName $acr `
  -ImageTag ("map-" + (Get-Date -Format yyyyMMddHHmm)) `
  -LlMProvider "openai/gpt-4o-mini" `
  -OpenAiApiKey $env:OPENAI_API_KEY
```

The script will:
- Build the image with `USE_LOCAL=true`
- Push to `acr.io`
- Ensure ingress to port `11235`
- Update the Container App image and env vars


## Interactive Testing

Visit the playground for interactive testing and request generation:
`https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/playground`

## Documentation

### Interactive API Documentation
Visit the Swagger UI for interactive testing and detailed endpoint documentation:
- **Swagger UI**: `https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/docs`
- **OpenAPI JSON**: `https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/openapi.json`

### Configuration Schema
Parameter schema and default configurations:
- **Schema**: `https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/schema`

### Playground
Interactive testing interface:
- **Playground**: `https://crawl4ai-prod.victoriousbay-83f81c44.northeurope.azurecontainerapps.io/playground`