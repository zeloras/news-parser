# Architecture

## Components

### 1. Content Extraction
- Interface: `ContentExtractorInterface`
- Implementation: `PlaywrightExtractor`
- Purpose: URL content extraction
- Tech: Playwright, async

### 2. Content Analysis
- Interface: `ContentAnalyzerInterface`
- Implementation: `OpenAIAnalyzer`
- Purpose: Text analysis with GPT
- Tech: LangChain + OpenAI

### 3. Storage
- Interface: `ContentRepositoryInterface`
- Implementation: `ChromaRepository`
- Purpose: Vector storage and search
- Tech: ChromaDB, LangChain

### 4. API
- Framework: FastAPI
- Routes: content, search
- Models: Pydantic
- Validation: Type hints
- Error Handling: HTTPException

### 5. Web UI
- Framework: Bootstrap 5
- Templates: Jinja2
- JS: Vanilla
- Components: Modular

## Data Flow

### Content Processing
```
URL -> Extractor -> Analyzer -> Repository -> Response
```

### Search
```
Query -> Vector Search -> Filter -> Response
```

## Project Structure
```
src/
├── api/          # FastAPI routes
│   ├── routes/   # Route handlers
├── core/         # Core functionality
│   ├── config.py # Settings
│   ├── factory.py # DI container
│   └── exceptions.py # Custom errors
├── models/       # Pydantic models
├── services/     # Business logic
│   ├── extraction/ # Content extraction
│   ├── analysis/   # Text analysis
│   └── storage/    # Vector storage
├── web/         # UI components
└── tests/       # Test suites
    ├── test_api/     # API tests
    ├── test_core/    # Core tests
    └── test_services/ # Service tests
```

## Error Handling
- Base: `ContentProcessingException`
- Types: 
  - ContentExtractionError
  - ContentAnalysisError
  - DatabaseError
  - SearchError
- HTTP mapping: 400, 422, 500
- Validation: Pydantic models

## Configuration
- Source: .env
- Validation: Pydantic Settings
- Cache: lru_cache
- Categories: 
  - OpenAI (API key, model, temperature)
  - ChromaDB (persist directory)
  - Content Processing (chunk size, overlap)

## Testing
- Framework: pytest
- Async: pytest-asyncio
- Mocks: pytest-mock, AsyncMock
- Coverage: pytest-cov (target: 80%+)
- CI/CD: GitHub Actions

## CI/CD
- Platform: GitHub Actions
- Triggers: push/PR to main/master
- Steps:
  - Python setup (3.11)
  - Dependencies installation
  - Playwright setup
  - Test execution
  - Coverage reporting
- Coverage: Codecov integration

## Security
- Input validation: Pydantic
- Error sanitization
- API keys in env
- CORS enabled
- Docker isolation

## Performance
- Async IO
- Connection pooling
- Batch processing
- Response caching
- ChromaDB persistence 