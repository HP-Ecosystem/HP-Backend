
## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- uv (for package management)

### Installation

1. Clone the repository
2. Create a virtual environment:
   `uv venv --python 3.12`
3. Install dependencies:
   `make install`
4. Copy `.env.template` to `.env` and configure
5. Run migrations:
   `make migrate`
6. Create superuser:
   `make superuser`
7. Run server:
   `make run`

### API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/api/docs/swagger/
- ReDoc: http://localhost:8000/api/docs/redoc/

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write comprehensive docstrings
- Keep functions focused and clear

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use factories for test data
- Run tests with:
  `make test`
- Run tests with coverage:
  `make test-coverage`

### Linting & Formatting

- Lint code:
  `make lint`
- Format code:
  `make format`

### Cleaning

- Remove Python cache and test artifacts:
  `make clean`

## Deployment

[To be documented]





# Housing & Properties Backend Documentation

## Overview

This is the backend API for the Housing & Properties marketplace platform. Built with Django 5 and Django REST Framework, it provides a robust, scalable API for managing property listings, transactions, messaging, and more.

## Architecture

The project follows a modular monolith architecture with clear domain boundaries, designed to evolve into microservices as needed.

### Key Technologies

- **Framework**: Django 5.2.1
- **API**: Django REST Framework 3.16.0
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Documentation**: drf-spectacular (Swagger/ReDoc)
- **Logging**: Loguru
- **Testing**: Pytest
- **Package Management**: uv
- **Code Quality**: Ruff, pre-commit

## Project Structure

```ini
housing_properties/
├── apps/                  # Domain-specific applications
│   └── authentication/    # Authentication & user management
│       ├── api/           # Views and URL routing
│       ├── managers/      # Custom model managers
│       ├── models/        # User and profile models
│       ├── permissions/   # Custom permissions
│       ├── serializers/   # DRF serializers
│       ├── services/      # Business logic layer
│       ├── tests/         # App-specific tests
│       └── apps.py        # Authentication AppConfig
├── api/                   # API versioning and routing
│   └── v1/                # Version 1 API URLs
├── config/                # Django settings and configuration
│   ├── settings/          # Environment-specific settings
│   │   ├── base.py        # Common settings
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
├── core/                  # Shared utilities and base classes
│   ├── exceptions/        # Custom exceptions & handlers
│   ├── logging/           # Loguru configuration
│   ├── middleware/        # Custom middleware
│   └── models.py          # Base model classes
├── logs/                  # Application logs
├── .env.template          # Environment variables template
├── Makefile               # Common commands
├── manage.py              # Django management script
├── pre-commit-config.yaml # Pre-commit configuration
└── pyproject.toml         # Project dependencies & tools config
```

## Implemented Features

### Core Infrastructure

- **Settings Management**: Modular settings for different environments (development, production, test)
- **Exception Handling**: Custom exception handler providing consistent API error responses
- **Logging**: Integrated Loguru with proper formatting and file rotation
- **Base Models**: Abstract base model with common fields (e.g. created, updated, is_active)
- **API Documentation**: Swagger UI and ReDoc integration for API exploration

### Authentication Domain

- **Custom User Model**:
  - Email-based authentication (no username)
  - UUID7 for public identifiers
  - Support for multiple user types (Client, Agent, Vendor, Admin)
  - Soft delete functionality
  - Email and phone verification tracking
- **User Profiles**:
  - **AgentProfile**: License info, specializations, ratings
  - **VendorProfile**: Business details
  - **ClientProfile**: Preferences, saved searches
- **Custom Managers**:
  - Chainable QuerySet methods for filtering
  - Optimized queries with select_related
  - Business logic encapsulation
  - Search functionality across multiple fields

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- uv (for package management)

### Installation

- Clone the repository
- Create a virtual environment:

  ```bash
  uv venv --python 3.12
  ```
- Install dependencies:

  ```bash
  make install
  ```
- Create PostgreSQL database:

  ```bash
  createdb housing_properties
  ```
- Copy .env.template to .env and configure:

  ```bash
  cp .env.template .env
  ```
- Run migrations:

  ```bash
  make migrate
  ```
- Create superuser:

  ```bash
  make superuser
  ```
- Run development server:

  ```bash
  make run
  ```

### Environment Variables

Key environment variables in `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/housing_properties
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
LOGGING_LEVEL=DEBUG
```

### API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/api/docs/swagger/
- ReDoc: http://localhost:8000/api/docs/redoc/
- Admin Interface: http://localhost:8000/admin/

### Development Commands

**Database Management:**

```bash
make migrations  # Create new migrations
make migrate    # Apply migrations
make superuser  # Create admin user
```
**Development:**

```bash
make run       # Start development server
make shell     # Django shell with IPython
make check     # Run Django system checks
```
**Code Quality:**

```bash
make lint      # Check code style with Ruff
make format    # Auto-format code with Ruff
make test      # Run tests with pytest
make test-coverage  # Run tests with coverage report
```
**Cleanup:**

```bash
make clean     # Remove cache files and artifacts
```

## Code Organization

### Models

- Models inherit from BaseModel for common fields
- Custom managers encapsulate query logic
- Type-specific data stored in profile models

### Exception Handling

- Custom exceptions in core.exceptions.base
- Consistent error response format
- Proper HTTP status codes

### Logging

- Structured logging with Loguru
- Automatic file rotation
- Different log levels per environment

### Testing

Tests are organized by app and use pytest:

```ini
apps/authentication/tests/
├── test_models.py
├── test_managers.py
├── test_services.py
└── test_api.py
```

Run all tests:

```bash
make test
```
Generate coverage report:

```bash
make test-coverage
```
