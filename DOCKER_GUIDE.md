# Docker Quick Start Guide

## Quick Commands

### Build and Start All Services
```bash
docker-compose up --build -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dashboard
docker-compose logs -f agents
docker-compose logs -f redis
```

### Check Service Status
```bash
docker-compose ps
```

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Full Reset)
```bash
docker-compose down -v
```

---

## Service URLs (After Starting)

| Service | URL | Description |
|---------|-----|-------------|
| Main Dashboard | http://localhost:8501 | Primary CI/CD dashboard |
| Observability | http://localhost:8502 | Metrics & monitoring |
| Redis | localhost:6379 | Event bus |

---

## Container Services

### Core Services
- **dashboard**: Main Streamlit dashboard (port 8501)
- **observability**: Observability dashboard (port 8502)
- **agents**: Main CI/CD agents
- **redis**: Redis event bus
- **queue-monitor**: Redis queue monitoring

### Worker Services
- **deploy-worker-1/2/3**: Deploy workers (3 instances)
- **health-monitor**: System health monitoring

---

## Common Tasks

### Restart Specific Service
```bash
docker-compose restart agents
```

### View Container Resources
```bash
docker stats
```

### Execute Command in Container
```bash
docker exec -it cicd-agents python demo_run.py
```

### Access Container Shell
```bash
docker exec -it cicd-agents /bin/bash
```

### View Redis Data
```bash
docker exec -it cicd-redis redis-cli
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs [service-name]

# Rebuild without cache
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker exec -it cicd-redis redis-cli ping
```

### Port Conflicts
```bash
# Check what's using port 8501
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac

# Change port in docker-compose.yml if needed
```

---

## Health Checks

All services have health checks configured:
- Redis: Pings every 10s
- Dashboard: Checks Streamlit health endpoint every 30s
- Agents: Validates log file existence every 30s

View health status:
```bash
docker-compose ps
```

---

## Volume Management

### Backup Logs
```bash
docker cp cicd-agents:/app/logs ./logs_backup
```

### Clear Redis Data
```bash
docker-compose down
docker volume rm multi-intelligent-agent-system-main_redis_data
docker-compose up -d
```

---

## Production Deployment

### Build for Production
```bash
docker-compose -f docker-compose.yml up -d --build
```

### Environment Variables
Create `.env` file:
```env
REDIS_HOST=redis
REDIS_PORT=6379
PLANNER_TYPE=rl
DATASET_PATH=dataset/student_scores.csv
```

Then:
```bash
docker-compose --env-file .env up -d
```

---

## Demo in Docker

### Run Demo Inside Container
```bash
docker exec -it cicd-agents python demo_run.py
```

### View Proof Logs
```bash
docker exec -it cicd-agents cat logs/day1_proof.log
```

---

## Updates Applied

### Dockerfile Improvements
- ✅ Added comprehensive directory creation
- ✅ Set Python environment variables
- ✅ Improved health checks
- ✅ Multi-port exposure (8501, 8080, 5000)

### docker-compose.yml Improvements
- ✅ Added observability dashboard service
- ✅ Added health monitoring service
- ✅ Improved health checks with conditions
- ✅ Better restart policies (unless-stopped)
- ✅ Redis optimization (maxmemory, LRU policy)
- ✅ Proper service dependencies

### .dockerignore Added
- ✅ Reduced image size
- ✅ Excluded test files
- ✅ Excluded unnecessary documentation
- ✅ Excluded cache files
