# Contributing to SDKWA WhatsApp Chatbot

We welcome contributions to the SDKWA WhatsApp Chatbot Python library! This document provides guidelines for contributing.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sdkwa/whatsapp-chatbot-python.git
   cd whatsapp-chatbot-python
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .[dev]
   ```

3. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Code Style

- **Format code with Black:**
  ```bash
  black sdkwa_whatsapp_chatbot/
  ```

- **Sort imports with isort:**
  ```bash
  isort sdkwa_whatsapp_chatbot/
  ```

- **Type checking with mypy:**
  ```bash
  mypy sdkwa_whatsapp_chatbot/
  ```

- **Lint with flake8:**
  ```bash
  flake8 sdkwa_whatsapp_chatbot/
  ```

## Testing

- **Run tests:**
  ```bash
  pytest
  ```

- **Run tests with coverage:**
  ```bash
  pytest --cov=sdkwa_whatsapp_chatbot
  ```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request

## Issue Reporting

When reporting issues, please include:
- Python version
- Library version
- Minimal code example
- Error messages and stack traces
- Expected vs actual behavior

## Documentation

- Use clear docstrings for all public methods
- Include type hints
- Add examples for complex features
- Update README for new features

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a git tag
4. Push to PyPI

Thank you for contributing!
