# Deployment Guide

This document provides comprehensive guidance for deploying the Automated Large-Text Field Extraction Solution in various environments. It covers deployment prerequisites, installation procedures, configuration options, and operational considerations.

## Deployment Architecture

The Automated Large-Text Field Extraction Solution can be deployed in various configurations depending on the specific requirements and constraints of the target environment. This section outlines the recommended deployment architectures.

### Standalone Deployment

The standalone deployment is suitable for development, testing, and small-scale production environments. In this configuration, all components run on a single server or virtual machine.

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Single Server/VM                        │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐    │
│  │ API Service │   │ Extraction  │   │ Configuration   │    │
│  │             │◄──┤ Pipeline    │◄──┤ Service         │    │
│  └─────────────┘   └─────────────┘   └─────────────────┘    │
│         │                 │                   │             │
│         ▼                 ▼                   ▼             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐    │
│  │ Logging     │   │ LLM Client  │   │ Error Handling  │    │
│  │ Service     │   │             │   │ Service         │    │
│  └─────────────┘   └─────────────┘   └─────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Resource Requirements

- **CPU**: 4+ cores (8+ recommended)
- **Memory**: 8+ GB RAM (16+ GB recommended)
- **Disk**: 20+ GB (SSD recommended)
- **Network**: Reliable internet connection for LLM API access

### Distributed Deployment

The distributed deployment is suitable for large-scale production environments with high throughput requirements. In this configuration, components are distributed across multiple servers or containers for improved scalability and reliability.

#### Architecture Diagram

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  API Service    │   │  API Service    │   │  API Service    │
│  (Instance 1)   │   │  (Instance 2)   │   │  (Instance N)   │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                       Load Balancer                          │
└────────────────────────────────┬────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Message Queue / Bus                       │
└───────┬─────────────────┬─────────────────┬─────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  Extraction   │  │  Extraction   │  │  Extraction   │
│  Worker (1)   │  │  Worker (2)   │  │  Worker (N)   │
└───────────────┘  └───────────────┘  └───────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Shared Configuration                       │
└─────────────────────────────────────────────────────────────┘
```

#### Resource Requirements

- **API Servers**:
  - CPU: 2+ cores per instance
  - Memory: 4+ GB RAM per instance
  - Disk: 10+ GB per instance
  - Instances: 2+ for high availability

- **Extraction Workers**:
  - CPU: 4+ cores per worker
  - Memory: 8+ GB RAM per worker
  - Disk: 20+ GB per worker
  - Workers: Based on throughput requirements

- **Message Queue**:
  - CPU: 2+ cores
  - Memory: 4+ GB RAM
  - Disk: 20+ GB
  - High availability configuration recommended

- **Load Balancer**:
  - CPU: 2+ cores
  - Memory: 4+ GB RAM
  - Network: High bandwidth capacity

### Containerized Deployment

The containerized deployment uses Docker containers and Kubernetes for orchestration, providing flexibility, scalability, and portability across different environments.

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 API Service Deployment              │    │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐           │    │
│  │  │ Pod 1   │   │ Pod 2   │   │ Pod N   │           │    │
│  │  └─────────┘   └─────────┘   └─────────┘           │    │
│  └──────────────────────────┬──────────────────────────┘    │
│                             │                               │
│  ┌──────────────────────────▼──────────────────────────┐    │
│  │                 Extraction Deployment               │    │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐           │    │
│  │  │ Pod 1   │   │ Pod 2   │   │ Pod N   │           │    │
│  │  └─────────┘   └─────────┘   └─────────┘           │    │
│  └──────────────────────────┬──────────────────────────┘    │
│                             │                               │
│  ┌──────────────────────────▼──────────────────────────┐    │
│  │                 Shared Services                      │    │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────┐    │    │
│  │  │ Config      │   │ Logging     │   │ Redis   │    │    │
│  │  │ Service     │   │ Service     │   │ Cache   │    │    │
│  │  └─────────────┘   └─────────────┘   └─────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Resource Requirements

- **Kubernetes Cluster**:
  - Worker Nodes: 3+ (for high availability)
  - CPU: 4+ cores per node
  - Memory: 16+ GB RAM per node
  - Disk: 50+ GB per node
  - Network: High bandwidth, low latency

- **Container Resources**:
  - API Service: 1 CPU, 2 GB RAM per pod
  - Extraction Service: 2 CPU, 4 GB RAM per pod
  - Config Service: 0.5 CPU, 1 GB RAM per pod
  - Logging Service: 0.5 CPU, 1 GB RAM per pod
  - Redis Cache: 1 CPU, 2 GB RAM per pod

## Prerequisites

### System Requirements

#### Operating System

- **Linux**: Ubuntu 20.04+, CentOS 8+, or Amazon Linux 2
- **macOS**: 10.15 (Catalina)+ for development
- **Windows**: Windows 10/11 with WSL2 for development

#### Software Dependencies

- **Python**: 3.9+
- **Docker**: 20.10+ (for containerized deployment)
- **Kubernetes**: 1.22+ (for containerized deployment)
- **Redis**: 6.0+ (for distributed deployment)
- **RabbitMQ**: 3.8+ (for distributed deployment)

#### Network Requirements

- **Outbound Access**: 
  - OpenAI API (api.openai.com)
  - Other LLM APIs as configured
- **Inbound Access**:
  - API service port (default: 8000)
  - Monitoring port (default: 9090)

### External Services

#### LLM API Access

- **OpenAI API Key**: Required for accessing OpenAI models
- **Alternative LLM API Keys**: As needed for configured models

#### Monitoring Services (Optional)

- **Prometheus**: For metrics collection
- **Grafana**: For metrics visualization
- **ELK Stack**: For log aggregation and analysis

## Installation

### Standalone Installation

#### Using pip

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package:
   ```bash
   pip install dudoxx-extraction
   ```

3. Create configuration files:
   ```bash
   dudoxx-extraction init-config --output-dir ./config
   ```

4. Edit configuration files in the `./config` directory.

5. Run the service:
   ```bash
   dudoxx-extraction start --config-dir ./config
   ```

#### Using Docker

1. Pull the Docker image:
   ```bash
   docker pull dudoxx/extraction:latest
   ```

2. Create a configuration directory:
   ```bash
   mkdir -p ./config
   ```

3. Generate default configuration:
   ```bash
   docker run --rm -v $(pwd)/config:/config dudoxx/extraction:latest init-config
   ```

4. Edit configuration files in the `./config` directory.

5. Run the container:
   ```bash
   docker run -d --name dudoxx-extraction \
     -v $(pwd)/config:/app/config \
     -p 8000:8000 \
     -e OPENAI_API_KEY=your_api_key \
     dudoxx/extraction:latest
   ```

### Distributed Installation

#### Using Docker Compose

1. Create a project directory:
   ```bash
   mkdir dudoxx-extraction && cd dudoxx-extraction
   ```

2. Create a `docker-compose.yml` file:
   ```yaml
   version: '3.8'
   
   services:
     api:
       image: dudoxx/extraction-api:latest
       ports:
         - "8000:8000"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - REDIS_HOST=redis
         - RABBITMQ_HOST=rabbitmq
       volumes:
         - ./config:/app/config
       depends_on:
         - redis
         - rabbitmq
     
     worker:
       image: dudoxx/extraction-worker:latest
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - REDIS_HOST=redis
         - RABBITMQ_HOST=rabbitmq
       volumes:
         - ./config:/app/config
       depends_on:
         - redis
         - rabbitmq
       deploy:
         replicas: 3
     
     redis:
       image: redis:6-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis-data:/data
     
     rabbitmq:
       image: rabbitmq:3-management
       ports:
         - "5672:5672"
         - "15672:15672"
       volumes:
         - rabbitmq-data:/var/lib/rabbitmq
   
   volumes:
     redis-data:
     rabbitmq-data:
   ```

3. Create a configuration directory:
   ```bash
   mkdir -p ./config
   ```

4. Generate default configuration:
   ```bash
   docker run --rm -v $(pwd)/config:/config dudoxx/extraction-api:latest init-config
   ```

5. Edit configuration files in the `./config` directory.

6. Set the OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key
   ```

7. Start the services:
   ```bash
   docker-compose up -d
   ```

### Kubernetes Installation

1. Create a namespace:
   ```bash
   kubectl create namespace dudoxx
   ```

2. Create a secret for the OpenAI API key:
   ```bash
   kubectl create secret generic openai-api-key \
     --from-literal=OPENAI_API_KEY=your_api_key \
     --namespace dudoxx
   ```

3. Create a ConfigMap for configuration:
   ```bash
   # Generate default configuration
   mkdir -p ./config
   docker run --rm -v $(pwd)/config:/config dudoxx/extraction-api:latest init-config
   
   # Create ConfigMap
   kubectl create configmap dudoxx-config \
     --from-file=./config \
     --namespace dudoxx
   ```

4. Apply Kubernetes manifests:
   ```bash
   kubectl apply -f kubernetes/redis.yaml -n dudoxx
   kubectl apply -f kubernetes/rabbitmq.yaml -n dudoxx
   kubectl apply -f kubernetes/extraction-api.yaml -n dudoxx
   kubectl apply -f kubernetes/extraction-worker.yaml -n dudoxx
   ```

5. Verify deployment:
   ```bash
   kubectl get pods -n dudoxx
   ```

## Configuration

### Configuration Files

The Automated Large-Text Field Extraction Solution uses a hierarchical configuration system with the following files:

#### config.json

The main configuration file that defines global settings:

```json
{
  "chunking": {
    "max_chunk_size": 16000,
    "overlap_size": 200,
    "default_strategy": "paragraph"
  },
  "processing": {
    "max_concurrency": 20,
    "retry_attempts": 3,
    "timeout": 60
  },
  "extraction": {
    "model_name": "gpt-4",
    "temperature": 0.0
  },
  "normalization": {
    "date_format": "%Y-%m-%d"
  },
  "merging": {
    "deduplication_threshold": 0.9
  },
  "formatting": {
    "include_metadata": true,
    "default_formats": ["json", "text"]
  },
  "logging": {
    "level": "info",
    "file": "logs/extraction.log",
    "max_size": 10485760,
    "backup_count": 5
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "timeout": 300
  }
}
```

#### domains/medical.json

Domain-specific configuration for medical documents:

```json
{
  "chunking": {
    "default_strategy": "section"
  },
  "fields": [
    {
      "name": "patient_name",
      "description": "Full name of the patient",
      "type": "string",
      "is_unique": true
    },
    {
      "name": "date_of_birth",
      "description": "Patient's date of birth in YYYY-MM-DD format",
      "type": "date",
      "validation_regex": "^\\d{4}-\\d{2}-\\d{2}$",
      "is_unique": true
    },
    {
      "name": "diagnoses",
      "description": "Medical diagnoses",
      "type": "string",
      "is_unique": false
    },
    {
      "name": "medications",
      "description": "Prescribed medications",
      "type": "string",
      "is_unique": false
    },
    {
      "name": "visits",
      "description": "Medical visits",
      "type": "timeline",
      "date_field": "date",
      "is_unique": false
    }
  ],
  "timeline": {
    "events_field": "visits",
    "date_field": "date",
    "event_fields": ["description", "treatment"],
    "sort_ascending": true,
    "merge_same_day": true
  }
}
```

### Environment Variables

The following environment variables can be used to override configuration settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | None (Required) |
| `EXTRACTION_CONFIG_DIR` | Directory containing configuration files | `./config` |
| `EXTRACTION_LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` |
| `EXTRACTION_API_HOST` | API service host | `0.0.0.0` |
| `EXTRACTION_API_PORT` | API service port | `8000` |
| `EXTRACTION_MAX_CONCURRENCY` | Maximum concurrent LLM requests | `20` |
| `EXTRACTION_MODEL_NAME` | Default LLM model name | `gpt-4` |
| `EXTRACTION_REDIS_HOST` | Redis host for distributed deployment | `localhost` |
| `EXTRACTION_REDIS_PORT` | Redis port for distributed deployment | `6379` |
| `EXTRACTION_RABBITMQ_HOST` | RabbitMQ host for distributed deployment | `localhost` |
| `EXTRACTION_RABBITMQ_PORT` | RabbitMQ port for distributed deployment | `5672` |

## API Usage

### RESTful API

The Automated Large-Text Field Extraction Solution provides a RESTful API for integration with other systems.

#### Authentication

API authentication uses API keys passed in the `Authorization` header:

```
Authorization: Bearer your_api_key
```

#### Endpoints

##### Extract Fields

```
POST /api/v1/extract
```

Request body:
```json
{
  "document": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
  "fields": ["patient_name", "date_of_birth", "diagnosis"],
  "domain": "medical",
  "output_formats": ["json", "text"]
}
```

Response:
```json
{
  "json_output": {
    "patient_name": "John Doe",
    "date_of_birth": "1980-05-15",
    "diagnosis": "Diabetes mellitus Type II"
  },
  "text_output": "patient_name: John Doe\ndate_of_birth: 1980-05-15\ndiagnosis: Diabetes mellitus Type II",
  "metadata": {
    "processing_time": 1.234,
    "chunk_count": 1,
    "token_count": 150
  }
}
```

##### Get Domains

```
GET /api/v1/domains
```

Response:
```json
{
  "domains": [
    {
      "name": "medical",
      "description": "Medical documents",
      "fields": [
        "patient_name",
        "date_of_birth",
        "diagnoses",
        "medications",
        "visits"
      ]
    },
    {
      "name": "legal",
      "description": "Legal documents",
      "fields": [
        "parties",
        "effective_date",
        "termination_date",
        "obligations",
        "events"
      ]
    }
  ]
}
```

##### Get Domain Fields

```
GET /api/v1/domains/{domain}/fields
```

Response:
```json
{
  "fields": [
    {
      "name": "patient_name",
      "description": "Full name of the patient",
      "type": "string",
      "is_unique": true
    },
    {
      "name": "date_of_birth",
      "description": "Patient's date of birth in YYYY-MM-DD format",
      "type": "date",
      "validation_regex": "^\\d{4}-\\d{2}-\\d{2}$",
      "is_unique": true
    },
    {
      "name": "diagnoses",
      "description": "Medical diagnoses",
      "type": "string",
      "is_unique": false
    },
    {
      "name": "medications",
      "description": "Prescribed medications",
      "type": "string",
      "is_unique": false
    },
    {
      "name": "visits",
      "description": "Medical visits",
      "type": "timeline",
      "date_field": "date",
      "is_unique": false
    }
  ]
}
```

##### Health Check

```
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "api": "healthy",
    "extraction": "healthy",
    "llm_client": "healthy"
  }
}
```

### Python Client

The Automated Large-Text Field Extraction Solution provides a Python client for easy integration:

```python
from dudoxx_extraction import ExtractionClient

# Initialize client
client = ExtractionClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Extract fields
result = client.extract(
    document="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
    fields=["patient_name", "date_of_birth", "diagnosis"],
    domain="medical",
    output_formats=["json", "text"]
)

# Access results
json_output = result.json_output
text_output = result.text_output
processing_time = result.metadata["processing_time"]

print(f"Extracted fields: {json_output}")
print(f"Processing time: {processing_time} seconds")
```

## Monitoring and Maintenance

### Logging

The Automated Large-Text Field Extraction Solution uses structured logging to facilitate monitoring and troubleshooting:

#### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about system operation
- **WARNING**: Potential issues that don't affect operation
- **ERROR**: Errors that affect specific operations
- **CRITICAL**: Critical errors that affect system operation

#### Log Format

Logs are output in JSON format for easy parsing and analysis:

```json
{
  "timestamp": "2023-05-15T10:30:45.123456",
  "level": "INFO",
  "message": "Processing document",
  "context": {
    "correlation_id": "abc123",
    "request_id": "req456"
  },
  "metadata": {
    "document_id": "doc123",
    "size": 1024,
    "log_id": "mno345"
  }
}
```

#### Log Storage

Logs are stored in the following locations:

- **Console**: Standard output/error
- **File**: `logs/extraction.log` (configurable)
- **External Services**: Optional integration with ELK Stack, Datadog, etc.

### Metrics

The Automated Large-Text Field Extraction Solution exposes metrics for monitoring system performance:

#### Available Metrics

- **Request Rate**: Requests per minute
- **Processing Time**: Time to process documents
- **Error Rate**: Errors per minute
- **Chunk Count**: Number of chunks processed
- **Token Usage**: Number of tokens used
- **Concurrency**: Number of concurrent requests
- **Queue Length**: Number of queued requests

#### Metrics Endpoints

Metrics are exposed via Prometheus-compatible endpoints:

```
GET /metrics
```

### Health Checks

The Automated Large-Text Field Extraction Solution provides health check endpoints for monitoring system health:

#### Health Check Endpoints

```
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "api": "healthy",
    "extraction": "healthy",
    "llm_client": "healthy"
  }
}
```

### Backup and Restore

#### Configuration Backup

To backup configuration:

```bash
tar -czf dudoxx-config-backup.tar.gz ./config
```

To restore configuration:

```bash
tar -xzf dudoxx-config-backup.tar.gz -C /path/to/restore
```

#### Database Backup (if applicable)

For Redis:

```bash
# Backup
redis-cli -h localhost -p 6379 --rdb redis-backup.rdb

# Restore
systemctl stop redis
cp redis-backup.rdb /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb
systemctl start redis
```

### Upgrades

#### Standalone Upgrade

Using pip:

```bash
pip install --upgrade dudoxx-extraction
```

Using Docker:

```bash
docker pull dudoxx/extraction:latest
docker stop dudoxx-extraction
docker rm dudoxx-extraction
docker run -d --name dudoxx-extraction \
  -v $(pwd)/config:/app/config \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key \
  dudoxx/extraction:latest
```

#### Distributed Upgrade

Using Docker Compose:

```bash
docker-compose pull
docker-compose up -d
```

Using Kubernetes:

```bash
kubectl set image deployment/dudoxx-api api=dudoxx/extraction-api:latest -n dudoxx
kubectl set image deployment/dudoxx-worker worker=dudoxx/extraction-worker:latest -n dudoxx
```

## Troubleshooting

### Common Issues

#### API Connection Issues

**Symptoms**:
- Unable to connect to API
- Connection timeouts
- Connection refused errors

**Solutions**:
1. Verify API service is running:
   ```bash
   docker ps | grep dudoxx
   # or
   kubectl get pods -n dudoxx
   ```

2. Check API logs:
   ```bash
   docker logs dudoxx-extraction
   # or
   kubectl logs deployment/dudoxx-api -n dudoxx
   ```

3. Verify network connectivity:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

#### LLM API Issues

**Symptoms**:
- Extraction failures
- Timeout errors
- API key errors

**Solutions**:
1. Verify API key is set correctly:
   ```bash
   # Check environment variable
   echo $OPENAI_API_KEY
   
   # Check container environment
   docker exec dudoxx-extraction env | grep OPENAI_API_KEY
   ```

2. Check LLM API status:
   - OpenAI Status: https://status.openai.com/

3. Verify network connectivity to LLM API:
   ```bash
   curl -I https://api.openai.com/v1/models
   ```

#### Performance Issues

**Symptoms**:
- Slow processing times
- High resource usage
- Request timeouts

**Solutions**:
1. Check system resources:
   ```bash
   # CPU and memory usage
   top
   
   # Disk usage
   df -h
   ```

2. Adjust concurrency settings:
   ```bash
   # Edit config.json
   {
     "processing": {
       "max_concurrency": 10  # Reduce from default
     }
   }
   ```

3. Monitor metrics:
   ```bash
   curl http://localhost:8000/metrics
   ```

### Diagnostic Tools

#### Log Analysis

To analyze logs:

```bash
# Search for errors
grep ERROR logs/extraction.log

# Search for specific request
grep "request_id=req123" logs/extraction.log

# Analyze processing times
grep "Processing completed" logs/extraction.log | awk '{print $8}' | sort -n
```

#### Performance Profiling

To profile API performance:

```bash
# Install wrk
apt-get install -y wrk

# Run benchmark
wrk -t4 -c50 -d30s -s benchmark.lua http://localhost:8000/api/v1/health
```

#### Debug Mode

To enable debug logging:

```bash
# Set environment variable
export EXTRACTION_LOG_LEVEL=debug

# Restart service
docker restart dudoxx-extraction
```

### Support Resources

- **Documentation**: https://docs.dudoxx.ai/extraction
- **GitHub Issues**: https://github.com/dudoxx/extraction/issues
- **Community Forum**: https://community.dudoxx.ai
- **Email Support**: support@dudoxx.ai

## Security Considerations

### API Security

- Use HTTPS for all API communications
- Implement API key authentication
- Use rate limiting to prevent abuse
- Validate all input data

### Data Security

- Do not store sensitive documents
- Process data in memory only
- Implement data encryption in transit
- Follow data retention policies

### Access Control

- Use principle of least privilege
- Implement role-based access control
- Audit access to sensitive operations
- Rotate API keys regularly

### Compliance

- Ensure GDPR compliance for EU data
- Follow HIPAA guidelines for medical data
- Implement data processing agreements
- Maintain audit logs for compliance

## Conclusion

This deployment guide provides comprehensive instructions for deploying, configuring, and maintaining the Automated Large-Text Field Extraction Solution. By following these guidelines, you can ensure a successful deployment that meets your specific requirements and constraints.

For additional assistance, please refer to the support resources or contact the development team.
