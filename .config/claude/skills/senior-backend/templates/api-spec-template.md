# API Specification: {api_name}

## Overview

| Field | Value |
|-------|-------|
| Base URL | {base_url} |
| Auth | {auth_method} |
| Format | JSON |
| Version | {version} |

## Endpoints

### {METHOD} {path}

**Purpose:** {description}

**Request:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| {param} | {type} | {yes/no} | {desc} |

**Response (200):**
```json
{response_example}
```

**Errors:**
| Code | Meaning |
|------|---------|
| 400 | {description} |
| 401 | Unauthorized |
| 404 | Not found |

## Rate Limits

| Tier | Limit |
|------|-------|
| Default | {n} req/min |
