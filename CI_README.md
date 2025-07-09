# CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment. The pipeline automatically runs when:

- A pull request is created or updated against `main` or `develop` branches
- Code is pushed to `main` or `develop` branches

## What the Pipeline Does

### 🧪 Test Job
- Runs on Ubuntu with Python 3.11 and 3.12
- Sets up PostgreSQL database for testing
- Installs dependencies and runs Django system checks
- Executes all tests with verbose output
- Optionally runs coverage analysis

### 🔍 Lint Job
- Checks code style with flake8
- Verifies code formatting with Black
- Validates import sorting with isort

### 🔒 Security Job
- Scans dependencies for known vulnerabilities with Safety
- Runs security analysis with Bandit

## Local Development

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run Tests Locally
```bash
# Django test runner
python manage.py test

# Or with pytest (if installed)
pytest

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Code Quality Checks
```bash
# Check code style
flake8 .

# Format code
black .

# Sort imports
isort .

# Security checks
safety check
bandit -r . -x tests/,myenv/,static/
```

### Django System Check
```bash
# Development check
python manage.py check

# Production deployment check
python manage.py check --deploy
```

## Configuration Files

- `.github/workflows/ci.yml` - GitHub Actions workflow
- `pytest.ini` - Pytest configuration
- `.flake8` - Flake8 linting configuration
- `pyproject.toml` - Black, isort, and coverage configuration
- `requirements-dev.txt` - Development dependencies

## Environment Variables for CI

The GitHub Actions workflow uses these environment variables:
- `DEBUG=False`
- `SECRET_KEY=test-secret-key-for-github-actions`
- `DATABASE_URL=postgres://postgres:postgres@localhost:5432/wagtail_demo_test`
- `ALLOWED_HOSTS=localhost,127.0.0.1`

## Status Badges

Add these to your README.md to show build status:

```markdown
![CI](https://github.com/yourusername/wagtail-demo/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/yourusername/wagtail-demo/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/wagtail-demo)
```
