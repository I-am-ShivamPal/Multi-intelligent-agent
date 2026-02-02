# Metrics & Logs Schema

## Naming Convention

### File Naming Pattern
```
{category}_{metric_type}_{environment}.csv
```

**Categories:**
- `deploy` - Deployment operations
- `heal` - Self-healing operations  
- `monitor` - System monitoring
- `perf` - Performance metrics
- `error` - Error tracking

**Metric Types:**
- `log` - Event logs (timestamped events)
- `rate` - Success/failure rates
- `time` - Timing metrics
- `count` - Counter metrics
- `health` - Health status

### Standard Schema

#### Core Fields (All Files)
```csv
timestamp,environment,agent_id,metric_value,status
```

#### Deployment Logs
**File:** `deploy_log_{env}.csv`
```csv
timestamp,environment,agent_id,dataset_path,status,response_time_ms,action_type
```

#### Deployment Metrics  
**File:** `deploy_rate_{env}.csv`
```csv
timestamp,environment,total_count,success_count,failure_count,success_rate_pct,avg_time_ms
```

#### Healing Logs
**File:** `heal_log_{env}.csv`
```csv
timestamp,environment,agent_id,issue_type,strategy,status,recovery_time_ms
```

#### System Health
**File:** `monitor_health_{env}.csv`
```csv
timestamp,environment,component,status,cpu_pct,memory_pct,uptime_sec
```

#### Performance Metrics
**File:** `perf_time_{env}.csv`
```csv
timestamp,environment,operation,response_time_ms,throughput_ops_sec
```

#### Error Tracking
**File:** `error_count_{env}.csv`
```csv
timestamp,environment,error_type,count,severity,component
```

## Directory Structure
```
logs/
├── {env}/
│   ├── deploy_log_{env}.csv
│   ├── deploy_rate_{env}.csv
│   ├── heal_log_{env}.csv
│   ├── monitor_health_{env}.csv
│   ├── perf_time_{env}.csv
│   └── error_count_{env}.csv
```

## Field Definitions

- `timestamp`: ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ffffff)
- `environment`: dev|stage|prod
- `agent_id`: Agent identifier (deploy_agent, heal_agent, etc.)
- `status`: success|failure|pending|error
- `response_time_ms`: Response time in milliseconds
- `success_rate_pct`: Success rate as percentage (0-100)
- `severity`: low|medium|high|critical