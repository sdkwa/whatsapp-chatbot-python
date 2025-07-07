# Publishing to PyPI

This document outlines the process for publishing the SDKWA WhatsApp Chatbot package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org/) and [TestPyPI](https://test.pypi.org/)
2. **GitHub Repository**: Set up the repository with proper access tokens
3. **API Tokens**: Create API tokens for PyPI publishing

## Setup for Publishing

### 1. PyPI API Tokens

Create API tokens for both PyPI and TestPyPI:

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create a new API token with scope limited to this project
3. Add the token to GitHub repository secrets as `PYPI_API_TOKEN`
4. Repeat for TestPyPI and add as `TEST_PYPI_API_TOKEN`

### 2. GitHub Repository Setup

Add the following secrets to your GitHub repository:

- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your TestPyPI API token

Go to: `Settings > Secrets and variables > Actions > New repository secret`

## Publishing Process

### Automatic Publishing (Recommended)

The repository includes GitHub Actions workflows for automated publishing:

1. **CI/CD Pipeline**: Runs tests and builds on every push
2. **Release Creation**: Creates GitHub releases when tags are pushed
3. **PyPI Publishing**: Automatically publishes to PyPI when releases are created

#### Steps:

1. **Version Bump**: Use the manual workflow or bump version locally:
   ```bash
   # Using the workflow (recommended)
   # Go to Actions > Version Bump and Release > Run workflow
   
   # Or locally:
   make version-patch  # for patch release (1.0.0 -> 1.0.1)
   make version-minor  # for minor release (1.0.0 -> 1.1.0)
   make version-major  # for major release (1.0.0 -> 2.0.0)
   ```

2. **Push Tags**: The version bump will automatically create and push tags
3. **Release**: The release workflow will create a GitHub release
4. **Publish**: The publish workflow will upload to PyPI

### Manual Publishing

For manual publishing or testing:

1. **Install build tools**:
   ```bash
   pip install build twine
   ```

2. **Build the package**:
   ```bash
   make build
   # or
   python -m build
   ```

3. **Test upload to TestPyPI**:
   ```bash
   make upload-test
   # or
   twine upload --repository testpypi dist/*
   ```

4. **Upload to PyPI**:
   ```bash
   make upload
   # or
   twine upload dist/*
   ```

## Version Management

The project uses `bump2version` for version management. Version numbers should follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backwards compatible manner
- **PATCH**: Backwards compatible bug fixes

## Testing Before Release

1. **Run tests**:
   ```bash
   make test
   ```

2. **Check code quality**:
   ```bash
   make lint
   make format-check
   ```

3. **Build and check distribution**:
   ```bash
   make build
   make check-dist
   ```

4. **Test install from TestPyPI**:
   ```bash
   pip install -i https://test.pypi.org/simple/ sdkwa-whatsapp-chatbot
   ```

## Workflow Files

The repository includes the following GitHub Actions workflows:

- `.github/workflows/ci.yml`: Continuous Integration
- `.github/workflows/publish.yml`: Publish to PyPI on release
- `.github/workflows/release.yml`: Create GitHub releases
- `.github/workflows/version-bump.yml`: Manual version bumping

## Package Structure

The package is configured with:

- `setup.py`: Legacy setup configuration
- `pyproject.toml`: Modern Python packaging configuration
- `MANIFEST.in`: Controls which files are included in the distribution
- `.bumpversion.cfg`: Version bumping configuration
- `Makefile`: Development and build commands

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are properly declared
2. **Build Failures**: Check that all required files are included in `MANIFEST.in`
3. **Upload Failures**: Verify API tokens and repository settings
4. **Version Conflicts**: Ensure version numbers are properly incremented

### Checking Package Contents

```bash
# List files in the built package
tar -tzf dist/sdkwa-whatsapp-chatbot-*.tar.gz

# Or for wheel
unzip -l dist/sdkwa_whatsapp_chatbot-*.whl
```

## Security Considerations

1. **Never commit API tokens** to version control
2. **Use GitHub secrets** for sensitive information
3. **Regularly rotate API tokens**
4. **Use trusted publishing** when available (configured in workflows)

## Post-Release

After successful release:

1. **Test installation**: `pip install sdkwa-whatsapp-chatbot`
2. **Update documentation** if needed
3. **Announce the release** on relevant channels
4. **Monitor for issues** and feedback
