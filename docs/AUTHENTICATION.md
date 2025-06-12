# Authentication System Documentation

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Email-Based Authentication Flow](#email-based-authentication-flow)
3. [Social Authentication Implementation](#social-authentication-implementation)
4. [Token Management System](#token-management-system)
5. [Data Model Implementation](#data-model-implementation)
6. [Service Layer Architecture](#service-layer-architecture)
7. [API Endpoint Specifications](#api-endpoint-specifications)
8. [Security Measures and Validation](#security-measures-and-validation)
9. [Error Handling Framework](#error-handling-framework)
10. [Configuration and Settings](#configuration-and-settings)

## System Architecture Overview

The Housing & Properties authentication system implements a sophisticated multi-layered architecture that separates concerns across distinct components. The system leverages `Django REST Framework` for API development, `djangorestframework-simplejwt` for JWT token management, `and drf-social-oauth2` for social authentication integration.

The architecture follows a clear separation pattern where **_views_** handle HTTP concerns, **_services_** encapsulate business logic, **_managers_** handle database operations, and **_serializers_** manage data validation and transformation. This design ensures maintainability, testability, and scalability while adhering to **SOLID** principles.

## Email-Based Authentication Flow

### Registration Process

The email-based registration flow begins when a client sends a POST request to `/api/v1/authentication/register/`. The `RegisterView` processes this request through a carefully orchestrated sequence of operations.

Upon receiving the request, the view instantiates the `UserRegistrationSerializer` which validates the incoming data. This serializer enforces strict validation rules including:
- email format validation
- password minimum length of 8 characters
- required user type selection from predefined choices (**_CLIENT, AGENT, VENDOR, ADMIN_**)
- mandatory **_first_** and **_last name_** fields.

Once validation passes, the view delegates to the AuthenticationService's `register_user` method. This service method first performs advanced password validation through the `_validate_password` method, which implements comprehensive security checks. The password must not contain spaces, must include at least:
- one uppercase letter
- one lowercase letter
- one digit
- one special character
These validations use regular expressions to ensure password complexity.

After password validation succeeds, the service calls the UserManager's `create_user` method. The manager **_normalizes_** the email address to ensure case-insensitive uniqueness, creates the user instance with the provided data, and automatically generates the appropriate profile based on the user type through the `_create_profile` method. This automatic profile creation ensures data consistency and eliminates the need for manual profile setup.

The registration process continues with JWT token generation. The `_generate_authentication_tokens` method creates both `access` and `refresh` tokens using the `djangorestframework-simplejwt` library. These tokens include custom claims for `user_type` and `email`, enabling frontend applications to make authorization decisions without additional API calls.

Finally, the system sends a verification email through the `_send_verification_email` method. This method generates a cryptographically secure token using Python's `secrets` module, stores it in the cache with the user's `UUID` as part of the key, and triggers the `EmailService` to send the verification email. The cache entry expires after a configurable period (default 15 minutes), ensuring security while providing reasonable time for users to verify their emails.

### Login Process

The login flow handles authentication for existing users through the `/api/v1/authentication/login/` endpoint. The `LoginView` receives credentials and validates them through the UserLoginSerializer, which ensures both email and password fields are present.

The AuthenticationService's `login` method performs the actual authentication using Django's built-in authentication backend. This method executes several critical checks in sequence. First, it attempts to **_authenticate_** the user with the provided credentials. If authentication fails, it raises a `ValidationError` with a generic message to prevent username enumeration attacks.

Upon successful authentication, the service verifies that the user account is active. Deactivated accounts receive a `BadRequestError` preventing access even with valid credentials. The service then checks the email verification status. Unverified accounts cannot log in, enforcing the platform's requirement for email verification before account usage.

After passing all checks, the system updates the user's `last_login` timestamp, providing an audit trail for security monitoring. Finally, **_JWT tokens_** are generated and returned to the client, completing the authentication process.

### Email Verification Mechanism

The email verification system implements a secure token-based approach that balances security with user convenience. When a user registers, the system generates a verification token using `secrets.token_urlsafe(32)`, producing a URL-safe string of 32 random bytes.

The verification token storage utilizes Django's cache framework rather than the database, providing several advantages. Cache-based storage allows automatic expiration without requiring cleanup jobs, reduces database load for temporary data, and provides flexibility in backend selection (Redis, Memcached, etc.). The cache key follows the pattern `email_verify_{user_uuid}`, ensuring uniqueness and easy retrieval.

When a user clicks the verification link, they access the `EmailVerificationView` endpoint with the pattern `/api/v1/authentication/verify-email/{user_id}/{verification_token}`. The view extracts both parameters and passes them to the AuthenticationService's `verify_email` method.

The verification process retrieves the cached data using the constructed cache key. If the cache entry doesn't exist or has expired, the method raises a `ValidationError` indicating an invalid or expired token. The service then validates that the cached user ID matches the user `UUID` from the URL, preventing token reuse across accounts. Upon successful validation, the user's `is_email_verified` flag is set to True, the cache entry is deleted to prevent reuse, and a success response is returned.

## Social Authentication Implementation

### OAuth2 Integration Architecture

The social authentication system builds upon the `drf-social-oauth2` package, which itself extends `python-social-auth`. This implementation provides a robust foundation for integrating multiple OAuth2 providers while maintaining consistency with the platform's authentication architecture.

The system currently supports **_Google OAuth2_** authentication, with the architecture designed to easily accommodate additional providers. The integration involves several Django applications working in concert:
- **social_django** for core social authentication functionality
- **oauth2_provider** for OAuth2 server capabilities
- **drf_social_oauth2** for REST API integration.

### Social Authentication Flow

The social authentication process begins when a user initiates login through a social provider. The frontend directs users to `/api/v1/authentication/social/begin/{backend}?user_type={type}`, where backend specifies the provider (e.g., "google-oauth2") and `user_type` indicates the account type being created.

The `SocialAuthenticationBeginView`, decorated with `@psa("authentication:social-complete")`, handles the initial request. This decorator integrates `python-social-auth`'s pipeline with the view. The view extracts the `user_type` parameter and stores it in the session for later use during user creation. It then calls `do_auth` from social_core, which initiates the OAuth2 flow by redirecting the user to the provider's authorization page.

After the user authorizes the application, the provider redirects back to `/api/v1/authentication/social/complete/{backend}/`. The `SocialAuthenticationCompleteView` processes this callback, again using the `@psa` decorator for pipeline integration. The view retrieves the `user_type` from the session, defaulting to `CLIENT` if not specified, and cleans up the session to prevent data leakage.

The completion process handles both **_partial_** and **_complete_** pipeline scenarios. Partial pipelines occur when additional user interaction is required (e.g., email conflict resolution). The view checks for partial pipeline data using `partial_pipeline_data`. If found, it continues the pipeline with `backend.continue_pipeline`, passing the `user_type` for profile creation. Otherwise, it completes the authentication with `backend.complete`.

### Custom Pipeline Configuration

The social authentication pipeline customizes the default `python-social-auth` flow through a custom pipeline configuration in settings. The pipeline consists of several steps executed sequentially:

The pipeline begins with `social_core.pipeline.social_auth.social_details`, extracting user information from the provider's response. Next, `social_core.pipeline.social_auth.social_uid` generates a unique identifier for the social account. The `auth_allowed` step checks whether authentication is permitted for the given backend and user.

The critical customization occurs in the `core.pipeline.create_user` step, which replaces the default user creation. This custom function handles both existing and new users differently. For existing users, it verifies email verification status and updates the last login timestamp. For new users, it creates accounts with the appropriate user type and marks email as 'verified' since it comes from a trusted OAuth provider.

The pipeline continues with `social_core.pipeline.social_auth.associate_user`, linking the social account to the user, and concludes with `social_core.pipeline.user.user_details`, updating user information from the social provider.

### User Creation and Profile Management

The custom `create_user` pipeline function in `core/pipeline.py` implements sophisticated user management logic. When processing a new social authentication, the function first checks if a user already exists. For existing users, it ensures the email is verified before allowing login, maintaining consistency with email-based authentication requirements.

For new users, the function extracts fields from the provider's response based on the backend's `USER_FIELDS` setting. It explicitly sets `is_email_verified` to **_True_**, acknowledging that OAuth providers have already verified the email. The function also sets the `user_type` from the session data passed through the pipeline.

The UserManager's `create_user` method handles the actual user creation, automatically generating the appropriate profile based on the `user_type`. This ensures social authentication users receive the same profile setup as email-registered users, maintaining data consistency across authentication methods.

## Token Management System

### JWT Token Generation

The token generation system leverages `djangorestframework-simplejwt` to create secure, stateless authentication tokens. The `_generate_authentication_tokens` method in `AuthenticationService` creates both access and refresh tokens with custom claims.

Access tokens have a 30-minute lifetime, balancing security with user convenience. These tokens include standard claims like `user_id` and `expiration`, plus custom claims for `user_type` and `email`. This additional information enables frontend applications to implement role-based UI without additional API calls.

Refresh tokens last 7 days and enable automatic token renewal without re-authentication. The `ROTATE_REFRESH_TOKENS` setting ensures each refresh generates a new refresh token, limiting the window for token compromise. The `BLACKLIST_AFTER_ROTATION` setting invalidates old refresh tokens after rotation, preventing their reuse.

### Token Security Measures

The token system implements several security measures to protect against common attacks. Tokens are signed using **_HMAC_** with **_SHA256_**, providing integrity verification and preventing tampering. The signing key derives from Django's `SECRET_KEY`, which must be kept secure and rotated periodically in production.

The `AUTH_HEADER_TYPES` configuration restricts accepted authentication schemes to "Bearer" only, preventing confusion attacks with other authentication methods. Token validation occurs automatically through Django REST Framework's authentication classes, checking signature validity, expiration, and blacklist status.

### Token Response Format

All authentication endpoints return tokens in a consistent format through the `TokenSerializer`. This serializer structures the response with access and refresh tokens as top-level fields, plus a nested user object containing essential user information. The user object includes:
- UUID as id
- email address
- user_type for role-based access control
- first and last names for display purposes
- is_verified status for email verification state

This consistent format simplifies frontend integration and reduces the need for additional API calls to fetch user information after authentication.

## Data Model Implementation

### User Model Architecture

The custom `User` model extends both Django's `AbstractUser` and the project's `BaseModel`, inheriting authentication functionality and common fields like **_timestamps_** and **_soft delete_** capability. The model explicitly removes the `username` field by setting it to `None`, enforcing email-based authentication throughout the system.

The `UUID` field uses `uuid6.uuid7` for generating time-ordered, globally unique identifiers. This choice provides several benefits over traditional UUIDs:
- time-ordering improves database index performance
- reduced randomness aids in debugging and log analysis
- guaranteed uniqueness across distributed systems.

The `user_type` field uses Django's `TextChoices` for type safety and database efficiency. The choices (CLIENT, AGENT, VENDOR, ADMIN) are stored as short strings in the database while providing descriptive labels for display. Database indexes on `user_type` combined with `is_active` optimize filtered queries common in multi-tenant systems.

### Profile Model System

Each user type except `ADMIN` has an associated profile model containing type-specific data. These models use `OneToOneField` relationships with the `User` model as primary keys, ensuring data integrity and query efficiency.

The `AgentProfile` model stores professional information including agency affiliation, specializations as a `JSON` field for flexibility, performance metrics (total listings, sales, average rating), and license information with verification status. This design supports the platform's need to showcase agent credentials and track performance.

The `VendorProfile` model captures business-related data such as business name and registration number, business type for categorization, physical address for verification, and verification status for trust building. The flexible design accommodates various vendor types while maintaining consistent verification workflows.

The `ClientProfile` model maintains user preferences and activity data through `JSON` fields for property preferences and saved searches, plus metrics like total purchases. The `JSON` fields provide flexibility for evolving preference schemas without database migrations.

### Manager Implementation

The `UserManager` extends both Django's `BaseUserManager` and the project's `BaseManager`, combining authentication functionality with custom query methods. The manager overrides `get_queryset` to return a custom `UserQuerySet`, enabling method chaining for complex queries.

The `_create_user` method implements the core user creation logic, normalizing email addresses for case-insensitive matching, handling password setting with support for unusable passwords, creating appropriate profiles based on user type, and providing detailed error messages for constraint violations.

The manager includes separate methods for **_regular users_** and **_superusers_**, enforcing business rules like preventing regular users from having staff privileges and ensuring superusers have all required permissions. The **_natural key_** functionality supports Django's serialization framework, using email as the unique identifier.

## Service Layer Architecture

### AuthenticationService Design

The `AuthenticationService` class encapsulates all authentication-related business logic, providing a clean interface for views while maintaining separation of concerns. The service implements methods for user registration, login, email verification, and social authentication completion.

Each method in the service layer handles specific aspects of the authentication flow. The `register_user` method orchestrates password validation, user creation, token generation, and email sending. The `login` method manages credential verification, account status checks, and audit logging. The `verify_email` method handles token validation and account activation.

The service layer design provides several architectural benefits. It centralizes business logic for easier testing and maintenance, abstracts database operations through managers, handles cross-cutting concerns like logging and caching, and provides transaction boundaries for data consistency.

### EmailService Implementation

The `EmailService` class manages all email-related functionality, supporting both plain text and HTML template-based emails. The service provides a clean abstraction over Django's email framework while adding template rendering capabilities.

The `send_verification_email` method specifically handles verification emails, constructing the verification URL with UUID and token, rendering the HTML template with user context, calculating and displaying token expiry time, and using configurable `FROM_DOMAIN` for environment-specific URLs.

The template-based approach ensures consistent email formatting while allowing easy updates to email content without code changes. The service automatically generates plain text versions from HTML templates, ensuring compatibility with all email clients.

## API Endpoint Specifications

### Registration Endpoint Details

The registration endpoint at `/api/v1/authentication/register/` accepts POST requests with specific payload requirements. The request must include email as a valid `email` address, password meeting complexity requirements, `user_type` from allowed choices, and both `first_name` and `last_name` as required fields.

The endpoint returns different status codes based on outcomes: `201 Created` for successful registration with JWT tokens, `400 Bad Request` for validation failures or business rule violations, `409 Conflict` for duplicate email addresses, `429 Too Many Requests` when rate limits are exceeded, and `500 Internal Server Error` for unexpected failures.

The response includes both authentication tokens and user information, enabling immediate login after registration. The success message reminds users to verify their email, maintaining security requirements while providing clear user guidance.

### Login Endpoint Specifications

The login endpoint at `/api/v1/authentication/login/` provides a streamlined authentication interface. It requires only email and password in the request body, both marked with `write_only` in the serializer to prevent data leakage in responses.

Success responses include the same token structure as registration, ensuring frontend consistency. Error responses provide specific messages for different failure scenarios while avoiding information disclosure that could aid attackers. The endpoint respects the same rate limiting as other authentication endpoints, preventing brute force attacks.

### Email Verification Endpoint

The email verification endpoint uses URL parameters rather than request body data, following RESTful design principles for resource identification. The endpoint pattern `/api/v1/authentication/verify-email/{user_id}/{verification_token}` embeds both required parameters in the URL.

The POST method choice, despite not having a request body, aligns with the state-changing nature of the operation. The endpoint returns appropriate status codes: `200 OK` for successful verification, `400 Bad Request` for invalid or expired tokens, and `404 Not Found` for non-existent user IDs.

### Social Authentication Endpoints

The social authentication begin endpoint supports dynamic backend selection through URL parameters. The optional `user_type` query parameter defaults to `CLIENT` when not specified. The endpoint returns `301 redirects` to the OAuth provider, requiring frontend handling of the authentication flow.

The completion endpoint processes OAuth callbacks, handling various scenarios including successful authentication for new and existing users, partial pipeline states requiring user interaction, and authentication failures from the provider or pipeline. Response formats match other authentication endpoints, ensuring consistent frontend integration regardless of authentication method.

## Security Measures and Validation

### Password Security Implementation

The password validation system implements defense-in-depth through multiple validation layers. Django's built-in validators provide baseline security including minimum length enforcement, common password detection, similarity to user attributes prevention, and numeric-only password rejection.

The custom validation in `_validate_password` adds additional requirements addressing common weaknesses. The space prohibition prevents copy-paste errors and encoding issues. Character class requirements ensure password complexity resistant to dictionary attacks. Regular expression-based validation provides precise control over password composition.

### Email Verification Security

The email verification system implements several security measures to prevent abuse. Token generation uses cryptographically secure random sources, ensuring unpredictability. Cache-based storage with automatic expiration limits the window for token use. `UUID` inclusion in cache keys prevents cross-user token reuse. One-time use enforcement through cache deletion prevents replay attacks.

The verification URL structure includes both user identifier and token, requiring both pieces for successful verification. This design prevents brute force attacks on tokens alone while maintaining URL simplicity for email clients.

### Session Security for Social Authentication

Social authentication session handling implements careful security measures. The session stores minimal data (only `user_type`) during the OAuth flow. Immediate cleanup after use prevents session fixation attacks. Default values ensure graceful handling of missing session data. The session cookie configuration inherits Django's security settings, including HttpOnly and Secure flags in production.

## Error Handling Framework

### Exception Hierarchy

The authentication system uses a custom exception hierarchy built on `BaseAPIException`. This base class provides consistent error structure with status codes, error messages, and optional detailed error dictionaries. Specific exceptions like `ConflictError` and `BadRequestError` provide semantic meaning to different error scenarios.

The exception handler in `hp_exception_handler` transforms various exception types into consistent API responses. Django validation errors convert to REST framework validation errors with field-level details. Database integrity errors transform into `ConflictError` with sanitized messages. Unexpected errors log full details while returning generic messages to clients.

### Error Response Consistency

All error responses follow a standardized format ensuring frontend predictability. The format includes a success boolean (always false for errors), a high-level message describing the error category, an errors dictionary with detailed field-level or general errors, and the HTTP status code for proper client handling.

This consistency extends across all authentication endpoints, simplifying frontend error handling and user feedback. Field-level errors support form validation display, while general errors provide context for non-field-specific issues.

### Logging and Monitoring

The authentication system integrates comprehensive logging through `Loguru`, configured in the base logging module. All authentication attempts log with appropriate detail levels. Successful logins record user identification for audit trails. Failed attempts log reasons while avoiding sensitive data exposure. Unexpected errors capture full stack traces for debugging.

The structured logging format enables efficient log analysis and monitoring. Time-based log rotation prevents disk space issues while maintaining historical data. The separation of authentication logs aids in security analysis and compliance requirements.

## Configuration and Settings

### Django Settings Integration

The authentication system configuration spreads across multiple settings modules, following Django best practices for environment-specific configuration. Base settings define common authentication parameters including the custom user model, authentication backends for Django and social auth, and JWT token configuration with lifetimes and algorithms.

Environment-specific settings override base configuration appropriately. Development settings use console email backend for easy testing, shorter token lifetimes for rapid development, and additional debug information in error responses. Production settings enforce secure cookies and HTTPS redirects, use real email backends with proper authentication, and implement stricter rate limiting and security headers.

### Social Authentication Configuration

Social authentication settings demonstrate careful security consideration. OAuth2 credentials load from environment variables, preventing credential exposure in code repositories. Scope configuration requests minimal necessary permissions, respecting user privacy. Redirect URLs use HTTPS in production, preventing token interception. Pipeline configuration balances functionality with security, avoiding unnecessary data exposure.

The modular configuration approach enables easy addition of new social providers. Each provider requires only client credentials and specific settings, with the pipeline handling common functionality across all providers.

### Cache Configuration

Cache configuration directly impacts authentication performance and security. Development environments use local memory cache for simplicity. Production deployments should use Redis or Memcached for persistence and performance. Cache key prefixes prevent collisions in shared cache instances. Timeout configuration balances security with user convenience.

The cache abstraction allows performance optimization without authentication logic changes, demonstrating good architectural separation between business logic and infrastructure concerns.

This comprehensive authentication system provides enterprise-grade security while maintaining developer productivity and user experience. The layered architecture ensures maintainability and testability, while the detailed implementation addresses common security concerns in modern web applications. The system's design accommodates future enhancements while providing a solid foundation for the Housing & Properties marketplace platform.

---
## Future Implementations

- Facebook/Instagram-based OAuth2
- Token refresh functionality
- Rate limiting on authentication endpoints
- Background processing for 'heavy' tasks e.g. profile creation, updates to `last_login` and `updated` fields, etc
