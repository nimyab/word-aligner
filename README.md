# Word Aligner Service

A FastAPI-based service that aligns words between source and target texts using the SimAlign model.

## Features

- Word alignment between source and target texts
- REST API with FastAPI
- CORS enabled for cross-origin requests
- Health check endpoint

## Requirements

- Python 3.9 or higher
- Poetry for dependency management

## Installation

### Using Poetry (recommended)

1. Clone this repository
2. Navigate to the project directory
3. Install dependencies with Poetry:

```bash
poetry install
```

1. Activate the virtual environment:

```bash
poetry shell
```

### Using pip

1. Clone this repository
2. Navigate to the project directory
3. Create a virtual environment:

```bash
python -m venv .venv
```

1. Activate the virtual environment:

```bash
# On Windows
.venv\Scripts\activate

# On Linux/macOS
source .venv/bin/activate
```

1. Install dependencies:

```bash
pip install -e .
```

## Running the Service

### Using the VS Code Task

1. Open the project in VS Code
2. Open the Command Palette (Ctrl+Shift+P)
3. Type "Tasks: Run Task" and select "Start Word Aligner API"

### Using the Terminal

Run the service using uvicorn:

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Or directly from the main file:

```bash
python main.py
```

The server will be available at `http://localhost:8000`

## API Documentation

When the service is running, you can access:

- API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

### POST /align

Aligns words between source and target texts.

**Request Body:**

```json
{
  "source_text": "Example source text",
  "target_text": "Example target text"
}
```

**Response:**

```json
{
  "alignments": [
    {
      "src_word": "Example",
      "target_word": "Example",
      "src_indexes": [0, 7],
      "target_indexes": [0, 7]
    },
    {
      "src_word": "source",
      "target_word": "target",
      "src_indexes": [8, 14],
      "target_indexes": [8, 14]
    },
    {
      "src_word": "text",
      "target_word": "text",
      "src_indexes": [15, 19],
      "target_indexes": [15, 19]
    }
  ],
  "source_text": "Example source text",
  "target_text": "Example target text",
  "total_alignments": 3
}
```

### GET /health

Checks the health of the service.

**Response:**

```json
{
  "status": "healthy",
  "message": "Service is running normally, model is loaded"
}
```

## Docker

To build and run the service using Docker:

```bash
# Build Docker image
docker build -t word-aligner-service .

# Run container
docker run -p 8000:8000 word-aligner-service
```
