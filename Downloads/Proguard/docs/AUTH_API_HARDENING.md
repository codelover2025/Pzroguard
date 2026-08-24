# Auth API Hardening

This document describes the new production-grade authentication API behavior in `src/proguard/api/auth.py`.

## Endpoints

- `POST /api/auth/login`
  - Requires JSON body: `username`, `password`
  - Returns `200` with user payload on success
  - Returns `401` for invalid credentials
  - Returns `429` when temporary lockout is active
- `POST /api/auth/logout`
  - Requires authenticated session
  - Logs out current user
- `GET /api/auth/status`
  - Public endpoint for front-end session checks
- `GET /api/auth/me`
  - Requires authenticated session
  - Returns current user profile
- `POST /api/auth/change-password`
  - Requires authenticated session
  - Validates current password
  - Enforces minimum password length from config

## Security Controls

- Login throttle and lockout:
  - `AUTH_MAX_LOGIN_ATTEMPTS` (default: `5`)
  - `AUTH_LOCKOUT_SECONDS` (default: `900`)
- Password policy:
  - `PASSWORD_MIN_LENGTH` (default: `10`)
- Session defaults:
  - `SESSION_COOKIE_HTTPONLY=True`
  - `SESSION_COOKIE_SAMESITE=Lax`

## Testing

Tests are located in:

- `tests/test_auth_api.py`
- `tests/test_health_api.py`

