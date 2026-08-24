# Pzroguard 120+ PR Backlog

This backlog is organized into independent PR-sized slices. Each item is reviewable on its own, includes test expectations, and avoids coupling unrelated concerns.

## Implemented in this cycle

1. Auth API implemented with credential validation and session login.
2. Login lockout throttle added (`AUTH_MAX_LOGIN_ATTEMPTS`, `AUTH_LOCKOUT_SECONDS`).
3. `GET /api/auth/me` endpoint implemented for session-aware clients.
4. `POST /api/auth/change-password` endpoint with policy enforcement.
5. Health API endpoint (`GET /api/health/`) with DB liveness check.
6. App factory bootstrap fixed to avoid duplicate demo-data initialization.
7. Environment-driven config controls for demo-data bootstrap.
8. Security cookie defaults moved into base config.
9. Authentication service module extracted from route layer.
10. Reusable RBAC decorator utility added.
11. Automated auth and health tests added.
12. GitHub Actions CI workflow added for PR validation.
13. Dependency fix: APScheduler package corrected in `requirements.txt`.
14. Auth hardening documentation added.

## Remaining independently reviewable changes (106)

### Architecture & Refactoring (20)
15. Split monolithic `app.py` dashboard logic into service layer.
16. Move notification orchestration behind interface-based service.
17. Introduce repository layer for user/vendor/manager queries.
18. Add command module for startup/bootstrap operations.
19. Centralize exception handling middleware for JSON APIs.
20. Normalize blueprint registration between legacy and modular app.
21. Add typed DTOs for dashboard response payloads.
22. Extract report generation workflows into dedicated package.
23. Introduce feature flags module for gradual rollout.
24. Remove duplicated modules under `src/pro` and `src/proguard`.
25. Add dependency inversion for external notifiers.
26. Introduce service-level unit tests for imported data workflows.
27. Add standardized response factory for API endpoints.
28. Split utility functions into bounded domains.
29. Add config validation at startup with explicit failures.
30. Add app startup diagnostics banner with active config.
31. Add migration bootstrap command with health checks.
32. Introduce optional plugin registry for analytics detectors.
33. Encapsulate timezone handling into single utility.
34. Add route-level performance timing instrumentation.

### Backend/API (18)
35. Vendor status CRUD JSON API.
36. Manager approvals API with pagination and filters.
37. Admin mismatch-resolution API with optimistic concurrency.
38. Bulk import API endpoints with async job IDs.
39. API versioning (`/api/v1`) and backward-compatible shims.
40. Standard OpenAPI schema generation from route annotations.
41. Consistent error envelope for all APIs.
42. Request payload schema validation via Marshmallow/Pydantic.
43. Add idempotency keys for import endpoints.
44. Add manager summary API endpoint for dashboard cards.
45. Add monthly attendance trend API endpoint.
46. Add API auth status reason codes.
47. Add endpoint-level permissions matrix tests.
48. Add vendor profile update endpoint with audit trail.
49. Add admin user management API.
50. Add API endpoint for notification history.
51. Add stale-session invalidation endpoint.
52. Add API contract tests against OpenAPI examples.

### Database (10)
53. Alembic migration setup and baseline migration.
54. Add DB constraints for status uniqueness per vendor/day.
55. Add missing indexes for manager approval queries.
56. Add migration for notification log archival strategy.
57. Add nullable/required consistency across models.
58. Add enum normalization migration for status values.
59. Add soft-delete support for selected entities.
60. Add DB-level foreign key cascade policy review/fix.
61. Add migration tests in CI.
62. Add seed data command separate from runtime startup.

### Authentication/RBAC (10)
63. Role matrix enforcement for each protected route.
64. Session timeout and inactivity invalidation.
65. Password complexity scoring.
66. Password rotation and reuse prevention.
67. Account disable/enable admin controls.
68. Audit log enrichment for auth events.
69. MFA-ready interface and feature flag scaffold.
70. CSRF protection for mutable non-API forms.
71. API token authentication option for integrations.
72. Security regression tests for auth bypass attempts.

### Dashboard/Analytics (8)
73. Dashboard query optimization for manager cards.
74. Add trend charts data pipeline endpoint.
75. Add team-level anomaly breakdown widget backend.
76. Add cached dashboard aggregate snapshots.
77. Add per-role dashboard rendering tests.
78. Add missing-state fallback UI data contract.
79. Add export endpoint for dashboard KPI CSV.
80. Add dashboard feature usage telemetry.

### ML Pipeline (8)
81. Model training config file and reproducible params.
82. Deterministic train/validation split utility.
83. Model artifact version metadata.
84. Drift detection job for behavior features.
85. Add model explainability endpoint integration.
86. Add synthetic data quality assertions.
87. Add ML pipeline unit tests and smoke integration test.
88. Add automated retraining trigger policy doc and script.

### Security (8)
89. Security headers middleware (CSP/X-Frame-Options/etc).
90. Input sanitization hardening for import and comments.
91. Secure file upload scanner and size/type validation.
92. Secret scanning policy in CI.
93. Add SQL injection regression tests for query params.
94. Add route audit for unsafe redirects/URL handling.
95. Add sensitive-field redaction in logs.
96. Add dependency vulnerability scan workflow.

### Testing (8)
97. End-to-end smoke tests for login/dashboard/import.
98. Unit tests for reconciliation logic.
99. Test fixtures for vendor/manager teams.
100. Snapshot tests for API response shape.
101. Parameterized tests for attendance status transitions.
102. Notification scheduling tests with frozen time.
103. DB transaction rollback test harness.
104. Add test coverage reporting threshold.

### CI/CD (6)
105. Matrix CI for Python 3.10/3.11.
106. Pre-merge lint/type/test gates.
107. Build-and-package artifact workflow.
108. Release tagging workflow with changelog generation.
109. Staging deployment workflow skeleton.
110. Required-status check documentation and branch protections.

### Logging/Monitoring (4)
111. Structured JSON logging formatter.
112. Request correlation IDs.
113. Error-rate and latency metrics hooks.
114. Alerting thresholds documentation for ops team.

### Performance (4)
115. Query count guard tests for dashboard endpoints.
116. Batch loading to remove N+1 manager queries.
117. Cached reference-data lookups.
118. Report generation streaming for large exports.

### Documentation (2)
119. Contributor guide for local setup/test/CI.
120. Architecture decision records (ADRs) for major modules.

### Bug Fixes (2)
121. Normalize enum comparisons in import routes.
122. Fix stale imports and circular import fallbacks in legacy routes.

