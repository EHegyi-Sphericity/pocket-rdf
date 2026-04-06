# Contributing to pocket-rdf

Thank you for considering contributing to pocket-rdf!

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/EHegyi-Sphericity/pocket-rdf.git
   cd pocket-rdf
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Install in editable mode with dev dependencies:

   ```bash
   pip install -e .[dev]
   ```

4. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=pocket_rdf --cov-report=term-missing
```

## Code Style

This project uses:

- **Black** for formatting
- **isort** for import ordering
- **flake8** for linting
- **pyright** for type checking

Run all checks locally:

```bash
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
pyright
```

Or let pre-commit handle formatting automatically on each commit.

## Submitting Changes

1. Create a branch from `main`
2. Make your changes
3. Ensure all tests pass and linting is clean
4. Submit a Pull Request with a clear description of your changes
