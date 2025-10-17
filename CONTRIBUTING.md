# Contributing Guide

Thank you for considering contributing to Daily Brief!

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to make participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates. When creating a bug report, please include:

- Use a clear and descriptive title
- Detailed steps to reproduce
- Expected behavior vs actual behavior
- Screenshots (if applicable)
- Home Assistant version, Python version
- Relevant log output

**Bug Report Template**:

```markdown
**Description**
Brief description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happened

**Environment**
- Home Assistant version: [e.g. 2024.10.0]
- Python version: [e.g. 3.11]
- Daily Brief version: [e.g. 0.1.0]

**Logs**
```
Paste relevant logs
```

**Screenshots**
If applicable, add screenshots
```

### Feature Requests

Feature requests should include:

- Clear description of the feature
- Why this feature is needed
- Possible implementation approach (optional)
- Related screenshots or mockups (optional)

### Submitting Code

#### Development Workflow

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/ha-daily-brief
   cd ha-daily-brief
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/amazing-feature
   # or
   git checkout -b fix/bug-description
   ```

3. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements_dev.txt
   pre-commit install
   ```

4. **Write code**
   - Follow existing code style
   - Add type hints
   - Write docstrings
   - Update relevant documentation

5. **Run tests**
   ```bash
   # Run all tests
   pytest tests/

   # Run code quality checks
   black custom_components/daily_brief/
   isort custom_components/daily_brief/
   pylint custom_components/daily_brief/
   mypy custom_components/daily_brief/
   ```

6. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   **Commit Message Conventions**:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation updates
   - `style:` Code formatting (does not affect code execution)
   - `refactor:` Refactoring
   - `test:` Test-related
   - `chore:` Build process or auxiliary tool changes

7. **Push and create PR**
   ```bash
   git push origin feature/amazing-feature
   ```
   Then create a Pull Request on GitHub

#### Pull Request Guidelines

- Fill out the PR template
- Link related issues
- Ensure all tests pass
- Update documentation (if needed)
- Add changelog entry
- Wait for code review

**PR Checklist**:

- [ ] Code follows project style guidelines
- [ ] Necessary tests have been added
- [ ] All tests pass
- [ ] Documentation has been updated
- [ ] Changelog entry has been added
- [ ] Commit messages are clear and descriptive

## Code Style

### Python Code Standards

- Use **Black** for code formatting
- Use **isort** for import sorting
- Use **pylint** for code linting
- Use **mypy** for type checking
- Follow **PEP 8** standards
- Maximum line length: 100 characters

### Documentation Standards

- All public functions/classes must have docstrings
- Use Google-style docstrings
- Code comments in English or Chinese (be consistent)
- README and documentation in Markdown format

### Example

```python
"""Module docstring."""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class ExampleClass:
    """Example class docstring.

    Detailed description of what this class does.

    Attributes:
        name: Name attribute
        value: Value attribute

    """

    def __init__(self, name: str, value: int) -> None:
        """Initialize the example class.

        Args:
            name: The name
            value: The value

        """
        self.name = name
        self.value = value

    async def example_method(self, param: str) -> dict[str, Any]:
        """Example async method.

        Args:
            param: Parameter description

        Returns:
            Return value description

        Raises:
            ValueError: When this exception is raised

        """
        if not param:
            raise ValueError("param cannot be empty")

        return {"result": param}
```

## Adding New Features

### Adding a New AI Provider

1. Create a new file in `ai/providers/` (e.g., `anthropic.py`)
2. Inherit from `LLMProvider` or `TTSProvider` base class
3. Implement all abstract methods
4. Add to `__init__.py`
5. Update config flow
6. Write tests
7. Update documentation

### Adding a New Content Pack

1. Edit `feeds/content_packs.py`
2. Add new content pack definition
3. Test that RSS feeds are valid
4. Update README

## Testing

### Writing Tests

- All new features must have tests
- Test file naming: `test_<module_name>.py`
- Use pytest fixtures
- Mock external API calls

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_aggregator.py

# Run specific test
pytest tests/test_aggregator.py::test_fetch_feed

# With coverage report
pytest --cov=custom_components/daily_brief tests/
```

## Release Process

Only maintainers can publish new versions:

1. Update version number
   - `manifest.json`
   - `const.py`

2. Update `CHANGELOG.md`

3. Create Git tag
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

4. GitHub Actions will automatically create release

## Getting Help

If you need help:

- Check the [documentation](README.zh-CN.md)
- Search [existing issues](https://github.com/yourusername/ha-daily-brief/issues)
- Create a new issue to ask
- Join the discussion

## Acknowledgments

Thank you to all contributors!

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
