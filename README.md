# AI Trading Analysis Platform

A modern, API-only backend for a trading platform that leverages AI (LLM) to generate technical analysis signals for cryptocurrency markets. Built for scalability, maintainability, and ease of deployment.

---

## 🚀 Features
- **JWT Authentication** with email verification (dj-rest-auth, django-allauth)
- **Automated Data Pipeline**: Scheduled fetching and pruning of market data (Celery, Celery Beat)
- **AI-Powered Signal Generation**: Uses a real LLM (via OpenAI API, integrated through Liara AI API for free ChatGPT access)
- **Market Data from KuCoin**: Fetches cryptocurrency chart data using the KuCoin API
- **Redis Caching**: Fast retrieval of latest signals
- **Conversational AI Chat**: Context-aware trading assistant for authenticated users (powered by Liara AI API)
- **Asynchronous Processing**: All heavy tasks run in the background
- **Interactive API Docs**: Auto-generated with drf-spectacular (Swagger UI)
- **Containerized**: Full Docker & Docker Compose support for local and production

---

## 🛠️ Tech Stack
- **Language:** Python 3.12
- **Framework:** Django 5.x
- **API:** Django REST Framework
- **Database:** PostgreSQL
- **Cache & Broker:** Redis
- **Async Tasks:** Celery & Celery Beat
- **Auth:** dj-rest-auth, djangorestframework-simplejwt, django-allauth
- **API Docs:** drf-spectacular
- **AI Integration:** openai (via Liara AI API for free ChatGPT)
- **Market Data:** KuCoin API
- **Containerization:** Docker, Docker Compose

See `requirements.txt` for all Python dependencies.

---

## ⚡ Quickstart

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 2. Clone the Repository
```bash
git clone <your-github-repository-url>
cd <project-folder>
```

### 3. Configure Environment Variables
- Create a `.env` file in the project root with the following variables:
  - `SECRET_KEY`
  - `DEBUG`
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`
  - `LIARA_API_KEY` (for AI integration)
  - (See `docker-compose.yml` and `settings.py` for all required variables)

### 4. Build and Start the Stack
```bash
docker-compose up --build
```

### 5. Apply Database Migrations
```bash
docker-compose exec app python manage.py migrate
```

### 6. Create a Superuser (for Django Admin)
```bash
docker-compose exec app python manage.py createsuperuser
```

---

## 🌐 Access Points
- **Main API:** http://localhost:8000/
- **API Docs (Swagger):** http://localhost:8000/docs/
- **Django Admin:** http://localhost:8000/admin/

---

## 📚 Documentation
- All endpoints are documented and testable via Swagger UI at `/docs/`.
- For detailed API usage, see the auto-generated docs after running the project.
- **Note:**
  - The project uses the **Liara AI API** to provide free ChatGPT-powered conversational AI features.
  - Market chart data is fetched using the **KuCoin API**.

---

## 📝 Notes
- All configuration is via environment variables for security and flexibility.
- The project is fully containerized for easy local development and production deployment.
- Follows best practices for security, scalability, and maintainability.

---

## 📦 Project Structure (Simplified)
- `TradingAnalysisAi/` – Main Django project (settings, URLs, celery config)
- `accounts/`, `market_data/`, `ai_signals/`, `chat/` – Core apps
- `requirements.txt` – Python dependencies
- `docker-compose.yml`, `Dockerfile` – Containerization

---

For any questions or contributions, please open an issue or pull request.