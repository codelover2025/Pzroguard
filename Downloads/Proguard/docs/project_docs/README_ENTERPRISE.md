# PROGUARD - Enterprise Timesheet Management System

![PROGUARD Logo](static/img/PROGUARD-logo.png)

## Overview

PROGUARD is an enterprise-grade vendor timesheet management system designed for large organizations. Built with modern architecture principles, it provides comprehensive attendance tracking, automated notifications, AI-powered insights, and detailed reporting capabilities.

## 🏗️ Enterprise Architecture

### Project Structure

```
PROGUARD/
├── src/                          # Source code
│   └── PROGUARD/                  # Main application package
│       ├── core/                 # Application factory and initialization
│       │   └── application.py    # Flask app factory
│       ├── models/               # Database models (separated)
│       │   ├── user.py          # User authentication models
│       │   ├── vendor.py        # Vendor profile models
│       │   ├── attendance.py    # Attendance tracking models
│       │   └── ...              # Other domain models
│       ├── api/                  # REST API blueprints
│       │   ├── auth.py          # Authentication endpoints
│       │   ├── vendor.py        # Vendor-specific APIs
│       │   ├── manager.py       # Manager dashboard APIs
│       │   └── admin.py         # Administrative APIs
│       ├── services/             # Business logic services
│       │   ├── notification_service.py
│       │   ├── report_service.py
│       │   └── ai_service.py
│       ├── utils/                # Utility functions
│       ├── config/               # Configuration management
│       │   └── settings.py      # Environment-specific configs
│       ├── middleware/           # Custom middleware
│       └── web/                  # Web assets
│           ├── templates/        # Jinja2 templates
│           └── static/          # CSS, JS, images
├── tests/                        # Test suites
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data fixtures
├── deployment/                   # Deployment configurations
│   ├── docker/                  # Docker containerization
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── kubernetes/              # Kubernetes manifests
├── docs/                        # Documentation
│   ├── architecture/           # System architecture docs
│   └── api/                    # API documentation
├── config/                      # Environment configurations
├── scripts/                     # Utility scripts
├── logs/                        # Application logs
└── app.py                       # Application entry point
```

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/true1ck/PROGUARD.git
   cd PROGUARD
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Web interface: http://localhost:5000
   - API documentation: http://localhost:5000/api/docs

### Production Deployment

#### Docker Deployment

```bash
# Build and run with Docker Compose
cd deployment/docker
docker-compose up -d
```

#### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/
```

## 🏢 Enterprise Features

### Multi-Environment Support

- **Development**: Local SQLite, debug mode, hot reloading
- **Production**: PostgreSQL, Gunicorn, Redis caching
- **Docker**: Containerized with orchestration support
- **Testing**: In-memory database, isolated test environment

### Security & Compliance

- Role-based access control (RBAC)
- Comprehensive audit logging
- Secure configuration management
- Input validation and SQL injection prevention
- Session security and CSRF protection

### Scalability & Performance

- Application factory pattern for multiple instances
- Database connection pooling
- Redis caching layer
- Horizontal scaling support
- Load balancer ready

### Monitoring & Observability

- Health check endpoints
- Structured logging with configurable levels
- Performance metrics collection
- Error tracking and alerting
- Database query monitoring

## 📊 Key Components

### 1. Dashboard Management
- **Vendor Dashboard**: Personal attendance tracking and status submission
- **Manager Dashboard**: Team oversight and approval workflows
- **Admin Dashboard**: System-wide administration and configuration

### 2. AI-Powered Insights
- Absence prediction algorithms
- Pattern recognition for attendance trends
- Risk assessment for team management
- Automated alert generation

### 3. Advanced Reporting
- Monthly attendance reports
- Team performance analytics
- Compliance reporting
- Export capabilities (Excel, PDF, CSV)
- Scheduled automated reports

### 4. Integration Capabilities
- Swipe machine data import
- HR system integration
- Leave management system sync
- External authentication (LDAP/AD ready)

### 5. Notification System
- Automated daily reminders
- Weekly summary reports
- Mismatch alerts
- Approval notifications

## 🔧 Configuration Management

### Environment Variables

```bash
# Application Settings
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/db

# Feature Toggles
NOTIFICATION_ENABLED=true
AI_PREDICTIONS_ENABLED=true
REPORTS_ENABLED=true

# External Services
REDIS_URL=redis://localhost:6379/0
SMTP_SERVER=smtp.company.com
```

### Configuration Files

Environment-specific configurations are managed in:
- `src/PROGUARD/config/settings.py`
- `config/environments/`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/PROGUARD

# Run specific test types
pytest tests/unit/
pytest tests/integration/
```

### Test Categories

- **Unit Tests**: Model validation, service logic, utility functions
- **Integration Tests**: API endpoints, database operations, external integrations
- **Performance Tests**: Load testing, stress testing, scalability validation

## 📚 API Documentation

### Interactive Documentation

Access the complete interactive API documentation at `/api/docs` when running the application.

### Key Endpoints

- **Authentication**: `/login`, `/logout`
- **Vendor APIs**: `/vendor/dashboard`, `/vendor/submit-status`
- **Manager APIs**: `/manager/dashboard`, `/manager/team-report`
- **Admin APIs**: `/admin/dashboard`, `/admin/ai-insights`
- **Reports**: `/api/reports/generate`, `/export/monthly-report`

## 🔄 Development Workflow

### Code Organization

- **Models**: Domain-specific models in separate files
- **Services**: Business logic separated from controllers
- **APIs**: RESTful endpoints organized by user role
- **Configuration**: Environment-specific settings management

### Best Practices

- Follow PEP 8 coding standards
- Use type hints for better code documentation
- Implement comprehensive error handling
- Write unit tests for all business logic
- Document APIs with OpenAPI/Swagger

## 🚀 Deployment Options

### Local Development
- Flask development server
- SQLite database
- Debug mode enabled

### Docker Container
- Multi-stage build process
- Production-optimized image
- Health checks included

### Kubernetes Cluster
- Horizontal pod autoscaling
- Rolling updates
- Persistent volume claims
- Ingress configuration

### Cloud Platforms
- AWS ECS/EKS ready
- Azure Container Instances/AKS compatible
- Google Cloud Run/GKE supported

## 📈 Performance & Monitoring

### Metrics Collected

- Request/response times
- Database query performance
- User activity patterns
- System resource utilization
- Error rates and types

### Monitoring Integration

- Prometheus metrics endpoint
- Grafana dashboard compatibility
- Application log aggregation
- Custom alerting rules

## 🔐 Security Considerations

### Authentication & Authorization

- Flask-Login session management
- Role-based access control
- Password hashing with salt
- Session timeout configuration

### Data Protection

- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF token validation

### Audit & Compliance

- Comprehensive audit logging
- Data retention policies
- Access control monitoring
- Compliance reporting capabilities

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

### Code Quality

- All code must pass linting checks
- Unit tests required for new features
- Documentation updates for API changes
- Security review for sensitive changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

For enterprise support and customization:
- Email: support@PROGUARD.com
- Documentation: [docs/](docs/)
- Issues: GitHub Issues
- Enterprise inquiries: enterprise@PROGUARD.com

---

**PROGUARD** - *Advanced Timesheet Tracking and Employee Notification Dashboard Operations*

