# Content Processing API

Web API for content extraction and analysis using GPT and vector search.

## Features

- Content extraction from URLs using Playwright
- Text analysis with OpenAI GPT-4
- Semantic search with ChromaDB and LangChain
- REST API with FastAPI
- Web UI with Bootstrap 5
- Comprehensive test coverage
- CI/CD with GitHub Actions

## Tech Stack

### Backend
- Python 3.11+
- FastAPI + Pydantic
- OpenAI GPT-4
- ChromaDB + LangChain
- Playwright

### Frontend
- Bootstrap 5
- Jinja2 Templates
- Vanilla JavaScript

## Docker Deployment

1. Clone the repository:
```bash
git clone <repo>
cd <project-dir>
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Running Tests in Docker

Run the test suite in a Docker container:
```bash
# Run all tests
docker-compose run --rm app pytest
```

### Project Structure
```
src/
├── api/          # API routes
├── core/         # Core functionality
├── models/       # Data models
├── services/     # Business logic
├── web/         # Web interface
└── tests/       # Test suites
```

## API Documentation

### Process Content
```http
POST /api/content/process
Content-Type: application/json

{
  "url": "string" | "urls": ["string"]
}
```

### Search Content
```http
GET /api/search/content?query=string&limit=number
```

See [API Documentation](api.md) for complete reference.

## License

MIT

## Acknowledgments

- OpenAI for GPT models
- ChromaDB team
- FastAPI framework
- Playwright project
