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
├── apps/                     # Domain-specific applications
│   └── authentication/       # Authentication & user management
│       ├── managers/         # Custom model managers
│       ├── models/           # User and profile models
│       ├── permissions/      # Custom permissions
│       ├── serializers/      # DRF serializers
│       ├── services/         # Business logic layer
│       ├── tests/            # App-specific tests
│       ├── views/            # Views
│       └── apps.py           # Authentication AppConfig
├── api/                      # API versioning and routing
│   └── v1/urls/              # Version 1 API URLs routing
├── config/                   # Django settings and configuration
│   ├── settings/             # Environment-specific settings
│   │   ├── base.py           # Common settings
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI configuration
├── core/                     # Shared utilities and base classes
│   ├── exceptions/           # Custom exceptions & handlers
│   ├── logging/              # Loguru configuration
│   ├── middleware/           # Custom middleware
│   ├── utils/                # Utility functions and classes
│   └── models.py             # Base model classes
├── logs/                     # Application logs
├── .env.template             # Environment variables template
├── Makefile                  # Common commands
├── manage.py                 # Django management script
├── pre-commit-config.yaml    # Pre-commit configuration
└── pyproject.toml            # Project dependencies & tools config
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
- **Custom Managers and Querysets**:
  - Chainable QuerySet methods for filtering
  - Optimized queries with select_related
  - Business logic encapsulation
  - Search functionality across multiple fields
- **Social authentication**:
  - Google OAuth2

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
  # Edit .env with your settings
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
FROM_DOMAIN=localhost:8000
GOOGLE_OAUTH2_KEY=your-google-client-id
GOOGLE_OAUTH2_SECRET=your-google-client-secret
```

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
make shell     # Django shell
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

### API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/api/docs/swagger/
- ReDoc: http://localhost:8000/api/docs/redoc/
- Admin Interface: http://localhost:8000/admin/

## Code Organization

### Models

- Models inherit from `BaseModel` for common fields
- Custom managers encapsulate query logic
- Type-specific data stored in profile models

### Services

- Business logic is encapsulated in service classes (e.g., `AuthenticationService`).
- Services handle registration, login, social authentication, email verification, and token management.

### Serializers

- DRF serializers for input validation and output formatting.
- Error responses are standardized.

### Exception Handling

- Custom exceptions in `core.exceptions.base`
- Consistent error response format with proper HTTP status codes.
- Centralized exception handler (`core.exceptions.handler.hp_exception_handler`) ensures all errors are logged and returned in a predictable structure.

**Example error response**:

```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "detail": {
      "email": "This field is required."
    }
  },
  "status_code": 400
}
```

### Logging

- Uses Loguru for structured logging.
- Logs are written to file with rotation (`10 MB` per file, `10 days` retention).
- All standard Python logs are routed through Loguru for consistency.
- Log configuration is in `core/logging/base.py`.

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
