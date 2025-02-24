# API Reference

Base URL: `http://localhost:8000/api`

## Content Processing

### Process Single URL
```http
POST /content/process
```

**Request Body**
```json
{
  "url": "string"
}
```

### Process Multiple URLs
```http
POST /content/process
```

**Request Body**
```json
{
  "urls": ["string"]
}
```

**Response Schema**
```json
{
  "url": "string",
  "title": "string",
  "content": "string",
  "source": "string",
  "author": "string",
  "published_at": "datetime",
  "language": "string",
  "keywords": ["string"],
  "topics": ["string"],
  "summary": "string",
  "sentiment": "string",
  "reading_time": "integer"
}
```

**Error Responses**
- 400: Invalid request format
- 422: Content extraction/analysis failed
  ```json
  {
    "detail": "Error message"
  }
  ```
- 500: Server error

## Content Search

### Search Content
```http
GET /search/content
```

**Query Parameters**
- `query` (required): Search query string
- `limit` (optional): Maximum number of results (default: 5)

**Response**: Array of content objects (same schema as above)

**Error Responses**
- 400: Invalid query parameters
- 500: Search operation failed

## Limits & Constraints
- Maximum URLs per batch request: 10
- Maximum content size: 100KB
- Maximum query length: 1000 characters
- Rate limits: 100 requests per minute
- Supported languages: en, es, fr, de

## Examples

### Process Single URL
```bash
curl -X POST "http://localhost:8000/api/content/process" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/article"}'
```

### Process Multiple URLs
```bash
curl -X POST "http://localhost:8000/api/content/process" \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://example.com/article1", "https://example.com/article2"]}'
```

### Search Content
```bash
curl "http://localhost:8000/api/search/content?query=artificial%20intelligence&limit=5"
```

## Notes
- All timestamps are in ISO 8601 format
- Content extraction uses Playwright for JavaScript rendering
- Text analysis is performed using OpenAI GPT models
- Search uses semantic similarity via ChromaDB
- All responses are UTF-8 encoded 