# 🏠 Housing & Properties Backend Documentation

## 🎯 Overview

This is the **backend API** for the **Housing & Properties marketplace platform**. Built with **Django 5** and **Django REST Framework**, it provides a **robust, scalable API** for managing property listings, transactions, messaging, and comprehensive user management.

### ⚡ **Core Philosophy**
- 🏗️ **Modular monolith** architecture with clear domain boundaries
- 🔄 **Evolution-ready** design for microservices transition
- 🛡️ **Security-first** approach with enterprise-grade authentication
- 📈 **Performance-optimized** for high-scale operations

---

## 🏗️ Architecture

The project follows a **modular monolith architecture** with clear domain boundaries, designed to evolve into **microservices** as needed.

### 🛠️ **Key Technologies**

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| 🔧 **Framework** | Django | Latest | Core web framework |
| 🌐 **API** | Django REST Framework | Latest | RESTful API development |
| 🗄️ **Database** | PostgreSQL | Latest | Primary data store |
| 🔐 **Authentication** | JWT (simplejwt) | Latest | Stateless authentication |
| 📚 **Documentation** | drf-spectacular | Latest | Swagger/ReDoc integration |
| 📊 **Logging** | Loguru | Latest | Structured logging |
| 🧪 **Testing** | Pytest | Latest | Test framework |
| 📦 **Package Management** | uv | Latest | Fast dependency management |
| ✨ **Code Quality** | Ruff + pre-commit | Latest | Linting & formatting |

---

## 📁 Project Structure

```ini
🏠 housing_properties/
├── 📱 apps/                     # Domain-specific applications
│   └── 🔐 authentication/       # Authentication & user management
│       ├── 🗄️ models/           # User and profile models
│       ├── 🧪 tests/            # App-specific tests
│       ├── 🌐 views/            # API views
│       └── ⚡ apps.py            # Authentication AppConfig
├── 🌐 api/                      # API versioning and routing
│   └── 📋 v1/urls/              # Version 1 API URL routing
├── ⚙️ config/                   # Django settings and configuration
│   ├── 🔧 settings/             # Environment-specific settings
│   │   ├── 📋 base.py           # Common settings
│   │   ├── 🔨 development.py    # Development configuration
│   │   ├── 🚀 production.py     # Production configuration
│   │   └── 🧪 test.py           # Testing configuration
│   ├── 🔗 urls.py               # Root URL configuration
│   └── 🌐 wsgi.py               # WSGI configuration
├── 🛠️ core/                     # Shared utilities and base classes
│   ├── ❌ exceptions/           # Custom exceptions & handlers
│   ├── 👥 managers/             # Custom model managers
│   ├── 🔄 middleware/           # Custom middleware
│   ├── 📊 logging/              # Loguru configuration
│   ├── 🛡️ permissions/          # Custom permissions
│   ├── 🔄 serializers/          # DRF serializers
│   ├── ⚙️ services/             # Business logic layer
│   ├── 🧰 utils/                # Utility functions and classes
│   └── 📋 models.py             # Base model classes
│   └── ⛓️ pipeline.py           # Social oauth custom pipeline
├── 📝 logs/                     # Application logs
├── 📄 .env.template             # Environment variables template
├── 🔧 Makefile                  # Common development commands
├── ⚙️ manage.py                 # Django management script
├── 🔍 pre-commit-config.yaml    # Pre-commit configuration
└── 📦 pyproject.toml            # Project dependencies & tools config
```

---

## ✅ Implemented Features

### 🏗️ **Core Infrastructure**

#### ⚙️ **Settings Management**
- 🔧 **Modular configuration** for different environments
- 🌍 **Environment-specific** settings (development, production, test)
- 🔒 **Secure configuration** with environment variables
- 📈 **Performance optimization** per environment

#### ❌ **Exception Handling**
- 🎯 **Custom exception handler** for consistent API responses
- 📋 **Standardized error format** across all endpoints
- 🔍 **Detailed error tracking** and logging
- 🛡️ **Security-aware** error messages

#### 📊 **Logging System**
- ⚡ **Integrated Loguru** with structured formatting
- 🔄 **Automatic file rotation** (10MB per file, 10 days retention)
- 📈 **Performance monitoring** and audit trails
- 🎯 **Environment-specific** logging levels

#### 🗄️ **Base Models**
- 📋 **Abstract base model** with common fields
- ⏰ **Automatic timestamps** (created, updated)
- 🔄 **Soft delete functionality** (`is_active` field)
- 🆔 **UUID7 integration** for public identifiers

#### 📚 **API Documentation**
- 📖 **Swagger UI** for interactive API exploration
- 📋 **ReDoc** for comprehensive documentation
- 🔄 **Auto-generated** from code annotations
- 🎯 **Version-aware** documentation

---

### 👤 **Authentication Domain**

#### 🔐 **Custom User Model**
**Advanced Features:**
- 📧 **Email-based authentication** (no username required)
- 🆔 **UUID7 for public identifiers** (time-ordered, globally unique)
- 👥 **Multiple user types** support:
  - 👤 **CLIENT** - property seekers and buyers
  - 🏢 **AGENT** - licensed real estate professionals
  - 🛠️ **VENDOR** - service providers and contractors
  - 👑 **ADMIN** - platform administrators
- 🗑️ **Soft delete functionality** for data retention
- ✅ **Email verification** tracking
- 🔒 **Security-first** design with comprehensive validation

#### 📋 **User Profiles**

**🏢 AgentProfile:**
- 📜 **License information** with verification status
- 🎯 **Specializations** (JSON field for flexibility)
- ⭐ **Performance ratings** and review system
- 📊 **Activity metrics** (listings, sales, client satisfaction)

**🛠️ VendorProfile:**
- 🏢 **Business registration** details
- 📋 **Service categories** and capabilities
- 📍 **Service area coverage**
- ✅ **Verification badges** and trust indicators

**👤 ClientProfile:**
- 🏠 **Property preferences** (location, type, budget)
- 💾 **Saved searches** and favorites
- 🔔 **Notification preferences**
- 📊 **Activity history** and engagement metrics

#### 🔧 **Custom Managers and QuerySets**

**Advanced Query Capabilities:**
- 🔗 **Chainable QuerySet methods** for complex filtering
- ⚡ **Optimized queries** with select_related and prefetch_related
- 🧠 **Business logic encapsulation** in manager methods
- 🔍 **Full-text search** across multiple fields
- 📊 **Aggregation and analytics** support

#### 🔗 **Social Authentication**
- 🔵 **Google OAuth2** integration
- 🏗️ **Extensible architecture** for additional providers
- 🔄 **Seamless user creation** and profile setup
- 🛡️ **Security-compliant** implementation

---

## 🚀 Getting Started

### 📋 **Prerequisites**

- 🐍 **Python 3.12+** (latest stable version)
- 🗄️ **PostgreSQL** (primary database)
- ⚡ **uv** (ultra-fast package management)

### 🔧 **Installation Process**

#### 1. 📥 **Repository Setup**
```bash
# Clone the repository
git clone <repository-url>
cd housing_properties
```

#### 2. 🐍 **Environment Setup**
```bash
# Create virtual environment with Python 3.12
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

#### 3. 📦 **Dependencies Installation**
```bash
# Install all project dependencies
make install
```

#### 4. 🗄️ **Database Configuration**
```bash
# Create PostgreSQL database
createdb housing_properties

# Configure database connection in .env
```

#### 5. ⚙️ **Environment Configuration**
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your specific settings
nano .env  # or your preferred editor
```

#### 6. 🔄 **Database Migration**
```bash
# Apply database migrations
make migrate
```

#### 7. 👑 **Admin User Creation**
```bash
# Create superuser for admin access
make superuser
```

#### 8. 🚀 **Development Server**
```bash
# Start development server
make run

# Server will be available at http://localhost:8000
```

---

### 🔧 **Environment Variables**

#### 📋 **Required Configuration (.env)**

```env
# 🔐 Security
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=True

# 🗄️ Database
DATABASE_URL=postgres://user:password@localhost:5432/housing_properties

# 🌐 Network & CORS
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# 📊 Logging
LOGGING_LEVEL=DEBUG

# 📧 Email Configuration
FROM_DOMAIN=localhost:8000
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# 🔗 Social Authentication
GOOGLE_OAUTH2_KEY=your-google-client-id-here
GOOGLE_OAUTH2_SECRET=your-google-client-secret-here

# 🎫 JWT Configuration
ACCESS_TOKEN_LIFETIME=30  # minutes
REFRESH_TOKEN_LIFETIME=7  # days

# 💾 Cache Configuration
CACHE_URL=redis://localhost:6379/1  # Optional: Redis cache
```

---

### 🛠️ **Development Commands**

#### 🗄️ **Database Management**
```bash
make migrations      # 📝 Create new database migrations
make migrate        # 🔄 Apply pending migrations
make superuser      # 👑 Create administrative user
make shell          # 🐍 Interactive Django shell
make dbshell        # 🗄️ Direct database shell access
```

#### 🚀 **Development Operations**
```bash
make run           # 🌐 Start development server
make check         # ✅ Run Django system checks
make collectstatic # 📁 Collect static files
make show-urls     # 🔗 Display all URL patterns
```

#### ✨ **Code Quality & Testing**
```bash
make lint             # 🔍 Check code style with Ruff
make format          # ✨ Auto-format code with Ruff
make test            # 🧪 Run full test suite with pytest
make test-coverage   # 📊 Generate coverage report
make test-fast       # ⚡ Run tests without coverage
```

#### 🧹 **Maintenance**
```bash
make clean          # 🗑️ Remove cache files and artifacts
make reset-db       # 🔄 Reset database (WARNING: destructive)
make backup-db      # 💾 Create database backup
make install-hooks  # 🔧 Install pre-commit hooks
```

---

### 📚 **API Documentation Access**

Once the development server is running, access comprehensive documentation:

| Interface | URL | Purpose |
|-----------|-----|---------|
| 📖 **Swagger UI** | http://localhost:8000/api/docs/swagger/ | Interactive API testing |
| 📋 **ReDoc** | http://localhost:8000/api/docs/redoc/ | Comprehensive documentation |
| 👑 **Admin Interface** | http://localhost:8000/admin/ | Database administration |
| 🔍 **Debug Toolbar** | *Automatic in DEBUG mode* | Development debugging |

---

## 🏗️ Code Organization

### 🗄️ **Models Architecture**

#### 📋 **Base Model Pattern**
- **Inheritance**: All models inherit from `BaseModel`
- **Common Fields**: Automatic `created`, `updated`, `is_active` fields
- **Soft Deletes**: Non-destructive data removal
- **UUID Integration**: Public identifiers separate from database IDs

#### 👥 **Custom Managers**
- **Query Logic Encapsulation**: Business rules in manager methods
- **Performance Optimization**: Built-in select_related and prefetch_related
- **Reusable Patterns**: Common query patterns as manager methods

#### 📊 **Profile Models**
- **Type-Specific Data**: Separate models for different user types
- **JSON Fields**: Flexible schema for evolving requirements
- **Relationship Integrity**: OneToOne relationships with User model

---

### ⚙️ **Services Layer**

#### 🧠 **Business Logic Encapsulation**
**Service classes handle complex operations:**
- 🔐 **AuthenticationService**: Registration, login, social auth, email verification, JWT generation, validation, blacklisting
- 📧 **EmailService**: Template rendering, delivery, tracking

#### 🎯 **Design Principles**
- **Single Responsibility**: Each service handles one domain
- **Dependency Injection**: Testable, maintainable code
- **Transaction Management**: Data consistency guarantees
- **Error Handling**: Comprehensive exception management

---

### 🔄 **Serializers**

#### 📋 **Input Validation & Output Formatting**
- **DRF Integration**: Seamless Django REST Framework integration
- **Custom Validation**: Business rule enforcement
- **Nested Serialization**: Complex object relationships
- **Performance Optimization**: Field selection and optimization

#### 📊 **Standardized Responses**
All API responses follow consistent structure:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* Response data */ },
}
```

---

### ❌ **Exception Handling**

#### 🎯 **Custom Exception Hierarchy**
- **Base Classes**: `BaseAPIException` for consistent structure
- **Specific Exceptions**: `ValidationError`, `ConflictError`, `NotFoundError`
- **Status Code Mapping**: Automatic HTTP status code assignment
- **Error Details**: Field-level and general error information

#### 🔧 **Centralized Handler**
**`hp_exception_handler` in `core.exceptions.handler`:**
- **Consistent Format**: All errors return standardized structure
- **Security Awareness**: Sanitized error messages for production
- **Comprehensive Logging**: Full error context for debugging
- **Client-Friendly**: Actionable error messages

**Example Error Response:**
```json
{
  "success": false,
  "message": "Validation error occurred",
  "errors": {
    "field_errors": {
      "email": ["This field is required."],
      "password": ["Password must be at least 8 characters."]
    },
    "non_field_errors": ["User account is deactivated."]
  },
  "status_code": 400,
  "error_code": "VALIDATION_ERROR"
}
```

---

### 📊 **Logging System**

#### ⚡ **Loguru Integration**
**Advanced logging capabilities:**
- **Structured Logging**: JSON format for analysis
- **File Rotation**: Automatic log file management (10MB per file)
- **Retention Policy**: 10 days of log history
- **Performance Monitoring**: Request timing and database queries

#### 🎯 **Log Configuration**
**Location**: `core/logging/base.py`

**Features:**
- **Environment-Specific**: Different log levels per environment
- **Integration**: All Python logs routed through Loguru
- **Security**: Sensitive data filtering and sanitization
- **Monitoring**: Integration points for external monitoring systems

---

### 🧪 **Testing Framework**

#### 📁 **Test Organization**
```ini
🧪 apps/authentication/tests/
├── 📋 test_models.py          # Model functionality tests
├── 👥 test_managers.py        # Manager and QuerySet tests
├── ⚙️ test_services.py        # Business logic tests
├── 🌐 test_api.py             # API endpoint tests
├── 🔐 test_permissions.py     # Permission logic tests
└── 🧰 test_utils.py           # Utility function tests
```

#### 🚀 **Testing Commands**

**Basic Testing:**
```bash
# Run all tests
make test

# Run specific app tests
pytest apps/authentication/tests/

# Run specific test file
pytest apps/authentication/tests/test_models.py

# Run specific test method
pytest apps/authentication/tests/test_models.py::TestUserModel::test_create_user
```

**Coverage Analysis:**
```bash
# Generate coverage report
make test-coverage

# View coverage in browser
coverage html && open htmlcov/index.html
```

**Performance Testing:**
```bash
# Run tests with performance profiling
pytest --profile

# Database query analysis
pytest --ds=config.settings.test --reuse-db --no-migrations
```

---

## 🎯 **Development Best Practices**

### ✨ **Code Quality Standards**
- **🔍 Ruff Integration**: Automated linting and formatting
- **🔧 Pre-commit Hooks**: Automatic code quality checks
- **📝 Type Hints**: Comprehensive type annotation
- **📚 Documentation**: Docstrings for all public methods

### 🔒 **Security Standards**
- **🛡️ Input Validation**: Comprehensive data sanitization
- **🔐 Authentication**: JWT-based stateless authentication
- **🚫 Authorization**: Role-based access control
- **📊 Audit Logging**: Comprehensive activity tracking

### 📈 **Performance Guidelines**
- **🗄️ Database Optimization**: Query optimization and indexing
- **💾 Caching Strategy**: Redis integration for performance
- **📊 Monitoring**: Performance metrics and alerting
- **🔄 Async Support**: Background task processing
