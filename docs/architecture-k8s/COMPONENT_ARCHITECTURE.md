# Component Architecture

## Overview

This document outlines the component architecture of Thinkube, a home-based development and experimentation platform built on Kubernetes. The focus is on practical deployment for a single environment with limited resources.

## Core Platform Components

The following components form the essential infrastructure:

### Infrastructure Layer
1. **MicroK8s** - Lightweight Kubernetes for home use
2. **CoreDNS + Ingress Controllers** - Network routing (2 NGINX controllers)
3. **Cert-Manager** - SSL certificates (self-signed or Let's Encrypt)
4. **GPU Operator** - GPU support for AI/ML workloads

### Security & Authentication
5. **Keycloak** - Single sign-on for all services
6. **Vault** (optional) - Secret management

### Storage & Data
7. **PostgreSQL** - Shared database instance
8. **MinIO** - S3-compatible object storage

### CI/CD & Deployment
9. **Harbor** - Container registry (critical for avoiding Docker Hub rate limits)
10. **Argo Workflows + Events** - Workflow automation
11. **ArgoCD** - GitOps deployment
12. **AWX** - Ansible automation for deploying optional components

### Monitoring
13. **Prometheus** - Metrics collection
14. **Grafana** - Dashboards and visualization

### Platform Management
15. **MkDocs** - Thinkube documentation
16. **Thinkube Dashboard** - Central control panel

## Currently Deployed Services

These services are working but could be managed as optional:

### Development Tools
- **JupyterHub** - Notebook environment with GPU support
- **Code Server** - Web-based VS Code
- **DevPi** - Python package repository

### AI/ML Infrastructure
- **MLflow** - Experiment tracking
- **Qdrant** - Vector database

### Data & Analytics
- **OpenSearch + Dashboards** - Search and log analysis
- **PgAdmin** - Database management

### Other Services
- **Knative** - Serverless platform
- **Penpot** - Design tool
- **Valkey** - Redis-compatible cache

## Optional Components (Deploy via AWX)

### Project Management
- **Wekan** - Simple Kanban board
- **Plane** - Project management
- **Vikunja** - Task management

### Collaboration
- **Gitea** - Git hosting
- **Outline** - Wiki/documentation
- **HedgeDoc** - Collaborative documents

### AI/ML Tools
- **ChromaDB** - Lightweight vector database
- **LangServe** - Deploy LLM applications
- **Label Studio** - Data labeling

### Databases
- **MongoDB** - Document database
- **ClickHouse** - Analytics database
- **Neo4j Community** - Graph database
- **TimescaleDB** - Time-series data

### Development Support
- **NATS** - Messaging system
- **Apache Superset** - Data visualization
- **DuckDB** - Embedded analytics

## Deployment Strategy

### Single Environment Approach
- One cluster for everything (no dev/prod separation)
- Deploy carefully - no rolling updates or zero-downtime
- Test changes during low-usage hours
- Keep backups of critical data

### Resource Management
- Start with core components only
- Add optional services as needed
- Remove unused services to free resources
- Monitor resource usage via Grafana

### AWX Templates
```yaml
awx_job_templates:
  - deploy_service    # Install new component
  - remove_service    # Uninstall component
  - backup_data      # Backup to MinIO
  - update_service   # Update existing service
```

## Hardware Considerations

### Minimum Requirements
- Control node: 8GB RAM, 4 cores
- Worker nodes: 16GB RAM, 8 cores
- GPU: Optional but recommended for AI workloads
- Storage: 500GB minimum

### Resource Optimization
- Use NodePort or ClusterIP instead of LoadBalancer
- Limit replicas to 1 for most services
- Adjust resource requests/limits based on actual usage
- Consider time-based scheduling for heavy workloads

## Component Management

### Thinkube Dashboard Features
```yaml
dashboard_features:
  - service_toggle      # Enable/disable components
  - resource_monitor    # CPU/Memory/GPU usage
  - service_status     # Health checks
  - quick_actions      # Common operations
  - awx_launcher       # Deploy new services
```

### Deployment Workflow
1. Check available resources
2. Deploy via AWX or direct kubectl
3. Verify service is working
4. Update documentation
5. Monitor resource impact

## Maintenance

### Backup Strategy
- PostgreSQL: Regular pg_dump to MinIO
- Persistent volumes: Velero to MinIO
- Configuration: Git repository
- Container images: Harbor registry

### Updates
- Plan updates during downtime
- Backup data before updates
- Test in isolated namespace if possible
- Have rollback plan ready

## Cost Optimization

### Power Management
- Schedule GPU-intensive tasks
- Shut down unused nodes
- Use wake-on-LAN for on-demand access

### Storage
- Clean up old container images
- Rotate logs and metrics
- Archive unused data to MinIO

## Service Selection Criteria

When choosing components:
1. Open source without commercial pressure
2. Low resource requirements
3. Provides real value for experiments
4. Easy to deploy and maintain
5. Good documentation

## Common Use Cases

### AI/ML Development
- JupyterHub for notebooks
- MLflow for experiment tracking
- Qdrant for vector search
- Harbor for model containers

### Web Development
- Code Server for IDE
- PostgreSQL for data
- MinIO for file storage
- ArgoCD for deployments

### Data Analysis
- OpenSearch for log analysis
- Grafana for visualization
- ClickHouse for analytics
- Superset for dashboards

## Troubleshooting

### Common Issues
- Resource exhaustion: Check Grafana, remove unused services
- Service failures: Check logs via kubectl or OpenSearch
- Network issues: Verify DNS and ingress configuration
- Storage full: Clean up images and logs

### Recovery Procedures
- Service won't start: Check events and logs
- Database corruption: Restore from MinIO backup
- Node failure: Rejoin to cluster or rebuild
- Complete failure: Reinstall from Ansible playbooks