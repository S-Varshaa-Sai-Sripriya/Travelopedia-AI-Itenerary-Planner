# AI Travel Planner - Project Setup

This is the base setup for the AI Travel Planner project. This document will help team members set up their development environment and start contributing.

## Project Overview

The AI Travel Planner is an intelligent, automated itinerary planning system that leverages:
- **Multi-Agent AI Architecture**: Orchestrated agents for different aspects of travel planning
- **Real-time Data Integration**: Live flight, hotel, and weather data
- **Graph Neural Networks (GNN)**: For personalized recommendations
- **Big Data Processing**: Kafka streams for real-time updates
- **Local-first Approach**: Constraint-aware validation engine

## Architecture Components

```
User Request → LLM Orchestrator → Real-time APIs → Personalization (GNN) → Decision Points → Automated Execution → User Response
```

### Key Agents:
1. **LLM Orchestrator**: Parses user requests and coordinates other agents
2. **GNN Agent**: Provides personalized recommendations based on user profile
3. **Budget Optimization Agent**: Balances cost vs convenience
4. **Itinerary Agent**: Consolidates decisions and automates bookings

## Quick Start

### Prerequisites
- Python 3.9+
- Git
- Redis (for caching and message queuing)
- Optional: Docker (for containerized development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/12-crypto/AI-Itenary.git
   cd AI-Itenary
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see API Keys section below)
   ```

5. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Project Structure

```
AI-Itenary/
├── app/                    # Main application code
│   ├── agents/            # AI agents (LLM, GNN, Budget, Itinerary)
│   ├── api/               # FastAPI routes and endpoints
│   ├── core/              # Core configuration and utilities
│   ├── models/            # Database models and schemas
│   ├── services/          # Business logic and external integrations
│   └── main.py           # FastAPI application entry point
├── data/                  # Data storage and processing
│   ├── raw/              # Raw data files
│   ├── processed/        # Processed datasets
│   └── models/           # Trained ML models
├── scripts/              # Utility scripts
├── tests/                # Test files
├── docs/                 # Documentation
├── docker/               # Docker configuration
├── notebooks/            # Jupyter notebooks for research
└── config/               # Configuration files
```

## Free APIs Used

### ✅ Completely Free APIs:
1. **Weather**: OpenWeatherMap (1000 calls/day free)
2. **Hotels**: Booking.com (free tier available)
3. **Flights**: Aviationstack (1000 requests/month free)
4. **Maps/Places**: OpenStreetMap + Nominatim (free)
5. **Currency**: Fixer.io (100 requests/month free)
6. **LLM**: Ollama (local inference, completely free)

### ⚠️ Freemium APIs (with generous free tiers):
1. **OpenAI**: $5 free credit for new accounts
2. **Hugging Face**: Free tier for model inference
3. **Redis Cloud**: 30MB free tier

### 💰 Paid APIs with Free Alternatives:
- **Google Maps API** → **OpenStreetMap + Nominatim** (free alternative)
- **Amadeus Travel API** → **Aviationstack** (free alternative)
- **AWS/Azure** → **Local development** (free alternative)

## API Keys Setup

Create a `.env` file with the following keys:

```env
# Core Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./travel_planner.db

# AI/LLM Configuration
OPENAI_API_KEY=your-openai-key  # Optional: $5 free credit
HUGGINGFACE_API_KEY=your-hf-key  # Free tier available
OLLAMA_BASE_URL=http://localhost:11434  # Local LLM (free)

# Travel APIs (All Free Tiers)
OPENWEATHER_API_KEY=your-openweather-key  # 1000 calls/day free
AVIATIONSTACK_API_KEY=your-aviationstack-key  # 1000 requests/month free
FIXER_API_KEY=your-fixer-key  # 100 requests/month free

# Infrastructure
REDIS_URL=redis://localhost:6379  # Local Redis
KAFKA_BOOTSTRAP_SERVERS=localhost:9092  # Local Kafka

# Optional Integrations
BOOKING_API_KEY=your-booking-key  # Free tier available
CALENDAR_WEBHOOK_URL=your-webhook-url  # For calendar sync
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/

# Format code
black .
flake8 .

# Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### 2. Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents/test_llm_orchestrator.py

# Run with coverage
pytest --cov=app tests/
```

### 3. Code Quality
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## Getting API Keys (Free)

### 1. OpenWeatherMap (Weather Data)
- Visit: https://openweathermap.org/api
- Sign up for free account
- Get API key (1000 calls/day free)

### 2. Aviationstack (Flight Data)
- Visit: https://aviationstack.com/
- Free plan: 1000 requests/month
- Sign up and get API key

### 3. Fixer.io (Currency Exchange)
- Visit: https://fixer.io/
- Free plan: 100 requests/month
- Sign up and get API key

### 4. Ollama (Local LLM - Completely Free)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama server
ollama serve
```

## Team Collaboration Guidelines

### 1. Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical fixes

### 2. Commit Convention
```
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: add or update tests
chore: maintenance tasks
```

### 3. Code Review Process
1. Create feature branch
2. Implement feature with tests
3. Create pull request
4. Code review by team member
5. Merge to develop
6. Deploy to staging
7. Merge to main for production

### 4. Communication
- Daily standups: Progress updates
- Weekly retrospectives: Process improvements
- Slack/Discord: Real-time communication
- GitHub Issues: Task tracking

## Deployment Options

### Local Development
```bash
uvicorn app.main:app --reload
```

### Docker (Recommended for consistency)
```bash
docker-compose up -d
```

### Production (Free Options)
1. **Railway**: Free tier available
2. **Fly.io**: Free tier available
3. **Heroku**: Free tier (limited)
4. **Vercel**: Free tier for Python

## Monitoring and Logging

- **Local**: Structured logging with `structlog`
- **Production**: Can integrate with free tiers of Sentry, LogRocket
- **Metrics**: Prometheus (self-hosted, free)

## Timeline Alignment

### Week 1: Project Setup & Data Engineering ✅
- [x] Base project structure
- [x] API integrations setup
- [x] Database schema design
- [x] Development environment

### Week 2-3: GNN/Multi-modal Development
- [ ] User profile modeling
- [ ] Preference learning algorithms
- [ ] Graph neural network implementation
- [ ] Multi-modal recommendation engine

### Week 4: LLM Orchestration
- [ ] Intent parsing and reasoning
- [ ] Multi-agent coordination
- [ ] Tool-augmented prompting
- [ ] Hallucination mitigation

### Week 5-6: Big Data Integration
- [ ] Kafka stream processing
- [ ] Real-time data pipelines
- [ ] Scaling optimizations
- [ ] Performance testing

### Week 7: Testing & Optimization
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Bug fixes and refinements

### Week 8: Final Report
- [ ] Documentation completion
- [ ] Deployment guide
- [ ] Performance metrics
- [ ] Project submission

## Contributing

1. Read this README thoroughly
2. Set up your development environment
3. Pick an issue from GitHub Issues
4. Create feature branch
5. Implement with tests
6. Submit pull request
7. Participate in code review

## Support

- **Documentation**: Check `/docs` folder
- **Issues**: GitHub Issues
- **Questions**: Team Slack/Discord channel
- **Code Review**: GitHub Pull Requests

## Next Steps

1. **For New Team Members**:
   - Complete environment setup
   - Run the test suite
   - Review the codebase structure
   - Pick a starter issue

2. **For Project Leads**:
   - Assign GitHub Issues to team members
   - Set up CI/CD pipeline
   - Configure monitoring and logging
   - Schedule regular team meetings

---

Happy coding! 🚀✈️🏨

For questions, reach out to the team or create an issue in the repository.