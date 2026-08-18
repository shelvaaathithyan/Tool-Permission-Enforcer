# Architecture

## System Overview
The Tool Permission Enforcer intercepts operations from AI agents and restricts their actions to a minimal security envelope via a permission proxy. 

## Component Data Flow

```
User
  ↓
AI Agent
  ↓
Tool Permission Proxy
  ↓
Permission Evaluation
  ↓
ALLOW / BLOCK
  ↓
Mock CRM Tool
  ↓
PostgreSQL
```

## Security Pipeline Flow

```
Permission Proxy
  ↓
Audit Log
```

```
Permission Proxy
  ↓
Violation Counter
  ↓
Security Alert
  ↓
Admin/Security Dashboard
```

## Implementation Status

### CURRENTLY IMPLEMENTED
- Production-ready scaffolding (FastAPI backend, React frontend).
- Dockerized setup and initial database connectivity.
- Configured health-check endpoints.
- Environment-based configuration management.

### PLANNED / FUTURE
- Permission Proxy and validation logic.
- Agent and Mock CRM Tool business logic.
- Audit Logging and Violation Counters.
- Security Alerts and Admin Dashboard functionalities.
- Database tables and active migrations.
