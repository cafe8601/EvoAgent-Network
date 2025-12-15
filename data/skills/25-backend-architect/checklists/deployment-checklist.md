# Deployment Checklist

Production readiness checklist for backend system deployments.

## Pre-Deployment

### Code Quality
- [ ] All tests passing (unit, integration, E2E)
- [ ] Test coverage meets threshold (>80%)
- [ ] No critical/high security vulnerabilities
- [ ] Code review approved
- [ ] Static analysis clean
- [ ] Dependency audit passed

### Build
- [ ] Docker image builds successfully
- [ ] Image tagged with version/commit SHA
- [ ] Image pushed to registry
- [ ] Image vulnerability scan passed
- [ ] Image size optimized

### Configuration
- [ ] Environment variables documented
- [ ] Secrets stored in secrets manager
- [ ] Feature flags configured
- [ ] External service URLs configured
- [ ] Resource limits set

### Database
- [ ] Migrations tested on staging
- [ ] Migrations are reversible
- [ ] Backup completed before migration
- [ ] Schema changes backward compatible
- [ ] Indexes verified

---

## Infrastructure

### Compute
- [ ] Sufficient replicas configured
- [ ] Auto-scaling policies set
- [ ] Resource requests/limits defined
- [ ] Anti-affinity rules configured
- [ ] Node selector/tolerations set

### Networking
- [ ] Load balancer configured
- [ ] SSL certificates valid
- [ ] DNS records updated
- [ ] Firewall rules configured
- [ ] Service mesh configured (if used)

### Storage
- [ ] Persistent volumes provisioned
- [ ] Storage class appropriate
- [ ] Backup policies configured
- [ ] Encryption at rest enabled

---

## Health & Monitoring

### Health Checks
- [ ] Liveness probe configured
- [ ] Readiness probe configured
- [ ] Startup probe configured (if needed)
- [ ] Health check endpoints tested
- [ ] Graceful shutdown configured

### Monitoring
- [ ] Metrics endpoint exposed
- [ ] Prometheus scraping configured
- [ ] Grafana dashboards created
- [ ] Log aggregation configured
- [ ] Distributed tracing enabled

### Alerting
- [ ] Error rate alerts configured
- [ ] Latency alerts configured
- [ ] Resource utilization alerts set
- [ ] PagerDuty/Slack integration tested
- [ ] Alert runbooks documented

---

## Security

### Authentication
- [ ] Authentication enabled
- [ ] API keys/tokens configured
- [ ] OAuth scopes defined
- [ ] Rate limiting enabled

### Network Security
- [ ] TLS 1.3 enforced
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] WAF rules active
- [ ] DDoS protection enabled

### Access Control
- [ ] RBAC policies applied
- [ ] Service account least privilege
- [ ] Secrets encrypted
- [ ] Network policies configured

---

## Deployment Strategy

### Rollout Plan
- [ ] Deployment strategy chosen (rolling/blue-green/canary)
- [ ] Rollback procedure documented
- [ ] Rollback tested
- [ ] Deployment window scheduled
- [ ] Stakeholders notified

### Canary (if applicable)
- [ ] Canary percentage configured
- [ ] Success metrics defined
- [ ] Promotion criteria clear
- [ ] Rollback triggers defined

---

## Post-Deployment

### Verification
- [ ] Smoke tests passing
- [ ] API endpoints responding
- [ ] Database connections working
- [ ] External integrations functioning
- [ ] Logs flowing correctly

### Monitoring
- [ ] Error rate normal
- [ ] Latency within SLO
- [ ] Resource utilization stable
- [ ] No memory leaks
- [ ] No connection pool exhaustion

### Documentation
- [ ] Deployment documented
- [ ] Changelog updated
- [ ] API documentation updated
- [ ] Runbook updated
- [ ] Incident channels notified

---

## Rollback Procedure

### Triggers
- [ ] Error rate > 1% for 5 minutes
- [ ] p99 latency > 2x baseline
- [ ] Critical functionality broken
- [ ] Data corruption detected
- [ ] Security incident

### Steps
1. [ ] Identify the issue
2. [ ] Notify stakeholders
3. [ ] Execute rollback command
4. [ ] Verify previous version healthy
5. [ ] Restore database if needed
6. [ ] Post-mortem scheduled

### Commands
```bash
# Kubernetes rollback
kubectl rollout undo deployment/api -n production

# Check rollout status
kubectl rollout status deployment/api -n production

# View rollout history
kubectl rollout history deployment/api -n production
```

---

## Environment Matrix

| Check | Staging | Production |
|-------|---------|------------|
| Health checks | [ ] | [ ] |
| Monitoring | [ ] | [ ] |
| Logging | [ ] | [ ] |
| Alerting | [ ] | [ ] |
| Secrets | [ ] | [ ] |
| SSL/TLS | [ ] | [ ] |
| Backup | [ ] | [ ] |
| Scaling | [ ] | [ ] |

---

## Sign-off

| Role | Name | Date | Approval |
|------|------|------|----------|
| Developer | | | [ ] |
| Tech Lead | | | [ ] |
| DevOps | | | [ ] |
| Security | | | [ ] |
| QA | | | [ ] |

---

## Emergency Contacts

| Role | Contact | Phone |
|------|---------|-------|
| On-call Engineer | | |
| DevOps Lead | | |
| Security | | |
| Database Admin | | |
| Manager | | |
