---
title: Notification Prioritization Env
emoji: 🔔
colorFrom: blue
colorTo: purple
sdk: docker
tags:
  - openenv
pinned: false
license: mit
---

# 🔔 Notification Prioritization Environment

An OpenEnv-compatible environment where AI agents learn to triage and prioritize real-world notifications.

## 🎯 Problem Statement

Modern users receive hundreds of notifications daily. This environment challenges AI agents to:
- Classify notifications by category
- Rank notifications by urgency
- Take appropriate actions and summarize critical alerts

## 🚀 Live API

Base URL: https://kammalakshmi-notification-prioritization-env.hf.space

## 📋 Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| task1 | Easy | Classify 8 notifications into 4 categories: urgent, informational, promotional, social |
| task2 | Medium | Rank 15 notifications by urgency (1 = most urgent) |
| task3 | Hard | Triage 30 notifications — choose action and summarize escalated ones |

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Health check |
| /reset | POST | Start a new episode |
| /step | POST | Submit agent action and get reward |
| /state | GET | Get current environment state |
| /tasks | GET | List all available tasks |
| /grader | POST | Get score after episode |
| /docs | GET | Interactive API documentation |

## 🧪 Quick Test

### 1. Health Check
\\\ash
curl https://kammalakshmi-notification-prioritization-env.hf.space/
\\\

### 2. Reset Environment
\\\ash
curl -X POST https://kammalakshmi-notification-prioritization-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task1", "seed": 42}'
\\\

### 3. Submit Action
\\\ash
curl -X POST https://kammalakshmi-notification-prioritization-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task1", "labels": [{"notification_id": "notif_000", "category": "urgent"}]}'
\\\

## 📊 Grading

| Task | Grading Method |
|------|---------------|
| task1 | Exact + partial category match |
| task2 | Kendall-tau ranking similarity |
| task3 | Weighted action accuracy + summary quality |

## 🛠️ Tech Stack

- **FastAPI** — REST API framework
- **Docker** — containerized deployment
- **Pydantic** — data validation
- **Uvicorn** — ASGI server

## 👩‍💻 Author

Kammalakshmi — Built for OpenEnv Hackathon 2026
