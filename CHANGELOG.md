# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PyPI publishing setup with automated workflows
- GitHub Actions for CI/CD, testing, and publishing
- Version management with bump2version
- Development tools and Makefile
- Comprehensive publishing documentation
- Type checking configuration
- Code formatting and linting setup
- Modern Python packaging with pyproject.toml

### Changed
- Improved project structure for PyPI distribution
- Enhanced development workflow with automated tools

## [1.0.0] - 2025-01-07

### Added
- Initial release of SDKWA WhatsApp Chatbot Python library
- Telegraf-like API for WhatsApp bots
- WhatsAppBot class with clean configuration
- Support for text messages, commands, and media files
- Scene system for conversation flows
- Wizard scenes for step-by-step interactions
- Session management with memory and file stores
- Middleware support for composable functionality
- Context object with reply methods
- Event filtering and pattern matching
- Webhook support for Flask and FastAPI
- Complete examples and documentation
- Type hints throughout the library
- Error handling and logging support

### Features
- **Bot Creation**: Simple WhatsAppBot class with SDKWA configuration
- **Message Handling**: Text, photo, document, audio, video, location, contact support
- **Commands**: /start, /help, and custom command handling
- **Scenes**: Conversation flow management with enter/leave handlers
- **Wizards**: Step-by-step conversation flows with data collection
- **Sessions**: Persistent state management across conversations
- **Middleware**: Composable middleware pattern for extensibility
- **Webhooks**: Built-in webhook support for web frameworks
- **Examples**: Complete working examples for all features

### Dependencies
- sdkwa-whatsapp-api-client >= 1.0.0
- typing-extensions >= 4.0.0
- pydantic >= 2.0.0

[Unreleased]: https://github.com/sdkwa/whatsapp-chatbot-python/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/sdkwa/whatsapp-chatbot-python/releases/tag/v1.0.0
